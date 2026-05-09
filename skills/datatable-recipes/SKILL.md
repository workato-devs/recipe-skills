---
name: datatable-recipes
description: Data Tables connector recipes for Workato. Covers triggers, CRUD actions, search, upsert, batch operations, UUID column mapping, and table reference objects for the internal workato_db_table connector.
license: MIT
metadata:
  author: Workato
  version: "0.3.0"
---

# Data Tables Recipes Skill - Agent Instructions

> **DEPENDENCY: Load `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, formulas, and recipe structure.

This skill provides Data Tables-specific knowledge for generating Workato recipes. It extends the **workato-recipes** base skill and focuses on the `workato_db_table` connector — Workato's internal relational data store.

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects:
1. **Read existing data table `.recipe.json` files** to discover column UUIDs and table references
2. **Read the `.workato_db_table.json` file** if present in the project — it defines the table schema

### For GREENFIELD projects:
1. **Ask the user for the table name** and column names/types
2. **Column UUIDs are not portable** — you cannot invent them. Either:
   - Build the recipe in the Workato UI first, export, and use the UUIDs from the export
   - Use placeholder UUIDs (e.g., `COLUMN_UUID_email`, `COLUMN_UUID_status`) and note they must be replaced after the table exists on the server

### ALWAYS:
1. **Use descriptive `as` aliases** — e.g., `new_pending_approval`, `update_row_status`
2. **Include `dynamicPickListSelection`** on the trigger and every action — `{"table_id": "TableDisplayName"}`
3. **Remember: column names are UUIDs** — not human-readable names. See [UUID Column Mapping](#uuid-column-mapping).
4. **Config uses `account_id: null`** — this is an internal connector with no external connection

---

## Table of Contents

1. [Provider Details](#provider-details)
2. [Config Requirements](#config-requirements)
3. [UUID Column Mapping](#uuid-column-mapping)
4. [Table ID Reference Objects](#table-id-reference-objects)
5. [dynamicPickListSelection](#dynamicpicklistselection)
6. [Triggers](#triggers)
7. [Actions](#actions)
8. [Datapill Paths](#datapill-paths)
9. [Patterns](#patterns)
10. [Verification Status](#verification-status)

---

## Provider Details

| Field | Value |
|-------|-------|
| Provider | `workato_db_table` |
| Type | Internal connector (no external auth) |
| Config `account_id` | `null` (always) |

---

## Config Requirements

Every recipe using data tables needs a `workato_db_table` entry in the top-level `config` array:

```json
{
  "keyword": "application",
  "name": "workato_db_table",
  "provider": "workato_db_table",
  "skip_validation": false,
  "account_id": null
}
```

**CRITICAL:** The `"name"` field is required alongside `"provider"`. Without it, activation fails silently with `"missing adapter configuration"`. The `name` value always matches the `provider` string.

`account_id` must be explicitly `null`. Omitting the field entirely can cause `Passed nil into T.must` at import time.

---

## UUID Column Mapping

This is the single most important difference between data tables and every other connector. **Column names in recipe JSON are UUIDs, not human-readable names.**

When a data table has a column called "Email", the recipe JSON refers to it by its column UUID with hyphens replaced by underscores:

| Column display name | UUID (from table schema) | Recipe JSON field name |
|---|---|---|
| Record ID | `11fbe9a6-a16d-4d7e-86ea-afe42ec03005` | `11fbe9a6_a16d_4d7e_86ea_afe42ec03005` |
| Email | `5d420ed4-eafd-44d7-89ae-77ed9c46dba5` | `5d420ed4_eafd_44d7_89ae_77ed9c46dba5` |
| Created at | `a5612739-5401-4ae7-bd07-782c1a6fb2d1` | `a5612739_5401_4ae7_bd07_782c1a6fb2d1` |

### Universal Meta Record ID

Every data table has a built-in Record ID with a fixed universal UUID:

```
11fbe9a6_a16d_4d7e_86ea_afe42ec03005
```

This is the same across ALL data tables. Use it to reference the record ID in datapills, update actions, and delete actions.

### System Columns

Every table also has `Created at` and `Updated at` columns. Their UUIDs are table-specific (not universal). They use:
- `type: "date_time"`
- `control_type: "date_time"`
- `parse_output: "date_time_conversion"`
- `render_input: "date_time_conversion"`

### Where UUIDs Come From

Column UUIDs are assigned by the server when the table is created. You cannot choose them. To discover UUIDs:
1. Export a recipe that uses the table from the Workato UI
2. Read the `.workato_db_table.json` schema file in the project
3. Look at the `extended_output_schema` of a trigger or action that references the table

See: [patterns/uuid-column-mapping.md](patterns/uuid-column-mapping.md)

---

## Table ID Reference Objects

`table_id` has two formats depending on context:

### Import format (what you write in recipe JSON)

Used when building recipes for `wk push`:

```json
"table_id": {
  "zip_name": "goldendatatable.workato_db_table.json",
  "name": "GoldenDataTable",
  "folder": ""
}
```

- `zip_name` — filename of the `.workato_db_table.json` file in the project
- `name` — display name of the table
- `folder` — subfolder path within the project (empty string if at root)

If the table schema file is in a subfolder:
```json
"table_id": {
  "zip_name": "data tables/pending_approvals.workato_db_table.json",
  "name": "pending_approvals",
  "folder": "data tables"
}
```

### Server format (what you see after export)

After export from server, Workato normalizes to a numeric string:
```json
"table_id": "5565"
```

Both formats are valid. Use the reference object format for portability — it resolves by name, not by ID.

---

## dynamicPickListSelection

**Required on triggers and all actions.** Uses the table display name (not numeric ID):

```json
"dynamicPickListSelection": {
  "table_id": "GoldenDataTable"
}
```

This is used by the Workato UI for field discovery. Without it, the UI cannot resolve column schemas.

---

## Triggers

### Naming Convention

Data table triggers use suffix-based naming:
- **`_realtime` suffix** = real-time triggers (fire immediately on change)
- **`_polling` suffix** = batch triggers (process records in groups on a schedule)

| Trigger type | Real-time | Batch |
|---|---|---|
| New records | `new_records_realtime` (verified) | `new_records_polling` (verified) |
| New/updated records | `updated_records_realtime` (verified) | `updated_records_polling` (verified) |

**INVALID trigger names confirmed:** `new_record_realtime` (singular — must be plural `new_records_realtime`)

### Real-Time Triggers

#### New/Updated Record (Real-Time)

**Verified from server:** `updated_records_realtime`

Fires immediately when a record is created or updated.

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
  "filter": {
    "conditions": [
      {
        "operand": "blank",
        "lhs": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"record_changed\",\"path\":[\"old_record\",\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}",
        "rhs": "",
        "uuid": "filter-new-only-001"
      }
    ],
    "operand": "and",
    "type": "compound"
  },
  "extended_output_schema": [
    {
      "label": "Record",
      "name": "record",
      "type": "object",
      "properties": [
        { "control_type": "text", "label": "Record ID", "type": "string", "name": "11fbe9a6_a16d_4d7e_86ea_afe42ec03005" },
        { "control_type": "text", "label": "Column 1", "type": "string", "name": "<column-uuid-with-underscores>" }
      ]
    },
    {
      "label": "Old record",
      "name": "old_record",
      "type": "object",
      "properties": [
        { "control_type": "text", "label": "Record ID", "type": "string", "name": "11fbe9a6_a16d_4d7e_86ea_afe42ec03005" },
        { "control_type": "text", "label": "Column 1", "type": "string", "name": "<column-uuid-with-underscores>" }
      ]
    }
  ],
  "uuid": "trigger-001"
}
```

