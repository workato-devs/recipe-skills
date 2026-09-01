# Bound HTML Apps (recipe-referenced MCP tools)

A second, independently-verified path to an MCP App, distinct from the [`workato_skill`/`agentic_skill` path](../SKILL.md#the-workato_skill-trigger) documented above. Here the MCP tool **is** a normal `workato_api_platform` API endpoint recipe, referenced directly by the server manifest — no `wk agentic skills create` wrapping step. Verified at runtime against a live Workato MCP server (Get_Labs_Dashboard build, June 2026), unless a line below is marked otherwise.

> **Open question, not yet reconciled:** this repo's other MCP App guidance ([patterns/mcp-apps.md](mcp-apps.md)) was verified using an `agentic_skill`-referenced tool and doesn't mention a `tools_type` field at all. This doc's build required `tools_type: "project_assets"` with a direct `type: "recipe"` reference (see below), and found that a sibling mode, `api_collection`, does **not** support bound apps. Whether an `agentic_skill`-referenced server is itself `project_assets`, `api_collection`, or a third unlisted mode is unconfirmed — treat the two paths as separately verified, not as interchangeable, until someone checks a real `.mcp_server.json` from each.

---

## 1. `tools_type` is the fork in the road

A Workato MCP server JSON (`*.mcp_server.json`) declares a `tools_type`:

- **`api_collection`** — `references[]` point at an `api_group`; tools are exposed via `api_endpoints`. **Bound apps do not work in this mode** (confirmed with the platform team).
- **`project_assets`** — `references[]` point at recipes directly (`type: "recipe"`). Tools are the recipes themselves. **This is the mode that supports `apps[]` bound views.**

A `project_assets` server does not need the intermediary `*.api_endpoint.json` / `api_group` artifacts — bind the recipe directly. The recipe still uses a normal `workato_api_platform` `receive_request` (`api_trigger`); you just don't emit the endpoint asset.

```json
{
  "auth_type": "token",
  "name": "Labs Dashboard",
  "tools_type": "project_assets",
  "references": {
    "ref_0": { "type": "recipe",
               "id": { "folder": "", "name": "Get Labs Dashboard", "zip_name": "get_labs_dashboard.recipe.json" } }
  },
  "tools": [
    { "tool": "ref_0", "vua_required": false,
      "description": "<dense, LLM-facing tool description>" }
  ],
  "apps": [ /* see §3 */ ]
}
```

The MCP tool name is derived from the recipe name (`Get Labs Dashboard` → `Get_Labs_Dashboard`).

---

## 2. File layout

For one `project_assets` server with one bound tool + view, all as synced project assets (`wk push` deploys them):

```
<server>.mcp_server.json          # project_assets, references the recipe, registers apps[]
<recipe>.recipe.json              # the tool recipe (api_trigger; no api_endpoint needed)
<server>_<app>.bin                # the bound view (UTF-8 HTML -- see §3 for the naming rule)
<table>.workato_db_table.json     # optional: any data tables the recipe reads/writes
```

A hand-authored `*.workato_db_table.json` is created by `wk push` and preserves the column UUIDs you supply — every column needs an `id`.

---

## 3. `apps[]` registration

```json
"apps": [{
  "content_digest": "<sha256 of the .bin file>",
  "meta": { "csp": {
      "resourceDomains": ["https://cdn.jsdelivr.net"],
      "connectDomains": [], "frameDomains": [], "baseUriDomains": [] } },
  "name": "Labs Dashboard",
  "tool": "ref_0"
}]
```

- `content_digest` — the raw SHA-256 of the `.bin` file (`shasum -a 256 <file>.bin`). Recompute and update whenever the HTML changes.
- **`.bin` filename convention (enforced on push):** must be `<mcp_server_file_basename>_<app_name_lowercased_underscored>.bin`. E.g. server `labs_dashboard.mcp_server.json` + app `"Labs Dashboard"` → `labs_dashboard_labs_dashboard.bin`. A mismatch fails with `import failed … key not found: "<expected>.bin"`.
- `meta.csp.resourceDomains` — every external origin the HTML loads (script/style/img). Loading the ext-apps SDK and Chart.js both from jsDelivr is covered by `["https://cdn.jsdelivr.net"]` alone.

> **Note on filename flexibility:** [patterns/mcp-apps.md](mcp-apps.md) states "the HTML file can have any filename" for the `agentic_skill` path. That claim does not hold here — the `.bin` naming rule above is enforced by `wk push` for a `project_assets` server. Unconfirmed whether the difference is the `tools_type`, the deployment mechanism (synced project file vs. manifest-embedded content), or both.

---

## 4. The view HTML

The `.bin` file is plain UTF-8 HTML using the official MCP Apps SDK ([`@modelcontextprotocol/ext-apps`](https://www.npmjs.com/package/@modelcontextprotocol/ext-apps), same package as [patterns/mcp-apps.md](mcp-apps.md)). The host calls the bound tool and delivers the result to `app.ontoolresult` — no tool name is hard-coded; binding is server-side via `apps[].tool`.

```js
import {App} from 'https://cdn.jsdelivr.net/npm/@modelcontextprotocol/ext-apps@1.3.1/dist/src/app-with-deps.js';

// The tool-result envelope shape varies by host. Recurse to find the object matching your contract.
function extractResponse(payload) {
  const candidates = [];
  const push = x => { if (x && typeof x === 'object') candidates.push(x); };
  if (payload) {
    push(payload); push(payload.structuredContent); push(payload.result); push(payload.toolResult);
    const content = payload.content || (payload.result && payload.result.content);
    if (Array.isArray(content)) for (const c of content)
      if (c && c.type === 'text' && typeof c.text === 'string') { try { push(JSON.parse(c.text)); } catch (e) {} }
  }
  const looksLike = o => o && typeof o === 'object' && (/* your contract */ o.schema_version || (Array.isArray(o.repos) && o.totals));
  const find = (o, d) => { if (d > 6 || !o || typeof o !== 'object') return null;
    if (looksLike(o)) return o; for (const k of Object.keys(o)) { const r = find(o[k], d + 1); if (r) return r; } return null; };
  for (const c of candidates) { const r = find(c, 0); if (r) return r; }
  return null;
}

const app = new App({ name: 'Labs Dashboard', version: '1.0.0' });
app.ontoolresult = result => render(extractResponse(result));
await app.connect();
```

**Envelope gotcha, specific to this (recipe-as-tool) path:** an API-platform MCP tool returns the recipe body as `content[0].text` — a JSON *string*, not a top-level `structuredContent` field — and the body is wrapped `{ "http_status_code": "...", "response": { ... } }`. `extractResponse` must `JSON.parse(content[0].text)` and recurse into `.response`. Match on a stable contract marker (`schema_version`, or `repos[]` + `totals` here) rather than assuming a fixed nesting depth — see the general [unwrapping guidance](mcp-apps.md#unwrapping-tool-results) for why a fixed-depth chain of `JSON.parse` calls is the wrong pattern regardless of which wiring path produced the tool.

Design the view to degrade gracefully: render whatever fields are present — optional sections (a history series, week-over-week deltas) may be absent in early versions of the recipe.

---

## 5. Returning native JSON from `return_response`

A UI-support tool usually needs native nested JSON (`repos: [ {...} ]`, `totals: {clones: 537}`) — not stringified sub-fields, not string-typed numbers. How you bind the value in `return_response` decides this; see [datapill-syntax.md's interpolation-stringifies gotcha](../../workato-recipes/fundamentals/datapill-syntax.md) for the general rule. Applied here:

```json
// return_response input.response -- formula mode for structured fields:
"totals":           "=_dp('{\"pill_type\":\"output\",\"provider\":\"py_eval\",\"line\":\"build_payload\",\"path\":[\"output\",\"totals\"]}')",
"repos":            "=_dp('{… ,\"path\":[\"output\",\"repos\"]}')",
"referrers_rollup": "=_dp('{… ,\"path\":[\"output\",\"referrers_rollup\"]}')",
"schema_version":   "#{_dp('{… ,\"path\":[\"output\",\"schema_version\"]}')}"   // plain string: interpolation is fine
```

**Rule:** bind structured/typed fields (objects, arrays, numbers) with `=_dp(...)`; plain strings can stay `#{_dp(...)}`. Build the whole payload in one `py_eval` step (see [python-snippets.md](../../workato-recipes/patterns/python-snippets.md)) whose `code_output_schema_json` fully models the nested shape, then bind each top-level `return_response` field directly to that `py_eval` output — do not route it through `____source`/`current_item` remapping, which can't express nested sub-arrays and drops them.

The base skill already requires `return_response`'s `extended_input_schema` to equal its `extended_output_schema` (see [triggers/api-endpoint.md](../../workato-recipes/triggers/api-endpoint.md)); the addition here is that for this pattern **both must also fully model the nested schema** of every structured field, not just its top-level type — otherwise the typed/nested values won't survive even with formula-mode binding. `wk lint` does not catch this EIS/EOS nested-schema desync.

Datapill inner JSON must be compact (`{"pill_type":"output",...}`, no spaces) and singly-escaped — build it with `json.dumps(..., separators=(',',':'))` in Python and let the file serializer escape it once; double-escaping produces `DP_VALID_JSON` lint errors.

---

## 6. Runtime gotchas (all hit on a real build)

- **`.to_json` of an absent/optional datapill yields the string `"null"`.** `json.loads("null")` → `None`, and `None or '[]'` does **not** save you — the string `"null"` is truthy before parsing. Guard `py_eval` inputs:
  ```python
  raw = input.get('x_json')
  try:
      data = json.loads(raw) if raw else []
  except Exception:
      data = []
  if not isinstance(data, list):
      data = []
  ```
- **`api_trigger` optional inputs are `nil` at runtime** — schema "defaults" are not applied to the value itself. A path formula like `'/repos/' + _dp(owner)` throws `argument must not be nil` on a zero-arg call. Resolve and default such values in an early `py_eval` step (output a defaulted `owner`) and reference *that* output — not the raw trigger field — in downstream formulas.
- **`wk lint` false-positives inside `foreach`**: datapills referencing the `foreach` alias (e.g. `current_repo`) or in-loop sibling steps raise Tier 3 `DP_LINE_RESOLVES` / `DP_STEP_REACHABLE` warnings — the linter can't statically resolve `foreach`-scoped aliases. `errors: 0` plus a successful runtime call confirms these are noise, not real problems.
- **Data-table number columns**: prefer formula-mode `=_dp(...)` when writing numeric values via `upsert_record`/`add_record` so they aren't coerced to strings — same root cause as §5.

---

## 7. Deploy & verify with the `wk` CLI

```bash
wk push --profile <p> --folder <folder> --skip-hooks      # deploys recipe + .bin + server (atomic per folder)
wk recipes start <recipe_id> --profile <p>                # api-triggered recipes must be running to serve
wk mcp servers list --profile <p> --json                  # find the server id + mcp_url
wk mcp servers get  <server_id> --profile <p> --json      # mcp_url (includes ?wkt_token=…)
wk mcp tools "<mcp_url>" --profile <p>                     # confirm the tool is exposed
```

Verify the binding the way a client sees it (JSON-RPC over the `mcp_url`), not just via the admin-API summary commands above:

```bash
# tool advertises the app:   _meta.ui.resourceUri = "ui://<slug>"
curl -s "<mcp_url>" -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# the view is a resource:     mimeType "text/html;profile=mcp-app"
curl -s "<mcp_url>" -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"resources/list"}'

# served HTML == local .bin (sha256 must match the registered content_digest)
curl -s "<mcp_url>" -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":3,"method":"resources/read","params":{"uri":"ui://<slug>"}}'

# exercise the tool and inspect native typing
curl -s "<mcp_url>" -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"<Tool_Name>","arguments":{}}}'
```

The actual visual render only happens in an MCP-Apps-capable client (e.g. Claude Desktop/web) — same caveat as [patterns/mcp-apps.md](mcp-apps.md#connecting-an-mcp-client-eg-claude-desktop). The CLI/JSON-RPC checks above confirm everything except the pixels.

**Shared-folder caveat:** `wk push` is folder-scoped and atomic. If other unrelated, half-staged assets in the same folder error on import, temporarily move them aside, push, then restore.

---

## Validation

See [validation-checklist.md](../validation-checklist.md)'s "Bound HTML Apps" section for the checklist form of everything above.
