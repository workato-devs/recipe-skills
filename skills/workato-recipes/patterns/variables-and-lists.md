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

Initialize a variable with a starting value. Uses `variables.schema` (stringified JSON defining the field) and `variables.data.{field_name}` for the value:

```json
{
  "number": 1,
  "provider": "workato_variable",
  "name": "declare_variable",
  "as": "declare_customer_id",
  "keyword": "action",
  "input": {
    "variables": {
      "schema": "[{\"name\":\"customer_id\",\"type\":\"string\",\"optional\":true,\"label\":\"customer_id\",\"details\":{\"real_name\":\"customer_id\"},\"control_type\":\"text\",\"parent\":[\"variables\",\"data\"]}]",
      "data": {
        "customer_id": ""
      }
    }
  },
  "extended_output_schema": [
    {
      "control_type": "text",
      "label": "customer_id",
      "name": "customer_id",
      "optional": true,
      "type": "string",
      "details": { "real_name": "customer_id" }
    }
  ],
  "extended_input_schema": [
    {
      "add_field_label": "Add a variable",
      "control_type": "form-schema-builder",
      "empty_schema_title": "Add variables by giving them a name, type and default value",
      "exclude_fields": ["hint"],
      "item_label": "variable",
      "label": "Variables",
      "mark_as_required": true,
      "name": "variables",
      "ngIf": "!input.name",
      "optional": true,
      "properties": [
        {
          "control_type": "text",
          "label": "Schema",
          "extends_schema": true,
          "broadcast_change_event": true,
          "type": "string",
          "name": "schema"
        },
        {
          "properties": [
            {
              "control_type": "text",
              "label": "customer_id",
              "name": "customer_id",
              "type": "string",
              "optional": true,
              "details": { "real_name": "customer_id" },
              "parent": ["variables", "data"],
              "hint": "Defaults to nil if not supplied.",
              "sticky": true
            }
          ],
          "label": "Data",
          "type": "object",
          "name": "data"
        }
      ],
      "type": "object"
    }
  ],
  "visible_config_fields": ["variables.data.customer_id"],
  "uuid": "declare-customer-id-001"
}
```

#### Key structural rules for `declare_variable`:

- **Input**: `variables.schema` is a stringified JSON array. Each field entry must have `"parent": ["variables", "data"]`
- **Input**: `variables.data.{field_name}` holds the default value (string, datapill, or formula)
- **EIS**: Uses `"control_type": "form-schema-builder"` with a `schema` property and a `data` property containing the field definitions
- **EOS**: Defines the output field using the **field name** (e.g., `"name": "customer_id"`), NOT `"value"`
- **`visible_config_fields`**: Array of `"variables.data.{field_name}"` entries

#### Variable Types

| Type | `control_type` | Description |
|------|----------------|-------------|
| `string` | `text` | Text value |
| `integer` | `number` | Whole number |
| `number` | `number` | Decimal number |
| `boolean` | `checkbox` | true/false |
| `date` | `date` | Date value |
| `datetime` | `date_time` | Date and time |

### Update Variable

Set or update a variable's value. **Use the "raw" input form** — this is what the Workato server normalizes to internally and what survives a push/pull round-trip:

```json
{
  "number": 3,
  "provider": "workato_variable",
  "name": "update_variables",
  "as": "set_customer_id",
  "keyword": "action",
  "input": {
    "input_mode": "raw",
    "name": "declare-customer-id-001:declare_customer_id:customer_id",
    "customer_id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"id\"]}')}"
  },
  "uuid": "set-customer-id-001"
}
```

#### Key structural rules for `update_variables` (raw form):

- **`input_mode`**: must be the literal string `"raw"`.
- **`name`**: `\n`-separated entries, one per variable being updated. Each entry has the form `<declare-uuid>:<declare-as>:<variable-name>`, pointing at the `declare_variable` step that owns the variable.
- **Per-variable values**: each variable is a flat top-level key on `input` (e.g., `customer_id`, `order_id`). The value is a datapill, formula, or literal.

For multiple variables in a single update:

```json
"input": {
  "input_mode": "raw",
  "name": "declare-vars-001:declare_vars:customer_id\ndeclare-vars-001:declare_vars:order_id",
  "customer_id": "#{_dp('{...}')}",
  "order_id": "#{_dp('{...}')}"
}
```

> **WARNING:** An older structured form — `"variables": [{"variable": "...", "value": "..."}]` — appears in some examples and parses as valid JSON, but **the Workato importer silently drops it on round-trip**. The recipe pushes, lint passes, but every variable mapping comes back empty after import. Use the raw form above.

### Reference Variable in Datapill