**Key details:**
- `since` — ISO datetime; events before this are ignored. Cannot be changed after first run/test. If omitted, defaults to one hour ago. Can go back up to 30 days.
- `filter` — trigger-level filter (NOT inside `block`). Uses the same compound condition syntax as `if` blocks. The example above filters to new records only by checking if `old_record.Record ID` is blank.
- `extended_output_schema` — must include BOTH `record` and `old_record` with identical column properties. The `old_record` contains the pre-update values (empty for new records).

#### New Record (Real-Time)

**Verified name:** `new_records_realtime` (note: **plural**, NOT `new_record_realtime`)

Fires only on new row creation, not updates. Same structure as the real-time updated trigger but without the `old_record` in EOS and without the `filter` block.

### Batch Triggers

#### New Records (Batch)

**Verified from server:** `new_records_polling`

Processes new records in batches on a polling schedule. Key structural difference from real-time: the EOS wraps records in an **array**.

```json
{
  "number": 0,
  "provider": "workato_db_table",
  "name": "new_records_polling",
  "as": "new_rows",
  "keyword": "trigger",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": {
      "zip_name": "tablename.workato_db_table.json",
      "name": "TableDisplayName",
      "folder": ""
    }
  },
  "extended_output_schema": [
    {
      "label": "Records",
      "name": "records",
      "type": "array",
      "of": "object",
      "properties": [
        {
          "label": "Record",
          "name": "record",
          "type": "object",
          "properties": [
            { "control_type": "text", "label": "Record ID", "type": "string", "name": "11fbe9a6_a16d_4d7e_86ea_afe42ec03005" },
            { "control_type": "text", "label": "Column 1", "type": "string", "name": "<column-uuid-with-underscores>" }
          ]
        }
      ]
    }
  ],
  "uuid": "trigger-001"
}
```

