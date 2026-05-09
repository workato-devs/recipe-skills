# Data Table Trigger

> **Full connector documentation has moved to [datatable-recipes](../../datatable-recipes/SKILL.md).** This file covers only the trigger basics for quick reference from the base skill. For actions (create, update, delete, search, upsert), UUID column mapping, and validation, see the connector skill.

Use the data table trigger when your recipe should run in response to row creation or updates in a Workato data table.

## Provider Details

| Field | Value |
|-------|-------|
| Provider | `workato_db_table` |
| Trigger (new/updated, real-time) | `updated_records_realtime` (verified) |
| Trigger (new records, batch) | `new_records_polling` (verified) |
| Trigger (new record, real-time) | `new_record_realtime` (needs verification) |
| Trigger (new/updated, batch) | `updated_records_polling` (needs verification) |
| Config | `account_id: null` (always — internal connector) |

## Quick Reference

```json
{
  "number": 0,
  "provider": "workato_db_table",
  "name": "updated_records_realtime",
  "as": "record_changed",
  "keyword": "trigger",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": {
      "zip_name": "tablename.workato_db_table.json",
      "name": "TableDisplayName",
      "folder": ""
    },
    "since": "2026-01-01T00:00:00.000-07:00"
  },
  "extended_output_schema": [
    {
      "label": "Record", "name": "record", "type": "object",
      "properties": [
        { "control_type": "text", "label": "Record ID", "type": "string", "name": "11fbe9a6_a16d_4d7e_86ea_afe42ec03005" },
        { "control_type": "text", "label": "Column 1", "type": "string", "name": "<column-uuid-with-underscores>" }
      ]
    },
    {
      "label": "Old record", "name": "old_record", "type": "object",
      "properties": [
        { "control_type": "text", "label": "Record ID", "type": "string", "name": "11fbe9a6_a16d_4d7e_86ea_afe42ec03005" },
        { "control_type": "text", "label": "Column 1", "type": "string", "name": "<column-uuid-with-underscores>" }
      ]
    }
  ],
  "uuid": "trigger-001"
}
```

### Key Rules

- **`dynamicPickListSelection`** is required — `{"table_id": "TableDisplayName"}`
- **`table_id`** is a reference object for import, numeric string after server export
- **Column names are UUIDs** with hyphens replaced by underscores
- **Record ID** uses universal meta UUID `11fbe9a6_a16d_4d7e_86ea_afe42ec03005`
- **`old_record`** EOS is present on `updated_records_realtime` (contains pre-update values)
- **`filter`** block at trigger level can filter to new-only by checking `old_record.Record ID` is blank

## Full Documentation

See [datatable-recipes/SKILL.md](../../datatable-recipes/SKILL.md) for:
- All trigger variants (real-time and batch)
- CRUD actions (create, update, delete, upsert, search)
- UUID column mapping patterns
- Validation checklist
- Golden recipe build plan
