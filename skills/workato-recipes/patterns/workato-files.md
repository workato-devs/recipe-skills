# Workato Files

Workato's built-in file storage exposes a `workato_files` provider with two actions verified in production: `store_file` (write content to Workato's managed file storage) and `create_shareable_link` (generate a time-limited download URL for a stored file).

---

## When to Use

Use `workato_files` when a recipe needs to persist generated content (a report, an export, a rendered document) somewhere Workato manages, then hand back a downloadable link — e.g. an API endpoint recipe that generates a report and returns a link to it in the response, rather than returning the raw content inline.

---

## Config Entry

```json
{
  "keyword": "application",
  "provider": "workato_files",
  "skip_validation": false,
  "account_id": null
}
```

Platform provider — no external connection, `account_id: null`.

---

## `store_file`

```json
{
  "number": 16,
  "provider": "workato_files",
  "name": "store_file",
  "as": "store_report",
  "keyword": "action",
  "dynamicPickListSelection": {
    "file_path": { "ids": ["/"], "titles": ["Root directory"] }
  },
  "toggleCfg": {
    "is_csv_file": true,
    "overwrite": true,
    "file_path": true
  },
  "input": {
    "is_csv_file": "false",
    "schema_type": "auto",
    "csv_has_header": "true",
    "csv_delimiter": "comma",
    "csv_quote": "double",
    "encoding": "UTF-8",
    "overwrite": "true",
    "file_name": "=\"Report-\"+ now.strftime(\"%m%d%Y_%H%M%S\") + \".xlsx\"",
    "file_path": "/",
    "content": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"api_call\",\"path\":[\"response\"]}')}"
  },
  "uuid": "store-report-001"
}
```

**Key fields:**
- `file_name` — a formula computing a unique/timestamped name is the verified real-world pattern (`now.strftime(...)` — see the base skill's [formula date/time methods](../SKILL.md#formula-syntax)), not a hardcoded literal.
- `file_path` — `"/"` is the verified root-directory value, paired with `dynamicPickListSelection.file_path` carrying the human-readable folder picker selection (`ids`/`titles`) — same dual-field dynamic-picklist pattern as [scheduler.md](../triggers/scheduler.md)'s `time_unit`.
- `content` — the raw content to store, typically piped directly from an upstream action's response (here, a `rest`/`make_request_v2` response).
- `is_csv_file`/`schema_type`/`csv_has_header`/`csv_delimiter`/`csv_quote`/`encoding` — CSV-specific parsing options, present even when storing a non-CSV binary file (`is_csv_file: "false"` in the verified example, storing an `.xlsx`) — these fields appear in the input regardless of file type, not just for CSVs.
- `overwrite` — `"true"` replaces an existing file at the same path/name rather than erroring.

### `store_file` Output

Produces (at minimum) a `path` field — the stored file's path, used to build a shareable link (see below).

---

## `create_shareable_link`

```json
{
  "number": 17,
  "provider": "workato_files",
  "name": "create_shareable_link",
  "as": "share_report",
  "keyword": "action",
  "toggleCfg": { "file_path": true },
  "input": {
    "scope": "download",
    "file_path": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_files\",\"line\":\"store_report\",\"path\":[\"path\"]}')}",
    "expires_in": "3600"
  },
  "visible_config_fields": ["file_path", "file_name", "file_dir", "expires_in"],
  "uuid": "share-report-001"
}
```

**Key fields:**
- `file_path` — chained directly from the preceding `store_file` step's `["path"]` output, not re-typed.
- `scope` — `"download"` is the verified value (generates a link that downloads the file).
- `expires_in` — seconds until the link stops working; `"3600"` (1 hour) is the verified value.

### `create_shareable_link` Output

Produces (at minimum) the shareable URL — pull a fresh action from the Workato UI to confirm the exact output field name before mapping it, since no downstream datapill referencing it was present in the verified recipes.

---

## Common Pattern: Generate and Share a Report

```
[build report content] → store_file (timestamped file_name, root path) → create_shareable_link (scope: download, expires_in) → return_response (with the link)
```

Both verified recipes ("Template Excel Export" and its v2) use exactly this two-step chain to turn a generated export into a downloadable link returned from an API endpoint recipe.

---

## Validation Checklist

- [ ] Config includes `workato_files` with `account_id: null`
- [ ] `store_file`'s `file_name` avoids collisions (e.g. via a timestamp formula) when `overwrite` is not intentionally `"true"`
- [ ] `store_file`'s `dynamicPickListSelection.file_path` (human-readable folder selection) and `input.file_path` (literal path) refer to the same folder
- [ ] `create_shareable_link`'s `file_path` is chained from a preceding `store_file` step's `["path"]` output, not hand-typed
- [ ] `create_shareable_link`'s `expires_in` is set deliberately (seconds), not left at a default that may be too short/long for the recipe's use case

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

---

## Related Documentation

- [Adhoc HTTP Actions](adhoc-http-actions.md) — often the source of the `content` being stored (an upstream `rest`/`make_request_v2` response)
