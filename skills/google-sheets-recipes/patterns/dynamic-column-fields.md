# Dynamic Column Fields

Google Sheets actions that read or write specific columns don't use fixed field names — they derive field names from your sheet's actual header row, at the time the action was configured. This is the single biggest source of confusion when working with this connector, so read this before writing any Sheets action by hand.

## Two different naming schemes exist, and they don't agree

**`get_spreadsheet_rows_v4`** and **`update_row_v4_new`** name dynamic fields after your header text, lowercased and prefixed: a `status` header becomes `col_status`, a `Due Date` header would become `col_due_date`, etc.

**`add_spreadsheet_row_v4`** does **not** do this. Its dynamic fields are purely positional: `col_1`, `col_2`, `col_3`, ... matching column order (A, B, C, ...), regardless of header text.

```
CORRECT — reading/updating by header name (get_spreadsheet_rows_v4, update_row_v4_new):
"data": { "col_status": "Published" }

CORRECT — appending, by position (add_spreadsheet_row_v4):
"data": { "col_1": "42", "col_2": "My Title", "col_3": "Published" }

WRONG — using header-derived names on an append action:
"data": { "col_status": "Published" }   // add_spreadsheet_row_v4 ignores this
```

This asymmetry is easy to miss because both actions display a field labeled "Columns" in the UI — the *labels* look the same, the underlying keys don't.

## The `data` object silently drops unrecognized keys

If you send a key that doesn't match one of the action's declared dynamic properties, the platform drops it before the request reaches Google Sheets — no error, no warning. The action still reports success. This means a typo'd column key (or a leftover key from copy-pasting between `update_row_v4_new` and `add_spreadsheet_row_v4`) produces a silent no-op on that field, not a failure you can catch from the response.

**Always verify the field names your specific sheet produced** by pulling the recipe after configuring the action once (`wk recipes export <id>`), rather than assuming `col_<header>` naming from a different sheet's example. Header text with spaces, punctuation, or capitalization may not normalize exactly the way you'd guess.

## Discovering your sheet's actual field names

There is no way to predict a sheet's dynamic field names without configuring the action against that specific sheet at least once (in the UI) and exporting the result:

```bash
wk recipes export <recipe-id> --json
```

Look at the action step's `extended_input_schema` (for `update_row_v4_new`) or `extended_output_schema` (for `get_spreadsheet_rows_v4`) — the `data`/`columns` object's `properties` array lists every dynamic field name Workato actually created for that sheet.

## `row_number` is a plain string field, not a lookup by content

Both `update_row_v4_new` and `get_spreadsheet_rows_v4`'s range parameter work off the spreadsheet's literal row number (1-indexed, including the header row) — not any value in your data. If you're updating a row you got from a prior `get_spreadsheet_rows_v4` call, pass along its `row_number` output field; don't try to re-derive a row number from an id or other column value.

## Range format for `get_spreadsheet_rows_v4`

The `range` field takes a plain numeric range, `Start row:End row` (e.g. `2:1000`) — **not** A1 notation (`A2:E1000`) and not a column range (`A:E`). Start from row 2 if row 1 is your header.
