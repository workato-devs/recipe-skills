# Workato Recipes Base Skill - Agent Instructions

This document provides foundational knowledge for AI agents to generate valid Workato recipe JSON. This is the base skill that connector-specific skills (stripe-recipes, salesforce-recipes, etc.) extend.

---

## Filename Convention

**Recipe filenames must match the recipe's `name` field**, converted to lowercase with spaces replaced by underscores. Workato normalizes filenames on pull, so mismatches cause filename changes.

| Recipe Name | Correct Filename |
|-------------|------------------|
| `"name": "Search Contact By Email"` | `search_contact_by_email.recipe.json` |
| `"name": "Create Stripe Customer"` | `create_stripe_customer.recipe.json` |
| `"name": "Handle Dialog Submit"` | `handle_dialog_submit.recipe.json` |

---

## Quick Reference

| Topic | Documentation |
|-------|---------------|
| Recipe Structure | [fundamentals/recipe-structure.md](fundamentals/recipe-structure.md) |
| Config Section | [fundamentals/config-section.md](fundamentals/config-section.md) |
| Datapill Syntax | [fundamentals/datapill-syntax.md](fundamentals/datapill-syntax.md) |
| Variables & Lists | [patterns/variables-and-lists.md](patterns/variables-and-lists.md) |
| If/Else | [control-flow/if-else.md](control-flow/if-else.md) |
| Try/Catch | [control-flow/try-catch.md](control-flow/try-catch.md) |
| Foreach Loops | [control-flow/foreach.md](control-flow/foreach.md) |
| API Endpoint Trigger | [triggers/api-endpoint.md](triggers/api-endpoint.md) |
| Callable Recipe Trigger | [triggers/callable-recipe.md](triggers/callable-recipe.md) |

---

## Table of Contents

1. [Trigger Types](#trigger-types)
2. [Calling Other Recipes](#calling-other-recipes)
3. [Response Actions](#response-actions)
4. [Block Requirements](#block-requirements)
5. [Extended Schemas](#extended-schemas)
6. [Formula Syntax](#formula-syntax)

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
      "schema": "[{\"name\":\"email\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Email\",\"optional\":false}]"
    },
    "response": {
      "content_type": "json",
      "responses": [
        {
          "name": "Success",
          "http_status_code": "200",
          "body_schema": "[{\"name\":\"success\",\"type\":\"boolean\",\"control_type\":\"checkbox\",\"label\":\"Success\"}]"
        }
      ]
    }
  }
}
```

**CRITICAL: Request Schema Format**
- Use `request.schema` (NOT `body_schema` or `path_params`)
- Fields are accessed directly: `["request", "field_name"]` (NOT `["request", "body", "field_name"]`)

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
    "parameters_schema_json": "[...]",
    "result_schema_json": "[...]"
  }
}
```

See: [triggers/callable-recipe.md](triggers/callable-recipe.md)

### Choosing a Trigger Type

| Scenario | Trigger Type |
|----------|--------------|
| External API access needed | API Endpoint |
| Called by other recipes only | Callable Recipe |
| Receive external webhooks | Webhook |
| Time-based execution | Scheduler |

---

## Calling Other Recipes

When a recipe needs to call another callable recipe, use the `workato_recipe_function` provider with action type `call`.

### CRITICAL: flow_id Requires zip_name

The `flow_id` object MUST include ALL fields, including `zip_name`.

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Recipe display name |
| `folder` | Yes | Folder containing the recipe |
| `folder_full_path` | Yes | Full path from Home |
| `zip_name` | **YES** | Path to recipe JSON file |

> **CRITICAL WARNING:** Missing `zip_name` causes **RECIPE MUTATION AT RUNTIME**. Without `zip_name`, Workato will unpredictably modify the recipe's metadata during execution. This corruption persists and breaks all future invocations. The recipe will appear valid during import/testing but will corrupt itself when actually invoked. **This is worse than a silent failure - it permanently corrupts the recipe.**

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

## Block Requirements

Every block in a recipe requires these fields:

| Field | Required | Description |
|-------|----------|-------------|
| `number` | Yes | Sequential step number |
| `keyword` | Yes | Block type: `trigger`, `action`, `if`, `else`, `try`, `catch`, `foreach` |
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

- **Fundamentals:** See `fundamentals/` directory for recipe structure, config, and datapill syntax
- **Triggers:** See `triggers/` directory for detailed trigger documentation
- **Control Flow:** See `control-flow/` directory for if/else, try/catch, and foreach patterns
- **Templates:** See `templates/` directory for starter templates
