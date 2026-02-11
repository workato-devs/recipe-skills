# Callable Recipe Trigger

Use the callable recipe trigger when your recipe should only be invoked by other Workato recipes (internal use).

## Provider Details

| Field | Value |
|-------|-------|
| Provider | `workato_recipe_function` |
| Action | `execute` |
| Config provider | `workato_recipe_function` with `account_id: null` |

## Complete Trigger Structure

```json
{
  "number": 0,
  "provider": "workato_recipe_function",
  "name": "execute",
  "as": "trigger",
  "keyword": "trigger",
  "input": {
    "parameters_schema_json": "[{\"name\":\"email\",\"label\":\"Email\",\"type\":\"string\",\"control_type\":\"text\",\"optional\":false,\"hint\":\"Customer email\"}]",
    "result_schema_json": "[{\"name\":\"customer_id\",\"label\":\"Customer ID\",\"type\":\"string\",\"control_type\":\"text\"},{\"name\":\"success\",\"label\":\"Success\",\"type\":\"boolean\",\"control_type\":\"checkbox\"}]"
  },
  "extended_output_schema": [
    {
      "label": "Parameters",
      "name": "parameters",
      "type": "object",
      "properties": [
        {
          "control_type": "text",
          "label": "Email",
          "name": "email",
          "type": "string",
          "optional": false,
          "hint": "Customer email"
        }
      ]
    }
  ],
  "block": [
    // Action blocks go here
  ],
  "uuid": "trigger-001"
}
```

## Input Parameters

Define input parameters in `parameters_schema_json`:

```json
"parameters_schema_json": "[{\"name\":\"email\",\"label\":\"Email\",\"type\":\"string\",\"control_type\":\"text\",\"optional\":false,\"hint\":\"Customer email address\"},{\"name\":\"name\",\"label\":\"Name\",\"type\":\"string\",\"control_type\":\"text\",\"optional\":false},{\"name\":\"phone\",\"label\":\"Phone\",\"type\":\"string\",\"control_type\":\"text\",\"optional\":true}]"
```

### Field Schema Properties

| Property | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Field identifier (used in datapills) |
| `label` | Yes | Display label |
| `type` | Yes | Data type: `string`, `integer`, `boolean`, `date_time`, `object`, `array` |
| `control_type` | Yes | UI control: `text`, `number`, `checkbox`, `select`, `date_time` |
| `optional` | Yes | Whether field is required |
| `hint` | No | Help text for the field |

## Result Schema

Define return values in `result_schema_json`:

```json
"result_schema_json": "[{\"name\":\"customer_id\",\"label\":\"Customer ID\",\"type\":\"string\",\"control_type\":\"text\"},{\"name\":\"created\",\"label\":\"Created\",\"type\":\"boolean\",\"control_type\":\"checkbox\"},{\"name\":\"error_message\",\"label\":\"Error Message\",\"type\":\"string\",\"control_type\":\"text\"}]"
```

**CRITICAL:** Every field in `result_schema_json` MUST be present in EVERY `return_result` action.

## Returning Results

Use the `return_result` action:

```json
{
  "number": 5,
  "provider": "workato_recipe_function",
  "name": "return_result",
  "as": "return_success",
  "keyword": "action",
  "toggleCfg": {
    "result.created": true
  },
  "input": {
    "result": {
      "customer_id": "#{_dp('...')}",
      "created": "true",
      "error_message": "=null"
    }
  },
  "extended_output_schema": [...],
  "extended_input_schema": [...],
  "uuid": "return-success-001"
}
```

### Return Value Rules

| Scenario | Value Format |
|----------|--------------|
| String with value | `"actual_value"` or `"#{datapill}"` |
| String null | `"=null"` |
| Boolean true | `"true"` |
| Boolean false | `"false"` |
| Integer | `"123"` (as string) |

## Accessing Input Parameters

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"email\"]}')}"
```

## Required Config Entry

```json
{
  "keyword": "application",
  "provider": "workato_recipe_function",
  "skip_validation": false,
  "account_id": null
}
```

## Extended Schemas on Return Blocks

Every `return_result` action needs matching extended schemas:

```json
"extended_output_schema": [
  {
    "label": "Result",
    "name": "result",
    "type": "object",
    "properties": [
      {
        "control_type": "text",
        "label": "Customer ID",
        "name": "customer_id",
        "type": "string"
      },
      {
        "control_type": "checkbox",
        "label": "Created",
        "name": "created",
        "type": "boolean",
        "render_input": "boolean_conversion",
        "parse_output": "boolean_conversion"
      }
    ]
  }
],
"extended_input_schema": [
  // Same structure as extended_output_schema
]
```

## Validation Checklist

- [ ] `result_schema_json` defines all expected return fields
- [ ] Every `return_result` action provides values for ALL fields in `result_schema_json`
- [ ] Catch blocks use `"=null"` for unavailable return fields (NOT empty string `""`)
- [ ] `parameters_schema_json` defines all expected input fields
- [ ] `extended_output_schema` wraps parameters under a `"parameters"` object
- [ ] Trigger `as` is `"trigger"` and input parameter datapills use `["parameters", "field_name"]` path

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

## Complete Example

See: [templates/callable-recipe-trigger.template.json](../templates/callable-recipe-trigger.template.json)