**Key differences from real-time triggers:**
- EOS top-level is `records` (array with `"of": "object"`) not `record` (object)
- Inner object is still called `record` but nested inside the array
- No `old_record` on new-only triggers
- `since` parameter is stripped by the server after initial import
- No `filter` block

#### New/Updated Records (Batch)

**Verified name:** `updated_records_polling`

Same batch array EOS pattern as `new_records_polling`, but includes `old_record` inside the array like the real-time variant.

---

## Actions

> Action names verified via golden recipe activation testing on 2026-05-08.

### Create Record

**Verified name:** `add_record`

Creates a single record in a data table.

**CRITICAL:** Column fields must be nested under `parameters` in both `input` and `extended_input_schema`. Without this nesting, activation fails with "At least one record field must be specified in input field".

```json
{
  "number": 1,
  "provider": "workato_db_table",
  "name": "add_record",
  "as": "create_row",
  "keyword": "action",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": "5565",
    "parameters": {
      "<column-uuid-with-underscores>": "value or datapill"
    }
  },
  "extended_input_schema": [
    {
      "label": "Parameters",
      "name": "parameters",
      "type": "object",
      "properties": [
        {
          "control_type": "text",
          "label": "Column 1",
          "name": "<column-uuid>",
          "type": "string",
          "optional": true
        }
      ]
    }
  ],
  "uuid": "create-row-001"
}
```

**Output:** Returns a `record` wrapper object containing Record ID, Created at, Updated at, and all column values:
```json
{
  "record": {
    "11fbe9a6_a16d_4d7e_86ea_afe42ec03005": "uuid-string",
    "<column-uuid>": "value",
    "a5612739_5401_4ae7_bd07_782c1a6fb2d1": "2026-05-08T18:53:45.472+00:00",
    "61aae604_a95e_4519_9091_bb0bf754a67f": "2026-05-08T18:53:45.472+00:00"
  }
}
```

**Output datapill path:** `["record", "<column-uuid>"]`

**Behavior:**
- Required columns must be populated
- Values must match column data types
- Empty fields are not set (column default applies)

### Update Record

