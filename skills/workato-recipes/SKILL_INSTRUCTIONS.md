# Workato Recipes Base Skill - Agent Instructions

This document provides foundational knowledge for AI agents to generate valid Workato recipe JSON. This is the base skill that connector-specific skills (stripe-recipes, salesforce-recipes, etc.) extend.

---

## Table of Contents

1. [Recipe JSON Structure](#recipe-json-structure)
2. [Trigger Types](#trigger-types)
3. [Config Section](#config-section)
4. [Control Flow](#control-flow)
5. [Datapill Syntax](#datapill-syntax)
6. [Block Requirements](#block-requirements)

---

## Recipe JSON Structure

### Top-Level Structure

Every Workato recipe has this structure:

```json
{
  "name": "Recipe Name",
  "version": 1,
  "private": true,
  "concurrency": 1,
  "config": [
    // Connection/provider configurations
  ],
  "code": {
    // Trigger block with nested action blocks
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Recipe display name |
| `version` | integer | Recipe version number |
| `private` | boolean | Whether recipe is private to workspace |
| `concurrency` | integer | Max concurrent executions (typically 1) |
| `config` | array | Provider/connection configurations |
| `code` | object | Trigger and action blocks |

---

## Trigger Types

Workato supports multiple trigger types. Choose based on how the recipe will be invoked.

### API Endpoint Trigger

**Use when:** Recipe should be callable via external HTTP request.

**Provider:** `workato_api_platform`
**Action:** `receive_request`

```json
{
  "provider": "workato_api_platform",
  "name": "receive_request",
  "as": "api_trigger",
  "keyword": "trigger",
  "input": {
    "request": {
      "content_type": "json",
      "schema": "[{\"name\":\"email\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Email\",\"optional\":false},{\"name\":\"name\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Name\",\"optional\":false}]"
    },
    "response": {
      "content_type": "json",
      "responses": [
        {
          "name": "Success",
          "http_status_code": "200",
          "body_schema": "[{\"name\":\"id\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"ID\"},{\"name\":\"success\",\"type\":\"boolean\",\"control_type\":\"checkbox\",\"label\":\"Success\"}]"
        },
        {
          "name": "Error",
          "http_status_code": "400",
          "body_schema": "[{\"name\":\"error\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Error message\"}]"
        }
      ]
    }
  },
  "extended_output_schema": [
    {
      "label": "Request",
      "name": "request",
      "type": "object",
      "properties": [
        {
          "control_type": "text",
          "label": "Email",
          "name": "email",
          "type": "string",
          "optional": false
        },
        {
          "control_type": "text",
          "label": "Name",
          "name": "name",
          "type": "string",
          "optional": false
        }
      ]
    }
  ]
}
```

**CRITICAL: Request Schema Format**
- Use `request.schema` (NOT `body_schema` or `path_params`)
- Fields are accessed directly: `["request", "field_name"]` (NOT `["request", "body", "field_name"]`)
- The `extended_output_schema` must have fields directly under `request.properties`

**Datapill access example:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"email\"]}')}"
```

See: [triggers/api-endpoint.md](triggers/api-endpoint.md)

### Callable Recipe Trigger

**Use when:** Recipe should be called by other Workato recipes (internal).

**Provider:** `workato_recipe_function`
**Action:** `execute`

```json
{
  "provider": "workato_recipe_function",
  "name": "execute",
  "keyword": "trigger",
  "input": {
    "parameters_schema_json": "[...]",  // Input parameters
    "result_schema_json": "[...]"       // Return values
  }
}
```

See: [triggers/callable-recipe.md](triggers/callable-recipe.md)

### Calling Other Recipes (workato_recipe_function)

When a recipe needs to call another callable recipe, use the `workato_recipe_function` provider with action type `call`.

#### CRITICAL: flow_id Requires zip_name

The `flow_id` object MUST include ALL fields, including `zip_name`.

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Recipe display name |
| `folder` | Yes | Folder containing the recipe |
| `folder_full_path` | Yes | Full path from Home |
| `zip_name` | **YES** | Path to recipe JSON file |

> **⛔ CRITICAL WARNING:** Missing `zip_name` causes **RECIPE MUTATION AT RUNTIME**. Without `zip_name`, Workato will unpredictably modify the recipe's metadata during execution. This corruption persists and breaks all future invocations. The recipe will appear valid during import/testing but will corrupt itself when actually invoked. **This is worse than a silent failure - it permanently corrupts the recipe.**

**WRONG (missing zip_name - WILL CORRUPT THE RECIPE):**
```json
"flow_id": {
  "name": "Search contact by email",
  "folder": "atomic-salesforce-recipes",
  "folder_full_path": "Home/atomic-salesforce-recipes"
}
```

**CORRECT (includes zip_name):**
```json
"flow_id": {
  "name": "Search contact by email",
  "folder": "atomic-salesforce-recipes",
  "folder_full_path": "Home/atomic-salesforce-recipes",
  "zip_name": "atomic-salesforce-recipes/search_contact_by_email.recipe.json"
}
```

**Complete call action example:**
```json
{
  "provider": "workato_recipe_function",
  "name": "call",
  "as": "call_search_contact",
  "keyword": "action",
  "input": {
    "flow_id": {
      "name": "Search contact by email",
      "folder": "atomic-salesforce-recipes",
      "folder_full_path": "Home/atomic-salesforce-recipes",
      "zip_name": "atomic-salesforce-recipes/search_contact_by_email.recipe.json"
    },
    "parameters": {
      "email": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"email\"]}')}"
    }
  }
}
```

### Choosing a Trigger Type

| Scenario | Trigger Type |
|----------|--------------|
| External API access needed | API Endpoint |
| Called by other recipes only | Callable Recipe |
| Receive external webhooks | Webhook |
| Time-based execution | Scheduler |

---

## Response Actions

Workato provides different actions for returning data based on the trigger type.

### API Endpoint Response Action

**Use when:** Recipe uses `workato_api_platform` trigger and needs to return HTTP response.

**Provider:** `workato_api_platform`
**Action:** `return_response`

```json
{
  "provider": "workato_api_platform",
  "name": "return_response",
  "as": "return_success",
  "keyword": "action",
  "toggleCfg": {
    "response.success": true
  },
  "input": {
    "http_status_code": "200",
    "response": {
      "id": "#{datapill}",
      "success": "true"
    }
  },
  "extended_output_schema": [
    {
      "change_on_blur": true,
      "control_type": "select",
      "extends_schema": true,
      "label": "Response",
      "name": "http_status_code",
      "pick_list": [
        ["Success", "200"],
        ["Error", "400"]
      ],
      "type": "string"
    },
    {
      "label": "Response body",
      "name": "response",
      "properties": [
        {
          "control_type": "text",
          "label": "ID",
          "name": "id",
          "type": "string"
        },
        {
          "control_type": "checkbox",
          "label": "Success",
          "render_input": "boolean_conversion",
          "parse_output": "boolean_conversion",
          "name": "success",
          "type": "boolean",
          "toggle_hint": "Select from option list",
          "toggle_field": {
            "label": "Success",
            "control_type": "text",
            "toggle_hint": "Use custom value",
            "name": "success",
            "type": "boolean"
          }
        }
      ],
      "type": "object"
    }
  ],
  "extended_input_schema": [
    {
      "change_on_blur": true,
      "control_type": "select",
      "extends_schema": true,
      "label": "Response",
      "name": "http_status_code",
      "pick_list": [
        ["Success", "200"],
        ["Error", "400"]
      ],
      "type": "string"
    },
    {
      "label": "Response body",
      "name": "response",
      "properties": [
        {
          "control_type": "text",
          "label": "ID",
          "name": "id",
          "type": "string"
        },
        {
          "control_type": "checkbox",
          "label": "Success",
          "render_input": "boolean_conversion",
          "parse_output": "boolean_conversion",
          "name": "success",
          "type": "boolean",
          "toggle_hint": "Select from option list",
          "toggle_field": {
            "label": "Success",
            "control_type": "text",
            "toggle_hint": "Use custom value",
            "name": "success",
            "type": "boolean"
          }
        }
      ],
      "type": "object"
    }
  ],
  "uuid": "return-success-001"
}
```

**CRITICAL fields:**
- `http_status_code` - HTTP status code (200, 400, 500, etc.)
- `response` - Response body matching the schema defined in trigger
- `extended_input_schema.http_status_code.pick_list` - Must map response names from trigger to status codes
- `extended_input_schema.http_status_code.extends_schema: true` - Required flag
- `extended_input_schema.http_status_code.change_on_blur: true` - Required flag
- `extended_output_schema` - Must mirror `extended_input_schema`
- `toggleCfg` - Optional, for boolean toggle fields

**Common pattern:**
- Success responses: `http_status_code: "200"` or `"201"`
- Error responses: `http_status_code: "400"`, `"409"`, or `"500"`
- The `pick_list` MUST match the response names defined in the trigger's `response.responses` array

### Callable Recipe Response Action

**Use when:** Recipe uses `workato_recipe_function` trigger and needs to return data.

**Provider:** `workato_recipe_function`
**Action:** `return_result`

```json
{
  "provider": "workato_recipe_function",
  "name": "return_result",
  "as": "return_result",
  "keyword": "action",
  "input": {
    "result": {
      "id": "#{datapill}",
      "success": "true"
    }
  },
  "extended_output_schema": [
    {
      "label": "Result",
      "name": "result",
      "properties": [
        {
          "control_type": "text",
          "label": "ID",
          "name": "id",
          "type": "string"
        },
        {
          "control_type": "checkbox",
          "label": "Success",
          "name": "success",
          "type": "boolean"
        }
      ],
      "type": "object"
    }
  ],
  "extended_input_schema": [
    {
      "label": "Result",
      "name": "result",
      "properties": [
        {
          "control_type": "text",
          "label": "ID",
          "name": "id",
          "type": "string"
        },
        {
          "control_type": "checkbox",
          "label": "Success",
          "name": "success",
          "type": "boolean"
        }
      ],
      "type": "object"
    }
  ],
  "uuid": "return-result-001"
}
```

**Key fields:**
- `result` - Result object matching the schema defined in trigger's `result_schema_json`

---

## Config Section

The config section defines which providers/connections the recipe uses.

### Structure

```json
"config": [
  {
    "keyword": "application",
    "provider": "PROVIDER_NAME",
    "skip_validation": false,
    "account_id": null | { connection_reference }
  }
]
```

### Provider Types

**Platform providers** (no connection needed):
- `workato_api_platform` - API endpoint triggers
- `workato_recipe_function` - Callable recipe triggers
- `logger` - Logging actions

**Connector providers** (connection required):
- `stripe` - Stripe connector
- `salesforce` - Salesforce connector
- etc.

### Connection Reference Format

```json
"account_id": {
  "zip_name": "Workspace Connections/connection_name.connection.json",
  "name": "Connection Display Name",
  "folder": "Workspace Connections"
}
```

### Config Rules

1. Include a provider entry for EACH provider used in the recipe
2. Platform providers use `"account_id": null`
3. Connector providers require connection references
4. Do NOT include `"workato"` or `"catch"` as providers in config

---

## Control Flow

### If/Else Structure

**CRITICAL:** Else blocks are nested INSIDE the if block's array, NOT as a property.

```json
{
  "number": 3,
  "keyword": "if",
  "as": "check_condition",
  "input": {
    "type": "compound",
    "operand": "and",
    "conditions": [
      {
        "operand": "present",
        "lhs": "#{datapill}",
        "uuid": "condition-uuid"
      }
    ]
  },
  "block": [
    {
      // Action if condition is TRUE
      "number": 4,
      "keyword": "action",
      ...
    },
    {
      // ELSE block is a sibling in the block array
      "number": 5,
      "keyword": "else",
      "as": "else_branch",
      "input": {},
      "block": [
        {
          // Action if condition is FALSE
          "number": 6,
          "keyword": "action",
          ...
        }
      ],
      "uuid": "else-uuid"
    }
  ],
  "uuid": "if-uuid"
}
```

### Try/Catch Structure

```json
{
  "number": 1,
  "keyword": "try",
  "input": {},
  "block": [
    {
      // Actions that might fail
      "number": 2,
      "keyword": "action",
      ...
    },
    {
      // Catch block is INSIDE try block
      "number": 3,
      "keyword": "catch",
      "provider": null,
      "as": "catch_error",
      "input": {
        "max_retry_count": "0",
        "retry_interval": "2"
      },
      "block": [
        {
          // Error handling actions
        }
      ],
      "uuid": "catch-uuid"
    }
  ],
  "uuid": "try-uuid"
}
```

### Condition Operands

| Operand | Description |
|---------|-------------|
| `present` | Value exists and is not empty |
| `blank` | Value is null or empty |
| `equals` | LHS equals RHS |
| `not_equals` | LHS does not equal RHS |
| `greater_than` | LHS > RHS |
| `less_than` | LHS < RHS |
| `contains` | LHS contains RHS |

---

## Datapill Syntax

Datapills reference data from previous steps.

### Format

```
#{_dp('{JSON_OBJECT}')}
```

### JSON Object Structure

```json
{
  "pill_type": "output",
  "provider": "PROVIDER_NAME",
  "line": "STEP_ALIAS",
  "path": ["field", "nested_field"]
}
```

### Examples

**Trigger parameter (callable recipe):**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"email\"]}')}"
```

**Trigger parameter (API endpoint):**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"STEP_ALIAS\",\"path\":[\"request\",\"body\",\"email\"]}')}"
```

**Action output:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"id\"]}')}"
```

**Array element access:**
```json
"path": ["data", {"path_element_type": "current_item"}, "id"]
```

**Catch block error:**
```json
{
  "provider": "catch",
  "line": "catch_error",
  "path": ["message"]
}
```

---

## Block Requirements

Every block in a recipe requires these fields:

| Field | Required | Description |
|-------|----------|-------------|
| `number` | Yes | Sequential step number |
| `keyword` | Yes | Block type: `trigger`, `action`, `if`, `else`, `try`, `catch` |
| `uuid` | Yes | Unique identifier (max 36 chars) |
| `as` | Yes* | Step alias for datapill references |

*Required for all blocks except some control flow

### Provider Field Rules

| Block Type | Provider |
|------------|----------|
| Trigger | Required (e.g., `workato_api_platform`) |
| Action | Required (e.g., `stripe`, `salesforce`) |
| If/Else | NO provider field |
| Catch | `"provider": null` (explicitly null) |

### UUID Guidelines

- Must be unique within the recipe
- **Max 36 characters** (platform will reject recipe if exceeded)
- Use descriptive names: `"search-customer-001"`, `"return-success-001"`

> **WARNING:** UUIDs longer than 36 characters will cause the recipe to be rejected during import. Keep names concise.

---

## Extended Schemas

Actions that return or accept complex data need extended schemas.

### CRITICAL: Schema Completeness Requirement

> **WARNING:** The `extended_input_schema` MUST fully define ALL fields in the action's `input` object, including nested objects. If any input field is missing from the schema, **Workato will silently drop that data during execution**, causing cascading failures.

This is a Workato platform behavior that affects ALL connectors. Complex connectors (Salesforce, NetSuite, etc.) are particularly vulnerable due to deeply nested input structures.

**Symptoms of incomplete schemas:**
- Input data silently dropped (no error, just missing)
- API calls missing required parameters
- Downstream steps fail due to missing data
- Difficult to debug because the recipe structure looks correct

**Agent requirement:** When generating recipes with custom actions or complex inputs, ALWAYS verify that `extended_input_schema` mirrors the complete `input` structure.

### extended_output_schema

Defines the output fields available from an action:

```json
"extended_output_schema": [
  {
    "label": "Customer ID",
    "name": "id",
    "type": "string",
    "control_type": "text"
  }
]
```

### extended_input_schema

Defines the input fields for an action. **Must mirror the `input` structure exactly.**

**Simple flat input:**
```json
"input": {
  "email": "test@example.com"
}

"extended_input_schema": [
  {
    "label": "Email",
    "name": "email",
    "type": "string",
    "control_type": "text",
    "optional": false
  }
]
```

**Nested input (e.g., custom HTTP actions):**
```json
"input": {
  "path": "/v1/customers/search",
  "verb": "get",
  "input": {
    "schema": "[...]",
    "data": {
      "query": "email:'test@example.com'",
      "limit": "1"
    }
  }
}

"extended_input_schema": [
  {
    "label": "Path",
    "name": "path",
    "type": "string",
    "control_type": "text"
  },
  {
    "label": "Verb",
    "name": "verb",
    "type": "string",
    "control_type": "select"
  },
  {
    "label": "Request URL parameters",
    "name": "input",
    "type": "object",
    "properties": [
      {
        "label": "Schema",
        "name": "schema",
        "type": "string",
        "control_type": "text"
      },
      {
        "label": "Data",
        "name": "data",
        "type": "object",
        "properties": [
          {
            "label": "Query",
            "name": "query",
            "type": "string",
            "control_type": "text"
          },
          {
            "label": "Limit",
            "name": "limit",
            "type": "string",
            "control_type": "text"
          }
        ]
      }
    ]
  }
]
```

### Schema Validation Checklist

Before finalizing any action block, verify:

- [ ] Every field in `input` has a corresponding entry in `extended_input_schema`
- [ ] Nested objects in `input` have matching nested `properties` in the schema
- [ ] Field names match exactly between `input` and schema
- [ ] For custom HTTP actions, the nested `input.data` object is fully defined

---

## Formula Syntax

Workato supports Ruby-based formulas for dynamic values and conditional logic.

### Formula Prefix

Formulas are prefixed with `=`:

```json
"input": {
  "field_name": "=formula_expression"
}
```

### Conditional Field Updates (Ternary Operator)

Use `.present?` checks with ternary operator to conditionally set fields:

```json
"FirstName": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"first_name\"]}').present? ? _dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"first_name\"]}') : skip"
```

**Pattern:**
```
=datapill.present? ? datapill : skip
```

- `present?` - Checks if value exists and is not empty
- `? value : skip` - If present, use value; otherwise, skip the field
- `skip` - Special keyword to exclude field from the action

### Common Formula Methods

| Method | Description | Example |
|--------|-------------|---------|
| `present?` | Value exists and not empty | `=field.present?` |
| `blank?` | Value is null or empty | `=field.blank?` |
| `upcase` | Convert to uppercase | `=field.upcase` |
| `downcase` | Convert to lowercase | `=field.downcase` |
| `strip` | Remove whitespace | `=field.strip` |

### Formula Examples

**Conditional assignment:**
```json
"Email": "=_dp('{...email...}').present? ? _dp('{...email...}') : skip"
```

**String transformation:**
```json
"Status": "=_dp('{...status...}').upcase"
```

**Null assignment:**
```json
"field_name": "=null"
```

### String Concatenation

When concatenating strings from multiple datapills, use formula mode (`=` prefix) with Ruby `+` operator.

**WRONG (mixing `#{}` interpolation with concatenation - INVALID):**
```json
"guest_name": "#{_dp('{...first_name...}')} + ' ' + _dp('{...last_name...}'}"
```

**CORRECT (use `=` prefix, no `#{}` wrapper):**
```json
"guest_name": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"first_name\"]}') + ' ' + _dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"last_name\"]}')"
```

**Pattern:**
```
"field": "=_dp('{...pill1...}') + ' ' + _dp('{...pill2...}')"
```

**Key rules:**
- Use `=` prefix (formula mode) for concatenation
- Do NOT wrap with `#{}`
- Use Ruby `+` operator between strings
- Literal strings must be quoted: `' '` or `'-'`

### Conditional Defaults

Provide a default value when an optional parameter is missing using `.present?` with ternary operator:

**Pattern:**
```json
"field": "=_dp('{...}').present? ? _dp('{...}') : 'default_value'"
```

**Example (default status to 'Reserved' when not provided):**
```json
"Status__c": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"status\"]}').present? ? _dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"status\"]}') : 'Reserved'"
```

**Key points:**
- `.present?` checks if value exists and is not empty
- The datapill must appear twice (once for check, once for value)
- Default value must be quoted if it's a string

---

## References

- **Triggers:** See `triggers/` directory for detailed trigger documentation
- **Control Flow:** See `control-flow/` directory for pattern details
- **Templates:** See `templates/` directory for starter templates
