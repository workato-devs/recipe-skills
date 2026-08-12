# Get Records Pattern

> **Status:** Action name and filter shape verified 2026-08-12 against live recipes and platform
> activation. Sections carry their own verification state; anything marked **unverified** has not
> been measured.

## Overview

The `get_records` action queries a data table with filters, sorting, and pagination. The action is
`get_records` — `search_records` is rejected at activation (see Action names below).

## Basic Get

```json
{
  "number": 1,
  "provider": "workato_db_table",
  "name": "get_records",
  "as": "find_rows",
  "keyword": "action",
  "input": {
    "table_id": "6024",
    "limit": "100",
    "output_format": "field_name_to_value"
  },
  "uuid": "get-rows-001"
}
```

In recipes exported from the server, `table_id` is the table's numeric id as a string (`"6024"`);
two harvested recipes instead carry a display name (`"Company Directory"`). SKILL.md also documents
the `{zip_name, name, folder}` reference-object form used in project files — both forms exist, in
different contexts. Neither the object form nor a bare table UUID was probed here.

## Filters

```json
"input": {
  "table_id": "6024",
  "limit": "1",
  "order_by_field_id": "c94319e3-c93e-4f06-b8db-4ec5d73513a0",
  "order_direction": "desc",
  "output_format": "field_name_to_value",
  "filters": [
    {
      "field_id": "2ea0e0d4-d332-482f-958a-d2e6ae5ce42d",
      "op_default": "eq",
      "value_default": "#{_dp('{...}')}"
    }
  ]
}
```

Verbatim from recipe `259412` (`running: true`).

- The key is `filters` (plural); each entry uses `field_id`, not `column`.
- The operand key varies. `op_default` carries the operand in every non-boolean filter observed
  (13 of 14); the one boolean filter used **`op_boolean`**. There is no single `operand` key.
  Which key applies to which column type, beyond boolean, is **unverified**.
- The value key is `value_default`, paired with `op_default`.

### Column-type map — optional, purpose unverified

Two harvested recipes carry a top-level map alongside `filters`, one entry per column as
`"<column-uuid>": "<type>"` (`"string"`, `"boolean"`, `"id"`, `"date_time"`):

```json
"filters": [ { "field_id": "0a03e30f-...", "op_boolean": "istrue" } ],
"0a03e30f-...": "boolean",
"11fbe9a6-...": "id"
```

Both recipes carrying it are `running: false`. Recipe `259412`, which is running and both filters
and sorts, carries **no** such map — so it is **not required**. What writes it and what consumes it
are **unverified**.

### UUID punctuation differs by position

| Position | Form | Observed example |
|---|---|---|
| `filters[].field_id`, `order_by_field_id` | hyphens | `2ea0e0d4-d332-482f-958a-d2e6ae5ce42d` |
| `add_record` `parameters` keys, output record keys | underscores | `316ea4b9_db3d_4ab9_bebc_55fe9f519758` |

SKILL.md documents the same split for `upsert_record`'s `primary_field_id` (dashes) against its
`parameters` keys (underscores), and warns that using underscores in `primary_field_id` causes a
runtime Internal Error.

### Operands

Observed in live recipes: `eq` and `starts_with` under `op_default`, `istrue` under `op_boolean`.
Note `istrue`, not `is_true`.

The full per-column-type operand vocabulary is **unverified**.

## Sorting

- `order_by_field_id` — the column UUID (hyphens) to sort on
- `order_direction` — `asc` or `desc`

`sort_by` / `sort_direction` and `ascending` / `descending` do not appear in any harvested recipe;
they were not probed.

## Pagination

`limit` is a string (`"1"` and `"100"` observed). Per SKILL.md, the output carries
**`continuation_token`** for paging. Default and maximum values for `limit`, and multi-page
handling, are **unverified**.

## Output

Per SKILL.md's activation-verified shape: a flat `records` array plus `continuation_token`. Output
record keys use underscored UUIDs. `output_format: "field_name_to_value"` appears in 8 of the 13
live `get_records` steps harvested; its alternatives are **unverified**.

## Accessing Results in Datapills

Array access uses `path_element_type: current_item` (same as Salesforce):

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"find_rows\",\"path\":[\"records\",{\"path_element_type\":\"current_item\"},\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}"
```

Recipe `205094` (`running: false`) reads a `get_records` result into `update_record`'s `record_id`
this way. The wrapper shape is otherwise **unverified**.

## Action names

`SKILL.md` carries the full list, verified by activation testing 2026-05-08, and `lint-rules.json`
rejects `search_records` and `create_record` by name. Re-verified 2026-08-12:

| Name | Activation response |
|---|---|
| `get_records` | accepted |
| `search_records` | rejected — `["name","search_records","is invalid"]` |
| `create_record` | rejected — `["name","create_record","is invalid"]` |

A name the platform does not know is rejected at `name`; a known name whose required input is
missing fails on that input instead. Both return `success: false`, so the response body — not the
success flag — is what distinguishes them.

This is the same failure shape as an invalid condition operand: the recipe lints clean, pushes
fine, and is refused at activation.