**Verified name:** `update_record`

Updates an existing record by Record ID. Partial updates — only fields you provide are changed.

**Input structure:** `record_id` is flat in `input`, column fields go under `parameters` (same as `add_record`). EIS needs a `parameters` wrapper for columns.

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
    "table_id": "5565",
    "record_id": "#{_dp('{...record_id_datapill...')}",
    "parameters": {
      "<column-uuid>": "new value"
    }
  },
  "extended_input_schema": [
    {
      "label": "Parameters",
      "name": "parameters",
      "type": "object",
      "properties": [
        {
          "control_type": "text",
          "label": "Column 1",
          "name": "<column-uuid>",
          "type": "string",
          "optional": true
        }
      ]
    }
  ],
  "uuid": "update-row-002"
}
```

**Output:** Returns a `record` wrapper (same as `add_record`). Datapill path: `["record", "<uuid>"]`.

**Key:** The `record_id` input field identifies which record to update. Pass it from a trigger or search result.

**To clear a field value**, use the `remove_values_from_record` action instead — leaving a field empty in update does NOT clear it.

### Delete Record

**Verified name:** `delete_record`

Deletes a record by Record ID.

**Input structure:** `record_id` is flat in `input`. No `parameters` nesting needed (no column fields to set). No EIS/EOS required on the action block.

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
    "table_id": "5565",
    "record_id": "#{_dp('{...record_id...}')}"
  },
  "uuid": "delete-row-003"
}
```

**Output:** Returns `{ "success": true }`. No record data in output.

### Upsert Record

**Verified name:** `upsert_record`

Creates a new record if no match found, updates existing if match found. Uses a single primary key column for matching.

