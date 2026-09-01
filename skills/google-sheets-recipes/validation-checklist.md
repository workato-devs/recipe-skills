# Google Sheets Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

The following checks are specific to Google Sheets connector recipes.

---

## Config & Connection

- [ ] Config includes `google_sheets` provider with connection reference
- [ ] Action `name` matches a valid name in `lint-rules.json`
- [ ] If the connection was just created, its `authorization_status` has been confirmed `"success"` via `wk connections get <id>` — a fresh connection stub cannot activate a recipe

## Dynamic Column Fields (the most common source of bugs)

- [ ] Dynamic field names (`col_status`, `col_1`, etc.) were taken from a real `wk recipes export` of a recipe configured against **this specific sheet** — not assumed from a different sheet's example or guessed from header text
- [ ] `update_row_v4_new` and `get_spreadsheet_rows_v4` use header-derived names (`col_status`); `add_spreadsheet_row_v4` uses positional names (`col_1`, `col_2`, ...) — these are NOT interchangeable
- [ ] No key in a `data`/"Columns" object is left over from copy-pasting between these two naming schemes
- [ ] `update_row_v4_new`'s `data` object only includes columns actually being changed — no empty-string placeholders for untouched columns

## Row Targeting

- [ ] `row_number` is the sheet's literal row position (1-indexed, header row counts), not derived from a data column's value
- [ ] A `row_number` used in `update_row_v4_new` came from a prior `get_spreadsheet_rows_v4` call's output, or is otherwise known to be correct — not guessed

## `get_spreadsheet_rows_v4` Range Format

- [ ] `range` is a plain numeric range in the format `Start row:End row` (e.g. `2:1000`) — NOT A1 notation (`A2:E1000`), NOT a column range (`A:E`)
- [ ] `range` starts at row 2 (or later) if row 1 is the header row

## Datapill Paths

- [ ] Native action datapills do NOT use a `["body"]` wrapper
- [ ] Serializing `rows[]` (or any array output) to a string uses formula mode (`=_dp(...).to_json`), not `#{}` interpolation
