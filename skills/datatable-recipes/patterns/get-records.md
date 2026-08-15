# Get Records Pattern

> **Status:** Action name and filter shape verified 2026-08-12; operand enum and filter behaviour
> verified 2026-08-14/15 — both against live recipes and platform activation. Sections carry their
> own verification state; anything marked **unverified** has not been measured.

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
- The operand key is `op_default`; the value key is `value_default`.
- Live recipes also show **`op_boolean`** on the one boolean filter among the 14 harvested, but the
  key is **not** type-dispatched. Measured against an all-true boolean column: `op_default: isfalse`
  and `op_boolean: isfalse` both return 0 rows, and both `istrue` forms return all 2. `op_boolean`
  is what the UI writes for a boolean column, not what the platform requires.
- An **unrecognised** operand key is not rejected — at activation or at runtime. The filter is
  dropped and the step returns the whole table. See [Filters that are silently
  dropped](#filters-that-are-silently-dropped).

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
| `add_record` `parameters` keys | underscores | `316ea4b9_db3d_4ab9_bebc_55fe9f519758` |

Output record keys are a third case and depend on `output_format` — see [Output](#output).

SKILL.md documents the same split for `upsert_record`'s `primary_field_id` (dashes) against its
`parameters` keys (underscores), and warns that using underscores in `primary_field_id` causes a
runtime Internal Error.

### Operands — the `ApiQueryOperation` enum

The operand vocabulary is a backend enum. A non-member fails the **job** (not activation) with an
error that names it, which makes the enum directly probeable:

```
parse request payload error: Expected input type "ApiQueryOperation", found "zzz_bogus".
(occurred while parsing "ApiQueryCondition") (occurred while parsing "list_ApiQueryCondition")
(occurred while parsing "ApiQueryRequest")
```

Candidate names were probed one at a time against that oracle. **12 are members**, each then run
against known rows on a 2-row table (`label` = `FOUND1`, `TEST101`), filtering `label = FOUND1`:

| Operand | Rows returned |
|---|---|
| `eq` | `FOUND1` |
| `ne` | `TEST101` |
| `lt` | none — comparison is lexical on a string column |
| `gt` | `TEST101` |
| `lte` | `FOUND1` |
| `gte` | both |
| `starts_with` | `FOUND1` |
| `in` | member; a scalar value returned none — the list form was not probed |
| `isnull` | none |
| `isnotnull` | both |
| `istrue` | boolean column: both rows (both true) |
| `isfalse` | boolean column: none |

**Not members** — each produced the `ApiQueryOperation` error: `le`, `ge`, `less_than`,
`greater_than`, `less_or_equal`, `greater_or_equal`, `equals`, `is_not_equal_to`, `not_equals`,
`neq`, `ends_with`, `endswith`, `contains`, `not_contains`, `contains_any`, `is_null`,
`is_not_null`, `null`, `not_null`, `present`, `ispresent`, `blank`, `empty`, `isempty`,
`isnotempty`, `isblank`, `nin`, `notin`, `not_in`, `between`, `matches`, `like`, `has`, `exists`,
`sw`, `is_true`, `is_false`.

Note the spelling throughout: `istrue`, not `is_true`. There is no `contains` and no `ends_with`.

`istrue` / `isfalse` used on a **string** column fail with `specified value for Doc(label) is
invalid` — a valid enum member on the wrong column type, a different error from a non-member.

### Filters that are silently dropped

**A filter is the one place in this surface where the platform returns wrong data instead of
erroring.** Two cases, both measured, both leaving the job green:

| Case | Result |
|---|---|
| Unrecognised operand key (`op_zzzkey: "eq"`) | filter dropped — **every row** returned |
| Correct key and a member operand, on an **integer** column | filter dropped — **every row** returned |

The integer case reproduced on three tables, against every encoding tried: `value_default`,
`value_integer`, `value_number`, `value`, `value_int`, `values`, `value_decimal`; a string, a native
JSON number, and formula mode (`=999`); `op_default` and `op_integer`; with and without the
column-type map; with and without the step's `extended_input_schema`. All returned every row.
`date_time` and `id` columns behave the same way — `gt` and `lt` against the *same* timestamp both
returned all rows, which is impossible if either had been applied. Those date probes were on system
columns; a **user-defined** `date_time` column and a **decimal** column remain untested.

Only `string` and `boolean` columns are confirmed to filter correctly.

This is a platform behaviour, not a recipe-authoring mistake — no change to a recipe made an
integer filter apply. Until it changes: **filter data tables on string columns, and check the
returned row count** — a step that returns the whole table is the symptom, and nothing in the job
log will flag it.

### What activation does not check

`PUT /api/recipes/:id/start` validates `table_id` existence and `filters[].field_id` presence, and
nothing else about a filter:

| Probe | Activation |
|---|---|
| `op_default: "zzz_bogus"` — non-member operand | **accepted** |
| `op_zzz: "eq"` — unknown operand key | **accepted** |
| filter entry with no operand at all | **accepted** |
| `field_id` = an all-zeros UUID naming no column | **accepted** |
| `field_id` absent | refused — `Filters/1/Column name can't be blank` |
| `table_id` = 99999999 | refused — `Table ID Does not exist in input field` |

This is the opposite of if-condition operands, which **are** rejected at activation (see the
condition-operand work in recipe-skills #15). The two surfaces do not behave alike, so "the recipe
activated" says almost nothing about whether a data-table filter is correct.

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

Per SKILL.md's activation-verified shape: a flat `records` array plus `continuation_token`.

Record keys depend on `output_format`. Under **`field_name_to_value`** — 8 of the 13 live
`get_records` steps harvested — they are human column **names**, plus `Record ID`, `Created at` and
`Updated at`:

```json
{"records": [{"Created at": "…", "Record ID": "4e32e358-…", "course_code": "FOUND1",
              "label": "FOUND1", "api_client_id": 0, "active": true}],
 "continuation_token": null}
```

The underscored-UUID record keys documented elsewhere must belong to a different `output_format`;
which one is **unverified**, as are the other formats. Note that the datapill path in
[Accessing Results](#accessing-results-in-datapills) below uses an underscored UUID — that step's
`output_format` was not recorded, so treat the two as belonging to different formats until
measured.

## Accessing Results in Datapills

Array access uses `path_element_type: current_item` (same as Salesforce):

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"find_rows\",\"path\":[\"records\",{\"path_element_type\":\"current_item\"},\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}"
```

Recipe `205094` (`running: false`) reads a `get_records` result into `update_record`'s `record_id`
this way. The wrapper shape is otherwise **unverified**.

## Action names

`lint-rules.json` is authoritative for which names are valid — this file does not restate them.
Re-verified 2026-08-12 that its list still matches what activation accepts, including that the two
names the old pattern file taught are still rejected:

```
["name","search_records","is invalid"]
```

Worth knowing when reading that response: a name the platform does not know is rejected at `name`;
a known name whose required input is missing fails on that input instead. Both return
`success: false`, so the response body — not the success flag — is what distinguishes them.

This is the same failure shape as an invalid condition operand: the recipe lints clean, pushes
fine, and is refused at activation.