**CRITICAL:** `primary_field_id` uses the column UUID **with dashes** (not underscores). Column fields go under `parameters` (same as `add_record`/`update_record`).

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
    "table_id": "5565",
    "primary_field_id": "226272d4-759a-465a-878a-40bfe8fdc12e",
    "parameters": {
      "<column-uuid-underscores>": "value or datapill"
    }
  },
  "extended_input_schema": [
    {
      "label": "Parameters",
      "name": "parameters",
      "type": "object",
      "properties": [
        {
          "control_type": "text",
          "label": "Column 1",
          "name": "<column-uuid-underscores>",
          "type": "string",
          "optional": true
        }
      ]
    }
  ],
  "uuid": "upsert-row-004"
}
```

**Output:** Returns `record` wrapper (same as `add_record`) plus a top-level `created` boolean:
```json
{
  "record": { ... column fields ... },
  "created": true
}
```

**Datapill paths:**
- Record fields: `["record", "<column-uuid>"]`
- Created flag: `["created"]`

**UUID format gotcha:** `primary_field_id` takes the dash-format UUID (`226272d4-759a-465a-878a-40bfe8fdc12e`), while column field names in `input.parameters` and EIS use the underscore-format UUID (`226272d4_759a_465a_878a_40bfe8fdc12e`). Using underscores in `primary_field_id` causes an Internal Error at runtime.

### Search Records

**Verified name:** `get_records`

Batch query with typed filters, sorting, and pagination.

**Input structure:** Column filter fields are flat (NOT nested under `parameters`). This differs from `add_record`.

```json
{
  "number": 5,
  "provider": "workato_db_table",
  "name": "get_records",
  "as": "search_rows",
  "keyword": "action",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": "5565",
    "<column-uuid>": "filter value"
  },
  "extended_input_schema": [
    {
      "control_type": "text",
      "label": "Column 1",
      "name": "<column-uuid>",
      "type": "string",
      "optional": true
    }
  ],
  "uuid": "search-rows-005"
}
```

**Output:** Returns `records` array (flat objects, no `record` wrapper per item) and `continuation_token` for pagination:
```json
{
  "records": [
    {
      "11fbe9a6_a16d_4d7e_86ea_afe42ec03005": "uuid-string",
      "<column-uuid>": "value",
      "a5612739_5401_4ae7_bd07_782c1a6fb2d1": "2026-05-08T18:53:45.472+00:00",
      "61aae604_a95e_4519_9091_bb0bf754a67f": "2026-05-08T18:53:45.472+00:00"
    }
  ],
  "continuation_token": null
}
```

**Output datapill path:** `["records"]` for the full array.

**Filters** use AND logic with typed operands per column type:

| Column type | Available operands |
|---|---|
| Short/Long text | equals, is_not_equal_to, starts_with, is_null, is_not_null |
| Integer/Decimal | equals, is_not_equal_to, less_than, greater_than, less_or_equal, greater_or_equal, is_null, is_not_null |
| Boolean | is_true, is_false, is_null, is_not_null |
| Date/DateTime | equals, is_not_equal_to, is_before, is_after, on_or_before, on_or_after, is_null, is_not_null |

The exact JSON shape for advanced filters is TBD — the simple column-value filter in `input` is verified.

See: [patterns/search-records.md](patterns/search-records.md)

### Batch Actions

**No batch action names exist.** Extensive brute-force testing confirmed all tested patterns are invalid:
- `create_records`, `update_records`, `delete_records`
- `add_records`, `upsert_records`
- `batch_create`, `batch_update`, `batch_delete`, `batch_add`, `batch_upsert`
- `bulk_create`, `bulk_update`, `bulk_delete`, `bulk_add`, `bulk_upsert`
- `add_records_batch`, `update_records_batch`, `delete_records_batch`

For batch operations, use a `repeat` loop over individual actions (`add_record`, `update_record`, etc.).

### Truncate Table

**Verified name:** `truncate_table`

Clears all records from a table. Destructive — no undo.

**Input:** Only requires `table_id` — no other fields needed. No `parameters`, EIS, or EOS on the action block.

```json
{
  "provider": "workato_db_table",
  "name": "truncate_table",
  "as": "clear_table",
  "keyword": "action",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": "5565"
  },
  "uuid": "truncate-001"
}
```

**Output:** Runtime output structure not verified (cannot test without destroying data). Activation-verified only.

### Remove Values From Record

**Verified name:** `remove_values_from_record`

Clears specific column values from a record without deleting the record. Different from `update_record` — update replaces values, this action removes them entirely.

**CRITICAL:** `values_to_be_removed` uses the column UUID **with dashes** (same format as `primary_field_id` in upsert). Using underscores causes a runtime Internal Error.

**Input structure:** `record_id` is flat in `input`. `values_to_be_removed` is a single dash-format UUID string identifying which column to clear. No `parameters` nesting.

```json
{
  "provider": "workato_db_table",
  "name": "remove_values_from_record",
  "as": "remove_vals",
  "keyword": "action",
  "dynamicPickListSelection": {
    "table_id": "TableDisplayName"
  },
  "input": {
    "table_id": "5565",
    "record_id": "#{_dp('{...record_id_datapill...}')}",
    "values_to_be_removed": "226272d4-759a-465a-878a-40bfe8fdc12e"
  },
  "extended_output_schema": [
    {
      "label": "Record",
      "name": "record",
      "type": "object",
      "properties": [
        { "control_type": "text", "label": "Record ID", "name": "11fbe9a6_a16d_4d7e_86ea_afe42ec03005", "type": "string" },
        { "control_type": "text", "label": "Column 1", "name": "<column-uuid-underscores>", "type": "string" }
      ]
    }
  ],
  "uuid": "remove-vals-001"
}
```

**Output:** Returns a `record` wrapper object (same as `add_record`). Cleared columns return empty string `""` (not `null`).

**Datapill path:** `["record", "<column-uuid>"]` — same as `add_record`/`update_record`.

---

## Datapill Paths

Datapill paths differ between triggers and actions. **Getting this wrong blocks activation or returns empty values.**

### Real-Time Triggers (`_realtime`)

Real-time triggers output a single `record` object:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"<as-alias>\",\"path\":[\"record\",\"<column-uuid>\"]}')}
```

