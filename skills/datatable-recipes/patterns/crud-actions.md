# CRUD Actions Pattern

> **Status:** Action names and input shapes are unverified guesses based on Workato docs and naming conventions. Build golden recipes to validate.

## Create Record

Creates a single row in a data table.

```json
{
  "number": 1,
  "provider": "workato_db_table",
  "name": "create_record",
  "as": "create_row",
  "keyword": "action",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": {
      "zip_name": "tablename.workato_db_table.json",
      "name": "TableDisplayName",
      "folder": ""
    },
    "<email-column-uuid>": "#{_dp('{...email_datapill...}')}",
    "<status-column-uuid>": "pending"
  },
  "uuid": "create-row-001"
}
```

- Required table columns must be populated
- Record ID is auto-assigned (do not set it)
- Output includes the full record with generated Record ID

## Update Record

Updates specific fields on an existing row. Partial — only provided fields change.

```json
{
  "number": 2,
  "provider": "workato_db_table",
  "name": "update_record",
  "as": "update_row",
  "keyword": "action",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": { ... },
    "11fbe9a6_a16d_4d7e_86ea_afe42ec03005": "#{_dp('{...record_id_from_trigger...}')}",
    "<status-column-uuid>": "approved"
  },
  "uuid": "update-row-002"
}
```

- Record ID (`11fbe9a6_a16d_4d7e_86ea_afe42ec03005`) identifies the target row
- Empty fields are NOT cleared — use `remove_values_from_record` to clear
- Output includes the full updated record

## Delete Record

Removes a row by Record ID.

```json
{
  "number": 3,
  "provider": "workato_db_table",
  "name": "delete_record",
  "as": "delete_row",
  "keyword": "action",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": { ... },
    "11fbe9a6_a16d_4d7e_86ea_afe42ec03005": "#{_dp('{...record_id...}')}"
  },
  "uuid": "delete-row-003"
}
```

- Output: `success` boolean
- Irreversible — no undo

## Upsert Record

Creates if no match, updates if match found. Matches on a single primary key column.

```json
{
  "number": 4,
  "provider": "workato_db_table",
  "name": "upsert_record",
  "as": "upsert_row",
  "keyword": "action",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": { ... },
    "<primary-key-column-uuid>": "match_value",
    "<other-column-uuid>": "new_value"
  },
  "uuid": "upsert-row-004"
}
```

- Only single-column primary key matching (no multi-column)
- Output: `record_created` boolean + full `record` object
- How the primary key column is specified in recipe JSON is TBD

## Remove Values From Record

Clears specific column values without deleting the row.

```json
{
  "number": 5,
  "provider": "workato_db_table",
  "name": "remove_values_from_record",
  "as": "clear_fields",
  "keyword": "action",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": { ... },
    "11fbe9a6_a16d_4d7e_86ea_afe42ec03005": "#{_dp('{...record_id...}')}"
  },
  "uuid": "clear-fields-005"
}
```

- Required columns cannot be cleared
- Use this instead of update when the intent is to blank out a field

## Batch Actions

**Names:** `create_records`, `update_records`, `delete_records`

Operate on multiple records. Input likely takes an array of records. Exact shape TBD — needs golden recipe validation.

## Truncate Table

**Name:** `truncate_table`

Removes ALL records from a table. No filtering. Destructive and irreversible.

```json
{
  "number": 6,
  "provider": "workato_db_table",
  "name": "truncate_table",
  "as": "clear_table",
  "keyword": "action",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": { ... }
  },
  "uuid": "clear-table-006"
}
```

## Common Pattern: Trigger + Update Same Row

```json
{
  "code": {
    "provider": "workato_db_table",
    "name": "updated_records_realtime",
    "as": "new_row",
    "keyword": "trigger",
    "input": { "table_id": { ... }, "since": "..." },
    "block": [
      {
        "provider": "workato_db_table",
        "name": "update_record",
        "as": "mark_processed",
        "keyword": "action",
        "input": {
          "table_id": { ... },
          "11fbe9a6_a16d_4d7e_86ea_afe42ec03005": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"new_row\",\"path\":[\"record\",\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}",
          "<status-uuid>": "processed"
        }
      }
    ]
  }
}
```
