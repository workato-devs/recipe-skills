# Smart Lists

Workato's "Smart Lists" feature exposes a `workato_smart_list` provider (`create_list`, `insert_rows`, `query_list`) plus a related `workato_list` provider (`create_list`). It builds an in-memory, SQLite-backed table from an array of records, then lets you run real SQL (`SELECT`, `MAX`, `GROUP BY`, etc.) against it — a materially different capability from [`workato_variable`'s `declare_list`](variables-and-lists.md), which only holds a plain list for iteration/insertion, not queries.

---

## When to Use Smart Lists Over `declare_list`

Use `workato_smart_list` when:

- You need to run an actual SQL query over a list — aggregation (`MAX`, `GROUP BY`, `DISTINCT`), filtering by a `WHERE` clause, or joining columns — not just iterating over items
- The list is large enough that a `foreach` + `if` chain to filter/aggregate it would be unwieldy (see [python-snippets.md](python-snippets.md) for the same tradeoff against `py_eval`)

Use `workato_variable`'s `declare_list`/`insert_to_list` (see [variables-and-lists.md](variables-and-lists.md)) when:

- You only need to accumulate items for later `foreach` iteration, with no querying

---

## Config Entry

```json
{
  "keyword": "application",
  "provider": "workato_smart_list",
  "skip_validation": false,
  "account_id": null
}
```

This is a platform provider — no external connection, `account_id: null`.

---

## Creating a List: `create_list` / `insert_rows`

Both actions take a `list_source` (a datapill referencing an array of records — typically another action's array output) and a `list_name`, and both produce the same output shape: `list_name`, a `columns` object (one property per inferred column, each carrying a `list_data_type`), and a `row_count`.

**`create_list`** — creates a fresh named list from `list_source`:

```json
{
  "number": 2,
  "provider": "workato_smart_list",
  "name": "create_list",
  "as": "create_releases_list",
  "keyword": "action",
  "input": {
    "list_source": "=_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"api_call\",\"path\":[\"response\",\"array\"]}')",
    "list_name": "Liferay Releases",
    "primary_index": "releaseKey"
  },
  "uuid": "create-releases-list-001"
}
```

**`insert_rows`** — same shape, plus a `create_table_if_not_exist` toggle (verified `true`) to create the underlying table on first use rather than requiring a separate `create_list` step:

```json
{
  "number": 9,
  "provider": "workato_smart_list",
  "name": "insert_rows",
  "as": "insert_pids_rows",
  "keyword": "action",
  "toggleCfg": { "create_table_if_not_exist": true },
  "input": {
    "list_source": "=_dp('{\"pill_type\":\"output\",\"provider\":\"liferay_connector_...\",\"line\":\"...\",\"path\":[\"body\",\"items\"]}')",
    "create_table_if_not_exist": "true",
    "list_name": "Liferay_Pids",
    "primary_index": "id"
  },
  "uuid": "insert-pids-rows-001"
}
```

`primary_index` names the column(s) to index for query performance — pick fields you'll filter/join on.

### Referencing columns in downstream SQL

`create_list`/`insert_rows`' output `columns` object holds one datapill-able field per inferred column (e.g. `["columns", "releaseKey"]`) — **these column-name datapills are how you reference column names inside a `query_list` SQL string**, not string literals, so the query stays valid if a column is ever renamed upstream.

---

## Querying a List: `query_list`

Runs a real SQL string against a list created by `create_list`/`insert_rows`. Column names in the `sql` field are datapills referencing the creating step's `columns` output, interpolated with `#{}`:

```json
{
  "number": 3,
  "provider": "workato_smart_list",
  "name": "query_list",
  "as": "query_latest_release",
  "keyword": "action",
  "toggleCfg": { "csv": true },
  "input": {
    "output_schema_by": "index",
    "csv": "false",
    "headers": "false",
    "col_sep": "comma",
    "sql": "SELECT #{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_smart_list\",\"line\":\"create_releases_list\",\"path\":[\"columns\",\"productGroupVersion\"]}')}, MAX(#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_smart_list\",\"line\":\"create_releases_list\",\"path\":[\"columns\",\"releaseKey\"]}')}) FROM #{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_smart_list\",\"line\":\"create_releases_list\",\"path\":[\"list_name\"]}')} WHERE #{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_smart_list\",\"line\":\"create_releases_list\",\"path\":[\"columns\",\"productGroupVersion\"]}')} LIKE \"20%\" GROUP BY #{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_smart_list\",\"line\":\"create_releases_list\",\"path\":[\"columns\",\"productGroupVersion\"]}')}",
    "result_schema_json": "[{\"name\":\"productGroupVersion\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"Product group version\"},{\"name\":\"releaseKey\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"Release key\"}]"
  },
  "uuid": "query-latest-release-001"
}
```

**Key fields:**
- `sql` — the query string. Table name is also a datapill (`["list_name"]`), not a hardcoded string.
- `result_schema_json` — a stringified JSON array declaring the shape of each result row; must match the columns your `SELECT` actually returns.
- `output_schema_by: "index"` and `col_sep: "comma"` were the verified values; `csv`/`headers` toggle whether results come back as a CSV-style string vs. structured rows.

### Reading query results

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_smart_list\",\"line\":\"query_latest_release\",\"path\":[\"rows\"]}')}"
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_smart_list\",\"line\":\"query_latest_release\",\"path\":[\"rows\",{\"path_element_type\":\"current_item\"},\"releaseKey\"]}')}"
```

Output is under `rows` — an array of objects matching `result_schema_json`.

---

## Validation Checklist

- [ ] Config includes `workato_smart_list` with `account_id: null`
- [ ] `create_list`/`insert_rows` provide `list_source` (an array datapill), `list_name`, and `primary_index`
- [ ] `insert_rows` sets `create_table_if_not_exist: "true"` when the list may not already exist
- [ ] `query_list`'s `sql` references column names and the table name via `["columns", "<col>"]`/`["list_name"]` datapills from the creating step, not hardcoded strings
- [ ] `query_list`'s `result_schema_json` matches the actual `SELECT` column list
- [ ] Query results are read via `["rows"]`, not a bare top-level array

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

---

## Related Documentation

- [Variables and Lists](variables-and-lists.md) — the simpler `workato_variable`/`declare_list` alternative for plain accumulate-and-iterate needs
- [Python Snippets](python-snippets.md) — an alternative for complex transforms that don't map cleanly to SQL