**Old record value (updated trigger only):**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"record_changed\",\"path\":[\"old_record\",\"<column-uuid>\"]}')}"
```

### Batch Triggers (`_polling`)

Batch triggers output a `records` array. Datapills must traverse: `records` → `current_item` → `record` → column UUID:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"<as-alias>\",\"path\":[\"records\",{\"path_element_type\":\"current_item\"},\"record\",\"<column-uuid>\"]}')}
```

**Verified example (from golden recipe 237600):**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"new_row\",\"path\":[\"records\",{\"path_element_type\":\"current_item\"},\"record\",\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}"
```

### Action Output Paths

**`add_record` output:** Wraps fields under `record` — same as real-time trigger:
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"create_row\",\"path\":[\"record\",\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}"
```

**`upsert_record` output:** Same `record` wrapper plus a `created` boolean at the top level:
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"upsert_row\",\"path\":[\"record\",\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}"
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"upsert_row\",\"path\":[\"created\"]}')}"
```

**`remove_values_from_record` output:** Same `record` wrapper as `add_record`:
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"remove_vals\",\"path\":[\"record\",\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}"
```

**`get_records` output:** Returns `records` array — use `["records"]` to get the full array:
```json
"=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"search_rows\",\"path\":[\"records\"]}').to_json"
```

### Why This Matters

Using real-time-style paths (`["record", "<uuid>"]`) in a batch trigger produces **corrupt datapill references that silently block activation**. The server accepts the import but the recipe cannot start. There is no error message — the datapills just don't resolve.

Similarly, using flat paths (`["<uuid>"]`) for `add_record` output instead of `["record", "<uuid>"]` returns empty strings — the recipe runs but output values are blank.

---

## Patterns

### Trigger + Update Same Row

The most common data table pattern: trigger on a new/updated record, process it, then update the same row with results.

1. Trigger fires on new/updated record, providing the Record ID via `record.11fbe9a6_a16d_4d7e_86ea_afe42ec03005`
2. Process the record (py_eval, API call, etc.)
3. Update the same row using the Record ID datapill from step 1

```json
{
  "provider": "workato_db_table",
  "name": "update_record",
  "input": {
    "table_id": { ... },
    "record_id": "#{_dp('{...trigger record ID...}')}",
    "parameters": {
      "<status-column-uuid>": "processed"
    }
  }
}
```

### New Records Only Filter

To trigger only on new records (not updates) when using `updated_records_realtime`, add a trigger-level filter that checks if `old_record.Record ID` is blank:

```json
"filter": {
  "conditions": [
    {
      "operand": "blank",
      "lhs": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"<as-alias>\",\"path\":[\"old_record\",\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}",
      "rhs": "",
      "uuid": "filter-new-only-001"
    }
  ],
  "operand": "and",
  "type": "compound"
}
```

When a record is newly created, the `old_record` fields are empty. When updated, `old_record` contains the previous values.

### Data Table + Slack Notification

Wire a data table trigger to Slack for row-driven notifications:

1. Trigger on new record in `pending_approvals` table
2. Look up Slack user by email column
3. Send Slack DM with action buttons
4. Update the data table row with Slack channel + message timestamp

See: [slack-recipes/patterns/workbot-triggers.md](../../slack-recipes/patterns/workbot-triggers.md) for Slack-side patterns.

---

## Verification Status

This skill is in **v0.3.0** — all trigger names, all action names, and all action input/output structures are verified via golden recipe end-to-end testing.

### Verified (from golden recipes on server)

