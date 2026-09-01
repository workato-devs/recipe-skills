---
name: google-sheets-recipes
description: Google Sheets integration recipes for Workato. Enables AI agents to generate valid recipe JSON for reading, appending, and updating rows in a Google Sheet via the native Google Sheets connector.
license: MIT
metadata:
  author: Workato
  version: "0.1.0"
---

# Google Sheets Recipes Skill

> **DEPENDENCY: Load the `workato-recipes` base skill first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

You are now equipped with Google Sheets-specific knowledge for writing Workato recipes using the **native Google Sheets connector**. This skill covers 3 audited actions — narrower than the other connector skills in this repo. Treat anything not listed in `lint-rules.json` as unverified, not confirmed-absent.

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects:
1. **Read existing Google Sheets `.recipe.json` files** to understand local patterns and, critically, the sheet's actual dynamic field names (see "Dynamic Column Fields" below — these are NOT predictable from the header text alone without checking).

### For GREENFIELD projects:
1. **Use skill templates** — see `templates/` for validated, real, pushed examples.
2. **Warn the user up front**: the first time an action touches a *new* sheet (different spreadsheet, different headers), its dynamic column field names must be discovered by configuring the action once in the Workato UI and pulling the recipe back down (`wk recipes export <id>`) — this skill cannot predict them blind. This is a hard boundary, not a gap in this skill's coverage.

### ALWAYS:
1. **Ask for the connection name** — exact name of the Google Sheets connection in the workspace.
2. **Ask for the spreadsheet and sheet/tab name** — required for every action.
3. **Never guess dynamic column field names** (`col_status`, `col_1`, etc.) for a sheet you haven't seen a real export of. See the pattern doc.
4. **Use descriptive UUIDs** — never copy random hex UUIDs from existing recipes.

---

## Capabilities

With this skill loaded, you can:
- Create recipes that read a range of rows from a sheet (`get_spreadsheet_rows_v4`)
- Create recipes that append a new row to a sheet (`add_spreadsheet_row_v4`)
- Create recipes that update an existing row by row number (`update_row_v4_new`)

See `skill.yaml`'s `gaps` list for what this skill does **not** yet cover (triggers, search/filter, delete, formatting) — do not assume those are unsupported by the connector, only that they're unaudited here.

---

## Google Sheets Connector

This skill covers the native Google Sheets connector (`google_sheets`). See `lint-rules.json` for the authoritative list of valid action names — there are no verified trigger names yet.

### Provider

```json
"provider": "google_sheets"
```

### Connection Configuration

```json
{
  "keyword": "application",
  "provider": "google_sheets",
  "skip_validation": false,
  "account_id": {
    "zip_name": "my_google_sheets_account.connection.json",
    "name": "My Google Sheets account",
    "folder": ""
  }
}
```

Connections are OAuth-based. **The CLI cannot complete OAuth.** `wk connections create --provider google_sheets ...` creates a connection stub with `authorization_status: null` — a human must authorize it in the Workato UI before any recipe using it can activate. Poll `wk connections get <id>` until `authorization_status: "success"`.

---

## Native Connector Guidance

### Choosing the Right Action

- **`get_spreadsheet_rows_v4`** — Use to read a range of rows. Takes a plain numeric `range` (`"2:1000"`, format `Start row:End row` — NOT A1 notation, NOT a column range). Returns `rows[]`, each with `row_number` plus one `col_<header>` field per column.
- **`add_spreadsheet_row_v4`** — Use to append a brand-new row. Its dynamic fields are **positional** (`col_1`, `col_2`, `col_3`, ...) matching column order, unlike the other two actions. Has an `is_top_left` field controlling insertion anchor.
- **`update_row_v4_new`** — Use to modify an existing row, located by `row_number` (a plain string field, not a lookup by content). Its dynamic `data`/"Columns" field uses header-derived names (`col_status`, not positional), matching `get_spreadsheet_rows_v4`'s output naming — but NOT matching `add_spreadsheet_row_v4`'s positional naming. See the pattern doc for the full asymmetry.

**This naming inconsistency between actions is the single most common source of silent bugs with this connector.** Read `patterns/dynamic-column-fields.md` before writing any of these three actions by hand.

---

## Google Sheets Datapill Paths

Standard native-action output access, no `["body"]` wrapper:

```json
"path": ["rows"]
"path": ["row_number"]
"path": ["col_status"]
```

Referencing a value from `get_spreadsheet_rows_v4`'s row array inside a `foreach`, or serializing the whole array to return from a skill/callable-recipe trigger, requires **formula mode** (`=`) because `.to_json` is a method call:

```
=_dp('{"pill_type":"output","provider":"google_sheets","line":"<action-as-id>","path":["rows"]}').to_json
```

The same reference inside `#{}` interpolation (not formula mode) will not work for the `.to_json` call — see the base skill's datapill-syntax doc for the general `#{}` vs `=` rule.

---

## Common Patterns

### Read-modify-write

There is no "upsert" or "find and update" action in this skill's verified set. The pattern is: call `get_spreadsheet_rows_v4` first (or use a `row_number` you already have from a prior read), then call `update_row_v4_new` with that exact `row_number`. Do not try to re-derive a row number from a data value like an id column — `row_number` is the sheet's literal row position, unrelated to your data.

### Partial updates

`update_row_v4_new`'s `data` object only needs the columns you're actually changing — omitted columns are left untouched. Do not pass empty strings for columns you don't want to change; omit the key entirely.

---

## Validation

See [validation-checklist.md](validation-checklist.md).

---

## Templates

- `templates/get-rows.json` — read a range of rows, serialize to JSON
- `templates/update-row.json` — update one row's status column by row number, with typed input parameters on a skill trigger
- No `add-row.json` template yet. `add_spreadsheet_row_v4`'s action name and positional-field convention (`col_1`, `col_2`, ...) are in `lint-rules.json`, but no full `extended_input_schema` has been captured — do not fabricate one; configure the action in the UI and export it first.

---

## Reference Files

- `skills/workato-recipes/SKILL.md` — Base platform knowledge
- `mcp-server-recipes` skill — the `workato_skill` trigger used in both templates here; load it whenever the recipe is for an MCP server/tool, not just this connector
- `skills/google-sheets-recipes/patterns/dynamic-column-fields.md` — read this before writing any action by hand
- `skills/google-sheets-recipes/templates/` — validated recipe templates

---

## Usage

### Before Generating Recipes

**Ask the user for these details:**

1. **Google Sheets connection name** (REQUIRED)
2. **Spreadsheet and sheet/tab name** (REQUIRED)
3. **Operation type** — read, append, or update?
4. If update or append: **has this exact sheet's dynamic column fields been captured before** (via a prior export in this project)? If not, say so explicitly rather than guessing `col_<header>` names.

### Example Prompts

- "Create a recipe that reads all rows from my tracker sheet"
- "Create a recipe that appends a new row with a title and status"
- "Create a recipe that updates the status column for a given row number"