Datapill path uses the **field name**, NOT `["value"]`:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_customer_id\",\"path\":[\"customer_id\"]}')}"
```

---

## List Actions

### Declare List

Initialize a named list with a schema defining each item's structure. Uses `name` for the list name and `list_item_schema_json` for the stringified item schema:

```json
{
  "number": 1,
  "provider": "workato_variable",
  "name": "declare_list",
  "as": "declare_results_list",
  "keyword": "action",
  "input": {
    "name": "results",
    "list_item_schema_json": "[{\"control_type\":\"text\",\"label\":\"Id\",\"type\":\"string\",\"name\":\"id\",\"optional\":true},{\"control_type\":\"text\",\"label\":\"Status\",\"type\":\"string\",\"name\":\"status\",\"optional\":true}]"
  },
  "extended_output_schema": [
    {
      "label": "results",
      "name": "list_items",
      "of": "object",
      "optional": false,
      "properties": [
        { "control_type": "text", "label": "Id", "type": "string", "name": "id", "optional": true },
        { "control_type": "text", "label": "Status", "type": "string", "name": "status", "optional": true }
      ],
      "type": "array"
    }
  ],
  "extended_input_schema": [
    {
      "hint": "Set the initial items in the list. Defaults to an empty list if not supplied.",
      "label": "Items",
      "name": "list_items",
      "of": "object",
      "optional": true,
      "properties": [
        { "control_type": "text", "label": "Id", "type": "string", "name": "id", "optional": true },
        { "control_type": "text", "label": "Status", "type": "string", "name": "status", "optional": true }
      ],
      "type": "array"
    }
  ],
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

Lists output via the `list_items` path:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_results_list\",\"path\":[\"list_items\"]}')}"
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
          "variables": {
            "schema": "[{\"name\":\"customer_id\",\"type\":\"string\",\"optional\":true,\"label\":\"customer_id\",\"details\":{\"real_name\":\"customer_id\"},\"control_type\":\"text\",\"parent\":[\"variables\",\"data\"]}]",
            "data": {
              "customer_id": ""
            }
          }
        },
        "extended_output_schema": [
          {
            "control_type": "text",
            "label": "customer_id",
            "name": "customer_id",
            "optional": true,
            "type": "string",
            "details": { "real_name": "customer_id" }
          }
        ],
        "extended_input_schema": [
          {
            "add_field_label": "Add a variable",
            "control_type": "form-schema-builder",
            "empty_schema_title": "Add variables by giving them a name, type and default value",
            "exclude_fields": ["hint"],
            "item_label": "variable",
            "label": "Variables",
            "mark_as_required": true,
            "name": "variables",
            "ngIf": "!input.name",
            "optional": true,
            "properties": [
              {
                "control_type": "text",
                "label": "Schema",
                "extends_schema": true,
                "broadcast_change_event": true,
                "type": "string",
                "name": "schema"
              },
              {
                "properties": [
                  {
                    "control_type": "text",
                    "label": "customer_id",
                    "name": "customer_id",
                    "type": "string",
                    "optional": true,
                    "details": { "real_name": "customer_id" },
                    "parent": ["variables", "data"],
                    "hint": "Defaults to nil if not supplied.",
                    "sticky": true
                  }
                ],
                "label": "Data",
                "type": "object",
                "name": "data"
              }
            ],
            "type": "object"
          }
        ],
        "visible_config_fields": ["variables.data.customer_id"],
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
        "as": "check_customer_found",
        "input": {
          "type": "compound",
          "operand": "and",
          "conditions": [
            {
              "operand": "present",
              "lhs": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"search_customer\",\"path\":[\"data\",{\"path_element_type\":\"current_item\"},\"id\"]}')}",
              "uuid": "cond-customer-present"
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
              "input_mode": "raw",
              "name": "declare-customer-id-001:declare_customer_id:customer_id",
              "customer_id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"search_customer\",\"path\":[\"data\",{\"path_element_type\":\"current_item\"},\"id\"]}')}"
            },
            "uuid": "set-found-id-001"
          },
          {
            "number": 5,
            "keyword": "else",
            "as": "else_create_customer",
            "input": {},
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
                  "input_mode": "raw",
                  "name": "declare-customer-id-001:declare_customer_id:customer_id",
                  "customer_id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"id\"]}')}"
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
            "customer_id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_variable\",\"line\":\"declare_customer_id\",\"path\":[\"customer_id\"]}')}"
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

1. **`workato`/`set_variable` is NOT recognized**: The built-in `workato` provider's `set_variable` action causes "select app and action" in the Workato UI. Always use `workato_variable`/`declare_variable` instead.

2. **Datapill path uses field name, NOT `["value"]`**: When referencing a variable's output, the `path` in the datapill uses the field name (e.g., `["customer_id"]`), not `["value"]`.

3. **Prefer ternary for 2 sources**: When choosing between just 2 possible values, ternary syntax is simpler and doesn't require config entries.

4. **Declare before use**: Always declare variables/lists before any action that might update them.

5. **Variable scope**: Variables are scoped to the recipe execution. They persist across all actions within a single run.

6. **EIS is required**: Without the `extended_input_schema` (with `form-schema-builder` control type), the variable action will not render correctly in the Workato UI.

7. **Schema field needs `parent`**: Each field in `variables.schema` must include `"parent": ["variables", "data"]` or the field won't bind to the data input.

8. **`update_variables` must use the raw input form**: The structured `variables: [{variable, value}]` array form is silently dropped by the Workato importer on round-trip. Use `input_mode: "raw"` with a `\n`-separated `name` field and flat per-variable top-level keys (see [Update Variable](#update-variable) above).

## Validation Checklist

- [ ] Variable actions use `workato_variable` provider (NOT `workato`)
- [ ] Variable actions use `declare_variable` (NOT `set_variable`)
- [ ] Input uses `variables.schema` (stringified JSON) + `variables.data.{field}` structure
- [ ] Schema entries have `"parent": ["variables", "data"]`
- [ ] EIS has `"control_type": "form-schema-builder"` with `schema` and `data` properties
- [ ] EOS field name matches the variable field name (NOT `"value"`)
- [ ] Datapill references use `"provider": "workato_variable"` and path uses the field name
- [ ] Config includes `workato_variable` entry with `"account_id": null`
- [ ] List actions use `name` + `list_item_schema_json` input (NOT `list_name` + `list_schema`)
- [ ] `update_variables` uses `input_mode: "raw"` with a `\n`-separated `name` field (NOT the structured `variables: [{variable, value}]` array form, which is silently dropped on import)

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

---

## Related Documentation

- [Config Section](../fundamentals/config-section.md)
- [Datapill Syntax](../fundamentals/datapill-syntax.md) - Ternary syntax for 2 sources
- [Foreach Loops](../control-flow/foreach.md) - Using lists with iteration