**Triggers (all verified via brute-force activation testing 2026-05-08):**
- `new_records_realtime` (real-time new records — plural, NOT `new_record_realtime`)
- `updated_records_realtime` (real-time new/updated)
- `new_records_polling` (batch new records)
- `updated_records_polling` (batch new/updated)
- Naming convention: `_realtime` = real-time, `_polling` = batch

**INVALID trigger names confirmed:** `new_record_realtime` (singular)

**Action names (all verified via activation testing 2026-05-08):**
- `add_record` — create a single record (NOT `create_record`)
- `get_records` — search/query records (NOT `search_records`)
- `update_record` — update a single record by ID
- `delete_record` — delete a single record by ID
- `upsert_record` — create or update by primary key
- `truncate_table` — clear all records from a table (activation-verified, runtime untested)
- `remove_values_from_record` — clear column values from a record

**INVALID action names confirmed:** `create_record`, `search_records`, `add_row`, `insert_record`, `create_row`, `create_records`, `update_records`, `delete_records`, `add_records`, `upsert_records`, `batch_create`, `batch_update`, `batch_delete`, `bulk_create`, `bulk_update`, `bulk_delete`

**Action input structure:**
- `add_record`: column fields MUST be nested under `parameters` in both `input` and EIS
- `update_record`: `record_id` flat in `input`, column fields under `parameters` (same as `add_record`)
- `delete_record`: `record_id` flat in `input`, no `parameters` needed, no EIS/EOS on action block
- `get_records`: column filter fields are flat in `input` (no nesting)
- `upsert_record`: `primary_field_id` flat (DASHES format), columns under `parameters`
- `remove_values_from_record`: `record_id` flat, `values_to_be_removed` as dash-format UUID string, no `parameters`
- `truncate_table`: only `table_id` needed, no other fields

**Action output structure:**
- `add_record`: output wraps fields under `record` object → datapill path `["record", "<uuid>"]`
- `update_record`: same as `add_record` — `record` wrapper → `["record", "<uuid>"]`
- `upsert_record`: `record` wrapper + top-level `created` boolean → `["record", "<uuid>"]` and `["created"]`
- `delete_record`: returns `{ "success": true }` only — no record data
- `get_records`: output has flat `records` array + `continuation_token` → datapill path `["records"]`
- `remove_values_from_record`: `record` wrapper (same as `add_record`) — cleared columns return empty string `""`

**General:**
- Provider: `workato_db_table`
- Config: `account_id: null`, `name: "workato_db_table"` required
- `table_id` reference object format: `{zip_name, name, folder}`
- `table_id` server format: numeric string `"5565"`
- `dynamicPickListSelection`: `{"table_id": "TableDisplayName"}`
- Real-time EOS: `record` + `old_record` wrappers (singular objects)
- Batch EOS: `records` array → inner `record` object
- UUID column naming with underscores
- Meta Record ID: `11fbe9a6_a16d_4d7e_86ea_afe42ec03005`

### Remaining Gaps

- [ ] Search advanced filter JSON structure (beyond simple column-value filter)
- [ ] `truncate_table` runtime output structure (cannot test without destroying data)
- [ ] Output format toggle (field hash vs field name)

### Golden Recipes (on server)

| Action | Recipe ID | Endpoint Path | Status |
|--------|-----------|---------------|--------|
| `add_record` | 237619 | `golden-dt-create` | Verified |
| `get_records` | 237620 | `golden-dt-search` | Verified |
| `update_record` | 237621 | `golden-dt-update` | Verified |
| `delete_record` | 237622 | `golden-dt-delete` | Verified |
| `upsert_record` | 237624 | `golden-dt-upsert` | Verified |
| `remove_values_from_record` | 237627 | `golden-dt-remove-values` | Verified |

---

## References

- **Base Skill:** `workato-recipes` — recipe structure, triggers, control flow, formulas
- **Workato Docs:** https://docs.workato.com/en/data-tables/data-table-connector.html
- **Patterns:** `patterns/` directory
- **Validation:** [validation-checklist.md](validation-checklist.md)
