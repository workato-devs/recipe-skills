# Lookup Tables (Legacy)

Workato has an older, separate "Lookup Tables" feature exposing a `lookup_table` provider with `get_entry`, `update_entry`, and `add_entry` actions. **This is a distinct, legacy feature from the modern Data Tables connector** (`workato_db_table`, covered by the `datatable-recipes` skill) — the two are easy to confuse and are not interchangeable.

**This is a thin pattern doc** — verified from a single real recipe. Treat it as a starting point, not an exhaustive reference.

---

## Lookup Tables vs. Data Tables — Do Not Confuse

| | Lookup Tables (`lookup_table`, this doc) | Data Tables (`workato_db_table`, see `datatable-recipes` skill) |
|---|---|---|
| Provider | `lookup_table` | `workato_db_table` |
| Shape | Simple key-value-style rows with generic `col1`/`col2`/... columns (renamed per-table in the UI, but referenced by their internal `colN` name in recipe JSON) | Full typed schema with named columns, UUID row IDs, batch/search operations |
| Verified actions | `get_entry`, `update_entry`, `add_entry` | See `datatable-recipes/lint-rules.json` |

If a recipe or a user request mentions "Data Table" or `workato_db_table`, use the `datatable-recipes` skill instead — this doc is only for the legacy `lookup_table` provider.

---

## Config Entry

```json
{
  "keyword": "application",
  "provider": "lookup_table",
  "skip_validation": false,
  "account_id": null
}
```

Platform provider — no external connection, `account_id: null`.

---

## `get_entry`

```json
{
  "number": 6,
  "provider": "lookup_table",
  "name": "get_entry",
  "as": "lookup_current_version",
  "keyword": "action",
  "dynamicPickListSelection": {
    "lookup_table_id": "Untitled lookup table"
  },
  "input": {
    "lookup_table_id": "33842",
    "parameters": {
      "col1": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"foreach\",\"line\":\"loop_versions\",\"path\":[\"productGroupVersion\"]}')}"
    }
  },
  "uuid": "lookup-current-version-001"
}
```

**Key fields:**
- `dynamicPickListSelection.lookup_table_id` (human-readable table name) + `input.lookup_table_id` (numeric ID) — same dual-field dynamic-picklist pattern as [scheduler.md](../triggers/scheduler.md)'s `time_unit`.
- `parameters` — one or more `colN` fields to search by (the verified example searches by `col1` alone; the table's EIS declares all columns as optional so you can search by any subset).

### Output

```json
"path": ["id"]                 // the entry's row ID, an integer
"path": ["entry", "col1"]
"path": ["entry", "col2"]
```

---

## `update_entry`

```json
{
  "number": 10,
  "provider": "lookup_table",
  "name": "update_entry",
  "as": "update_current_version",
  "keyword": "action",
  "dynamicPickListSelection": { "lookup_table_id": "Untitled lookup table" },
  "toggleCfg": { "ignore_not_found": true },
  "input": {
    "ignore_not_found": "false",
    "id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"lookup_table\",\"line\":\"lookup_current_version\",\"path\":[\"id\"]}')}",
    "lookup_table_id": "33842",
    "parameters": {
      "col1": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"foreach\",\"line\":\"loop_versions\",\"path\":[\"productGroupVersion\"]}')}",
      "col2": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"foreach\",\"line\":\"loop_versions\",\"path\":[\"releaseKey\"]}')}"
    }
  },
  "uuid": "update-current-version-001"
}
```

**Key fields:**
- `id` — the entry's row ID, typically chained from a preceding `get_entry` call (find-then-update pattern).
- `ignore_not_found` — `"false"` in the verified example (an update targeting a missing `id` raises an error rather than silently no-op-ing).
- `parameters` — only the columns being changed need to be included (the verified example updates `col1`/`col2` without touching `col3`).

---

## `add_entry`

Not directly observed in the verified recipe's action calls (only referenced by name in the connector's lint-rules), but follows the same `lookup_table_id` + `parameters` shape as `get_entry`/`update_entry` — provide values for the columns you want the new row to have.

---

## Validation Checklist

- [ ] Config includes `lookup_table` with `account_id: null`
- [ ] `dynamicPickListSelection.lookup_table_id` (human-readable) and `input.lookup_table_id` (numeric) refer to the same table
- [ ] Columns are referenced by their internal `colN` name (as shown in the table's own EIS), not by their UI display label
- [ ] `update_entry`'s `id` is obtained from a preceding `get_entry` (or another known source), not guessed
- [ ] Confirm this is genuinely the legacy Lookup Tables feature, not Data Tables (`workato_db_table`) — see the comparison table above

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

---

## Related Documentation

- `datatable-recipes` skill — the modern Data Tables connector (`workato_db_table`); use that skill instead if the target is Data Tables, not this legacy feature
