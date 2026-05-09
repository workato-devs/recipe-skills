# UUID Column Mapping

## The Problem

Unlike every other Workato connector, data table columns are identified by UUIDs in recipe JSON — not by human-readable field names. A column labeled "Email" in the UI becomes `5d420ed4_eafd_44d7_89ae_77ed9c46dba5` in the recipe.

This means you cannot write a data table recipe from scratch without first knowing the column UUIDs.

## How UUIDs Are Formatted

The server stores column UUIDs with hyphens: `5d420ed4-eafd-44d7-89ae-77ed9c46dba5`

In recipe JSON, hyphens are replaced with underscores: `5d420ed4_eafd_44d7_89ae_77ed9c46dba5`

## Discovering Column UUIDs

### Method 1: Export an existing recipe

Build a minimal recipe in the Workato UI that triggers on the table. Export it. The `extended_output_schema` in the trigger contains all column UUIDs:

```json
"extended_output_schema": [
  {
    "name": "record",
    "properties": [
      { "name": "11fbe9a6_a16d_4d7e_86ea_afe42ec03005", "label": "Record ID" },
      { "name": "5d420ed4_eafd_44d7_89ae_77ed9c46dba5", "label": "Email" },
      { "name": "a1b2c3d4_e5f6_7890_abcd_ef1234567890", "label": "Status" }
    ]
  }
]
```

### Method 2: Read the table schema file

If the project includes a `.workato_db_table.json` file, it contains the column definitions with UUIDs.

### Method 3: Workato API

Use `GET /api/data_tables/{table_id}` to retrieve the table schema programmatically.

## Universal Record ID

One UUID is constant across ALL data tables:

```
11fbe9a6_a16d_4d7e_86ea_afe42ec03005
```

This is the built-in Record ID column. Every record has one. Use it for:
- Identifying records in update/delete actions
- Passing record references between steps
- Joining data across recipes

## Placeholder Pattern

When writing recipes before the table exists, use descriptive placeholders:

```json
{
  "name": "COLUMN_UUID_email",
  "label": "Email",
  "type": "string",
  "control_type": "text"
}
```

Document clearly that placeholders must be replaced with real UUIDs after the table is created.

## Output Format Toggle

The data tables connector supports two output modes:

**Field hash to value (default):** Uses UUID column names. This is what recipe JSON always uses for datapill references.

**Field name to value:** Uses human-readable column names. More intuitive but breaks if columns are renamed. The JSON representation of this toggle in recipe input is TBD — needs golden recipe validation.

## Column Types and Schema Properties

| Column type | `type` | `control_type` | Extra properties |
|---|---|---|---|
| Short text | `string` | `text` | — |
| Long text | `string` | `text-area` | — |
| Integer | `integer` | `integer` | `parse_output: "integer_conversion"` |
| Decimal | `number` | `number` | `parse_output: "float_conversion"` |
| Boolean | `boolean` | `checkbox` | `parse_output: "boolean_conversion"`, `toggle_field`, `toggle_hint` |
| Date | `date` | `date` | `parse_output: "date_time_conversion"`, `render_input: "date_time_conversion"` |
| Date/Time | `date_time` | `date_time` | `parse_output: "date_time_conversion"`, `render_input: "date_time_conversion"` |
| Link to table | `object` | — | Nested `record_id` + `display_name` properties |
| File | `object` | — | TBD |
| Multi-value | `array` | — | TBD |
