# Variables and Lists

This pattern covers using the `workato_variable` provider for declaring and managing variables and lists within recipes.

---

## Provider Overview

Workato provides two similar-sounding providers for variables:

| Provider | Config Required | Recommended |
|----------|-----------------|-------------|
| `workato` | No (built-in) | **No** - datapill references may not resolve |
| `workato_variable` | Yes | **Yes** - proper variable/list pattern |

> **CRITICAL:** The built-in `workato` provider's `set_variable` action has a known limitation: datapill references to its output often fail to resolve in downstream actions. Use `workato_variable` instead.

---

## When to Use Variables

### Use Ternary Syntax (2 sources)

When a value could come from **2 possible sources** (e.g., search result OR create result), use Ruby ternary syntax directly:

```json
"field_value": "=(_dp('{...search...}').present? ? _dp('{...search...}') : _dp('{...create...}'))"
```

See [datapill-syntax.md](../fundamentals/datapill-syntax.md) for ternary syntax details.

### Use `workato_variable` (3+ sources)

When you need to consolidate values from **3 or more sources**, or need to accumulate values in a loop, use the `workato_variable` provider.

---

## Config Entry

The `workato_variable` provider requires a config entry:

```json
{
  "keyword": "application",
  "provider": "workato_variable",
  "skip_validation": false,
  "account_id": null
}
```

> **Note:** Unlike external connectors, `workato_variable` uses `"account_id": null` because it doesn't require authentication.

---

## Variable Actions

### Declare Variable

Initialize a variable with a starting value:

```json
{
  "number": 1,
  "provider": "workato_variable",
  "name": "declare_variable",
  "as": "declare_customer_id",
  "keyword": "action",
  "input": {
    "variable_name": "customer_id",
    "variable_type": "string",
    "variable_value": ""
  },
  "uuid": "declare-customer-id-001"
}
```

#### Variable Types

| Type | Description |
|------|-------------|
| `string` | Text value |
| `integer` | Whole number |
| `number` | Decimal number |
| `boolean` | true/false |
| `date` | Date value |
| `datetime` | Date and time |

### Update Variable

Set or update a variable's value:

```json
{
  "number": 3,
  "provider": "workato_variable",
  "name": "update_variables",
  "as": "set_customer_id",
  "keyword": "action",
  "input": {
    "variables": [
      {
        "variable": "customer_id",
        "value": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"id\"]}')}"
      }
    ]
  },
  "uuid": "set-customer-id-001"
}
```

### Reference Variable in Datapill

Reference format: `{uuid}:{as}:{variable_name}`

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_customer_id\",\"path\":[\"value\"]}')}"
```

---

## List Actions

### Declare List

Initialize an empty list:

```json
{
  "number": 1,
  "provider": "workato_variable",
  "name": "declare_list",
  "as": "declare_results_list",
  "keyword": "action",
  "input": {
    "list_name": "results",
    "list_schema": "[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"status\",\"type\":\"string\"}]"
  },
  "uuid": "declare-results-list-001"
}
```

### Insert to List

Add a single item to a list:

```json
{
  "number": 3,
  "provider": "workato_variable",
  "name": "insert_to_list",
  "as": "add_result",
  "keyword": "action",
  "input": {
    "list_name": "results",
    "list_item": {
      "id": "#{_dp('{...}')}",
      "status": "success"
    }
  },
  "uuid": "add-result-001"
}
```

### Insert Batch to List

Add multiple items at once:

```json
{
  "number": 3,
  "provider": "workato_variable",
  "name": "insert_to_list_batch",
  "as": "add_results_batch",
  "keyword": "action",
  "input": {
    "list_name": "results",
    "list_items": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_contacts\",\"path\":[\"records\"]}')}"
  },
  "uuid": "add-results-batch-001"
}
```

### Reference List in Datapill

Reference format: `{uuid}:{as}` (no variable name for lists)

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_results_list\",\"path\":[\"list\"]}')}"
```

---

## Complete Example: Conditional Value Assignment

This example shows using a variable to capture a customer ID from either a search or create action:

```json
{
  "name": "Find or Create Customer",
  "version": 1,
  "private": true,
  "concurrency": 1,
  "config": [
    {
      "keyword": "application",
      "provider": "workato_recipe_function",
      "skip_validation": false,
      "account_id": null
    },
    {
      "keyword": "application",
      "provider": "workato_variable",
      "skip_validation": false,
      "account_id": null
    },
    {
      "keyword": "application",
      "provider": "stripe",
      "skip_validation": false,
      "account_id": {
        "zip_name": "stripe_connection.connection.json",
        "name": "Stripe Connection",
        "folder": ""
      }
    }
  ],
  "code": {
    "number": 0,
    "keyword": "trigger",
    "provider": "workato_recipe_function",
    "name": "execute",
    "as": "trigger",
    "input": { "..." : "..." },
    "block": [
      {
        "number": 1,
        "provider": "workato_variable",
        "name": "declare_variable",
        "as": "declare_customer_id",
        "keyword": "action",
        "input": {
          "variable_name": "customer_id",
          "variable_type": "string",
          "variable_value": ""
        },
        "uuid": "declare-customer-id-001"
      },
      {
        "number": 2,
        "provider": "stripe",
        "name": "search_customers",
        "as": "search_customer",
        "keyword": "action",
        "input": { "..." : "..." },
        "uuid": "search-customer-001"
      },
      {
        "number": 3,
        "keyword": "if",
        "input": {
          "type": "compound",
          "operand": "and",
          "conditions": [
            {
              "operand": "present",
              "lhs": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"search_customer\",\"path\":[\"data\",{\"path_element_type\":\"current_item\"},\"id\"]}')}",
              "rhs": ""
            }
          ]
        },
        "block": [
          {
            "number": 4,
            "provider": "workato_variable",
            "name": "update_variables",
            "as": "set_found_id",
            "keyword": "action",
            "input": {
              "variables": [
                {
                  "variable": "customer_id",
                  "value": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"search_customer\",\"path\":[\"data\",{\"path_element_type\":\"current_item\"},\"id\"]}')}"
                }
              ]
            },
            "uuid": "set-found-id-001"
          },
          {
            "number": 5,
            "keyword": "else",
            "block": [
              {
                "number": 6,
                "provider": "stripe",
                "name": "create_customer",
                "as": "create_customer",
                "keyword": "action",
                "input": { "..." : "..." },
                "uuid": "create-customer-001"
              },
              {
                "number": 7,
                "provider": "workato_variable",
                "name": "update_variables",
                "as": "set_created_id",
                "keyword": "action",
                "input": {
                  "variables": [
                    {
                      "variable": "customer_id",
                      "value": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"id\"]}')}"
                    }
                  ]
                },
                "uuid": "set-created-id-001"
              }
            ],
            "uuid": "else-001"
          }
        ],
        "uuid": "if-customer-found-001"
      },
      {
        "number": 8,
        "provider": "workato_recipe_function",
        "name": "return_result",
        "as": "return_result",
        "keyword": "action",
        "input": {
          "result": {
            "customer_id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_customer_id\",\"path\":[\"value\"]}')}"
          }
        },
        "uuid": "return-result-001"
      }
    ],
    "uuid": "trigger-001"
  }
}
```

---

## Gotchas and Best Practices

1. **Avoid `workato` provider**: The built-in `workato` provider's `set_variable` action has unreliable datapill resolution. Always use `workato_variable` instead.

2. **Prefer ternary for 2 sources**: When choosing between just 2 possible values, ternary syntax is simpler and doesn't require config entries.

3. **Declare before use**: Always declare variables/lists before any action that might update them.

4. **Variable scope**: Variables are scoped to the recipe execution. They persist across all actions within a single run.

5. **List schema**: When declaring lists, the `list_schema` must define the structure of items that will be inserted.

---

## Related Documentation

- [Config Section](../fundamentals/config-section.md)
- [Datapill Syntax](../fundamentals/datapill-syntax.md) - Ternary syntax for 2 sources
- [Foreach Loops](../control-flow/foreach.md) - Using lists with iteration
