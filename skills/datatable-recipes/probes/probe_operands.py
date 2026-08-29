#!/usr/bin/env python3
"""Measure the Workato data-table filter operand vocabulary, and reproduce the
silent-drop defect on non-string columns.

Workspace-agnostic: every workspace-specific value is an argument. It does need a
live Dev API token, because the claims are about platform behaviour at runtime —
activation does not validate filter operands at all, so nothing offline can settle
them.

What it does, per candidate operand: builds a clock-triggered recipe carrying one
get_records step, activates it, waits for a job, reads the step output, then stops
and deletes the recipe. Nothing is left behind.

Verdicts:
  MEMBER        job ran; the operand is in the backend enum
  NOT-A-MEMBER  job failed with Expected input type "ApiQueryOperation"
  WRONG-TYPE    job failed some other way (valid name, wrong column type)

Usage:
  export WK_TOKEN=...            # Dev API token for the workspace
  python3 probe_operands.py \
      --host https://app.trial.workato.com \
      --folder 35553 \
      --table 6025 \
      --column 58dc1aae-f7b8-42be-a6b2-8c2d905c3d4b \
      --value FOUND1 \
      --total-rows 2

`--total-rows` is the unfiltered row count of the table. It is what separates a
filter that worked from one that was silently ignored: an ignored filter returns
every row and the job is still green.
"""
import argparse, json, os, time, urllib.request, urllib.error

DEFAULT_CANDIDATES = [
    "eq", "ne", "lt", "gt", "lte", "gte", "le", "ge",
    "starts_with", "ends_with", "contains", "not_contains",
    "isnull", "isnotnull", "is_null", "is_not_null",
    "istrue", "isfalse", "is_true", "is_false",
    "in", "not_in", "nin", "between", "equals", "is_not_equal_to",
]
NOT_A_MEMBER = 'Expected input type "ApiQueryOperation"'


class Client:
    def __init__(self, host, token, folder):
        self.host, self.token, self.folder = host.rstrip('/'), token, str(folder)

    def req(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.host + path, data=data, method=method,
                                   headers={"Authorization": "Bearer " + self.token,
                                            "Content-Type": "application/json"})
        try:
            return 200, urllib.request.urlopen(r).read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()

    def code(self, table, filters):
        return {
            "number": 0, "keyword": "trigger", "provider": "clock",
            "name": "scheduled_event", "as": "sched", "uuid": "trg-probe-0001",
            "input": {"time_unit": "minutes", "interval": "1"},
            "extended_input_schema": [], "extended_output_schema": [],
            "block": [{
                "number": 1, "keyword": "action", "provider": "workato_db_table",
                "name": "get_records", "as": "probe_rows", "uuid": "act-probe-0001",
                "extended_input_schema": [], "extended_output_schema": [],
                "input": {"table_id": str(table), "limit": "50",
                          "output_format": "field_name_to_value",
                          "filters": filters},
            }],
        }

    def start(self, name, table, filters):
        cfg = json.dumps([
            {"keyword": "application", "provider": "clock", "name": "clock", "account_id": None},
            {"keyword": "application", "provider": "workato_db_table",
             "name": "workato_db_table", "account_id": None}])
        _, b = self.req("POST", "/api/recipes", {"recipe": {
            "name": name, "code": json.dumps(self.code(table, filters)),
            "folder_id": self.folder, "config": cfg}})
        try:
            rid = json.loads(b).get('id')
        except Exception:
            return None, b[:200]
        if not rid:
            return None, b[:200]
        _, a = self.req("PUT", f"/api/recipes/{rid}/start")
        return rid, a

    def job(self, rid):
        _, b = self.req("GET", f"/api/recipes/{rid}/jobs?per_page=1")
        try:
            items = json.loads(b).get('items') or []
        except Exception:
            return None
        if not items:
            return None
        h = items[0].get('job_handle') or items[0].get('id')
        _, jb = self.req("GET", f"/api/recipes/{rid}/jobs/{h}")
        try:
            j = json.loads(jb)
            return j.get('data', j)
        except Exception:
            return None

    def teardown(self, rid):
        if rid:
            self.req("PUT", f"/api/recipes/{rid}/stop")
            self.req("DELETE", f"/api/recipes/{rid}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", required=True)
    p.add_argument("--folder", required=True)
    p.add_argument("--table", required=True)
    p.add_argument("--column", required=True, help="column UUID, hyphenated")
    p.add_argument("--value", required=True, help="a value matching exactly one row")
    p.add_argument("--total-rows", type=int, required=True)
    p.add_argument("--op-key", default="op_default")
    p.add_argument("--operands", default=",".join(DEFAULT_CANDIDATES))
    p.add_argument("--wait", type=int, default=120)
    a = p.parse_args()

    token = os.environ.get("WK_TOKEN")
    if not token:
        raise SystemExit("set WK_TOKEN")
    c = Client(a.host, token, a.folder)
    ops = [o.strip() for o in a.operands.split(",") if o.strip()]

    made = []
    try:
        for o in ops:
            f = [{"field_id": a.column, a.op_key: o, "value_default": a.value}]
            rid, _ = c.start(f"zz-opprobe-{o}"[:60], a.table, f)
            made.append((o, rid))
        deadline = time.time() + a.wait
        seen = {}
        while len(seen) < len([1 for _, r in made if r]) and time.time() < deadline:
            time.sleep(10)
            for o, rid in made:
                if not rid or o in seen:
                    continue
                j = c.job(rid)
                if not j:
                    continue
                line = next((l for l in j.get('lines', [])
                             if l.get('adapter_operation') == 'get_records'), None)
                err = (line or {}).get('error') or j.get('error')
                if err:
                    e = str(err)
                    seen[o] = ("NOT-A-MEMBER" if NOT_A_MEMBER in e else "WRONG-TYPE", e[:120])
                elif line:
                    n = len(((line.get('output') or {}).get('records')) or [])
                    tag = "IGNORED(all rows)" if n == a.total_rows else f"applied({n} rows)"
                    seen[o] = ("MEMBER", tag)
        print(f"{'operand':<18} {'verdict':<14} detail")
        print("-" * 68)
        for o, _ in made:
            v, d = seen.get(o, ("NO-JOB", f">{a.wait}s"))
            print(f"{o:<18} {v:<14} {d}")
    finally:
        for _, rid in made:
            c.teardown(rid)
        print("\nall probe recipes deleted")


if __name__ == "__main__":
    main()
