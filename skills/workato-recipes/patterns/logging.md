# Logging

Workato's built-in "Logger" utility exposes a `logger` provider with a `log_message` action — writes a message to the recipe's job report, optionally also to Workato's account-level log service.

**This is a thin pattern doc** — verified from a single real recipe. Treat it as a starting point, not an exhaustive reference.

---

## When to Use

Use `log_message` for lightweight, human-readable diagnostic notes attached to a specific job run — e.g. recording which branch of an `if`/`else` was taken, or noting an intermediate value for later troubleshooting. It does not stop the recipe or raise an error (see [Stop Action](../control-flow/stop.md) for that).

---

## Config Entry

```json
{
  "keyword": "application",
  "provider": "logger",
  "skip_validation": false,
  "account_id": null
}
```

Platform provider — no external connection, `account_id: null`.

---

## Action Structure

```json
{
  "number": 6,
  "provider": "logger",
  "name": "log_message",
  "as": "log_sync_status",
  "keyword": "action",
  "input": {
    "user_logs_enabled": "false",
    "message": "Renewal project sync completed for customer batch"
  },
  "extended_input_schema": [
    {
      "control_type": "switch",
      "default": false,
      "disable_formula": true,
      "extends_schema": true,
      "label": "Send to Workato log service",
      "name": "user_logs_enabled",
      "optional": true,
      "type": "string",
      "hint": "Send a copy of the message to Workato logs."
    }
  ],
  "uuid": "log-sync-status-001"
}
```

**Key fields:**
- `message` — the log text. Can be a literal string or a formula/datapill-built string (e.g. interpolating a variable's current value for context).
- `user_logs_enabled` — `"false"` in the verified example. When `"true"`, the message is also sent to Workato's account-level log service (in addition to always appearing in the recipe's own job report) — per the field's own hint text. Note `disable_formula: true` on its EIS entry: this toggle cannot be set via formula/datapill, only a literal `"true"`/`"false"`.

---

## Validation Checklist

- [ ] Config includes `logger` with `account_id: null`
- [ ] `message` is populated with useful, specific context (not a generic placeholder) — it's the only content this action produces
- [ ] `user_logs_enabled` is a literal `"true"`/`"false"` string, not a formula/datapill (the field has `disable_formula: true`)

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

---

## Related Documentation

- [Stop Action](../control-flow/stop.md) — for halting a recipe with an error, rather than just logging a note
