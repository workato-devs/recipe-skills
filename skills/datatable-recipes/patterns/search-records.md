# Search Records Pattern

> **Status:** Action name and filter input shape are unverified. Build a golden recipe to validate.

## Overview

The `search_records` action queries a data table with typed filters, sorting, and pagination. Unlike Salesforce's SOQL-based search, data table search uses structured filter objects with per-column-type operands.

## Basic Search

```json
{
  "number": 1,
  "provider": "workato_db_table",
  "name": "search_records",
  "as": "find_rows",
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
    "limit": "100"
  },
  "uuid": "search-rows-001"
}
```

## Filter Operands by Column Type

| Column type | Operand options |
|---|---|
| Short/Long text | `equals`, `is_not_equal_to`, `starts_with`, `is_null`, `is_not_null` |
| Integer/Decimal | `equals`, `is_not_equal_to`, `less_than`, `greater_than`, `less_or_equal`, `greater_or_equal`, `is_null`, `is_not_null` |
| Boolean | `is_true`, `is_false`, `is_null`, `is_not_null` |
| Date/DateTime | `equals`, `is_not_equal_to`, `is_before`, `is_after`, `on_or_before`, `on_or_after`, `is_null`, `is_not_null` |
| Link to table | `equals`, `is_not_equal_to`, `in`, `is_null`, `is_not_null` |
| File | `equals`, `is_not_equal_to`, `is_null`, `is_not_null` |
| Multi-value | `contains`, `is_null`, `is_not_null` |

All filters use AND logic (no OR support at the connector level — use multiple searches or post-filter with if/else).

## Filter Input Shape (TBD)

The exact JSON structure for filters in recipe input is unverified. Possible shapes based on other Workato connectors:

**Option A: Structured filter array**
```json
"input": {
  "table_id": { ... },
  "filter": [
    { "column": "<uuid>", "operand": "equals", "value": "active" }
  ],
  "limit": "100"
}
```

**Option B: Flat column-value pairs (like Salesforce search_sobjects)**
```json
"input": {
  "table_id": { ... },
  "<status-column-uuid>": "active",
  "limit": "100"
}
```

Build a golden recipe with a filter in the UI and export to determine the actual shape.

## Sorting

Input accepts:
- `sort_by` — column to sort on
- `sort_direction` — `ascending` or `descending`

Exact field names in recipe JSON are TBD.

## Pagination

- `limit` — max records per page (default 100, max 1000)
- `next_page_token` — token from previous result to fetch next page

For multi-page results, use a foreach loop with the next_page_token.

## Output

```json
{
  "records": [
    {
      "11fbe9a6_a16d_4d7e_86ea_afe42ec03005": "record-id-value",
      "<column-uuid>": "value",
      ...
    }
  ],
  "next_page_token": "..."
}
```

## Accessing Search Results in Datapills

Array access uses `path_element_type: current_item` (same as Salesforce):

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"find_rows\",\"path\":[\"records\",{\"path_element_type\":\"current_item\"},\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}"
```

This needs verification — the wrapper might be different for search results vs trigger output.
