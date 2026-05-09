---
name: workato-recipes
description: Base skill for Workato recipe development. Provides foundational knowledge for recipe JSON structure, trigger types, control flow patterns, datapill syntax, and formulas. Connector-specific skills extend this base.
license: MIT
metadata:
  author: Workato
  version: "1.0.0"
---

# Workato Recipes Base Skill - Agent Instructions

This document provides foundational knowledge for AI agents to generate valid Workato recipe JSON. This is the base skill that connector-specific skills (stripe-recipes, salesforce-recipes, etc.) extend.

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects (recipes already exist):

1. **Read 1-2 existing `.recipe.json` files** to understand project structure and patterns
2. **Verify connection names** - ask user for exact connection names in their workspace
3. **Follow established folder structure** - match where recipes and connections are organized

### For GREENFIELD projects (no existing recipes):

1. **Use skill templates as reference** - see `templates/` directory in each skill
2. **Use standard file naming** - `{recipe_name}.recipe.json` (lowercase, underscores for spaces)
3. **Start recipe names with action verbs** - "Create...", "Search...", "Update...", "Process..."
4. **Ask user for connection names** - exact names from their Workato workspace

### ALWAYS (both scenarios):

1. **Use descriptive UUIDs** - `{action}-{number}` format (e.g., `search-contact-001`, `return-success-005`)
2. **Use API endpoint triggers** for testability (unless callable recipe is specifically needed)
3. **Define all response codes** upfront in the trigger (200, 400, 500 at minimum)

---

## UUID Format (MANDATORY)

**ALWAYS use descriptive UUIDs**, regardless of what existing recipes in a project use:

```
search-contact-001
create-customer-002
if-found-003
return-success-004
return-error-005
```

**NEVER use random hex UUIDs:**
```
a1b2c3d4-e5f6-7890-abcd-ef1234567890  ← ANTI-PATTERN
11111111-1111-1111-1111-111111111111  ← ANTI-PATTERN
```

> **NOTE:** Recipes created in Workato's declarative UI have random hash UUIDs. This is a platform limitation, NOT a pattern to follow. When you see random UUIDs in existing recipes, do NOT copy them. Always use descriptive UUIDs for new recipes and actions.

---

## Recipe JSON Structure (CRITICAL)

The `code` field is an **OBJECT** (the trigger itself), **NOT** an array wrapped in a `recipe` object.

**Key points:**
- `code` is the trigger object directly, not wrapped in `recipe`
- `code` is NOT an array - actions go inside `code.block`
- Trigger `number` starts at **0**, not 1
- Trigger `as` should be `"trigger"` for callable recipes

See: [fundamentals/recipe-structure.md](fundamentals/recipe-structure.md) for full structure with examples.

---

## Action Numbering (CRITICAL)

Every block must have a sequential `number` field:

| Block | Number |
|-------|--------|
| Trigger | 0 |
| First action | 1 |
| Second action | 2 |
| ... | ... |

**Non-sequential numbers cause "out of sequence" errors that block recipe activation.** When modifying recipes, always renumber all actions sequentially.

---

## Built-in Providers

The `workato` provider is **built-in** and should **NOT** be in the recipe's `config` array. Only include config entries for external connectors requiring authentication (e.g., `salesforce`, `stripe`, `gmail`).

---

## Connection Configuration (CRITICAL)

**DO NOT put `config` blocks inside actions.** Connections are defined ONLY in the top-level `config` array. Actions reference connections implicitly through the `provider` field.

### WRONG (config inside action):
```json
{
  "provider": "gmail",
  "name": "adhoc_http",
  "config": {
    "account_id": {"name": "My Gmail"}
  }
}
```

### CORRECT (top-level only):
```json
{
  "code": { ... },
  "config": [
    {
      "keyword": "application",
      "provider": "gmail",
      "account_id": {"name": "My Gmail"}
    }
  ]
}
```

---

## Filename Convention

**Recipe filenames must match the recipe's `name` field**, converted to lowercase with spaces replaced by underscores. Workato normalizes filenames on pull, so mismatches cause filename changes.

| Recipe Name | Correct Filename |
|-------------|------------------|
| `"name": "Search Contact By Email"` | `search_contact_by_email.recipe.json` |
| `"name": "Create Stripe Customer"` | `create_stripe_customer.recipe.json` |
| `"name": "Handle Dialog Submit"` | `handle_dialog_submit.recipe.json` |

---

## CRITICAL: REST Connector Action Name

> **WARNING:** The `rest` provider MUST use `make_request_v2` as its action name — NOT `__adhoc_http_action`. Using the wrong action name causes Workato to silently strip all input config on import. See [patterns/adhoc-http-actions.md](patterns/adhoc-http-actions.md) for the full `make_request_v2` structure and examples.

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
| Stop Action | [control-flow/stop.md](control-flow/stop.md) |
| API Endpoint Trigger | [triggers/api-endpoint.md](triggers/api-endpoint.md) |
| Callable Recipe Trigger | [triggers/callable-recipe.md](triggers/callable-recipe.md) |
| Messaging Topic Trigger | [triggers/messaging-topic.md](triggers/messaging-topic.md) |
| Publish to Topic Action | [triggers/messaging-topic.md](triggers/messaging-topic.md) |
| Adhoc HTTP Actions | [patterns/adhoc-http-actions.md](patterns/adhoc-http-actions.md) |
| JWT Bearer Auth | [patterns/jwt-auth.md](patterns/jwt-auth.md) |
| API Platform Artifacts | [patterns/api-platform-artifacts.md](patterns/api-platform-artifacts.md) |

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

### API Endpoint Trigger (Recommended for Testing)

**Use when:** Recipe should be callable via external HTTP request (curl, webhooks, third-party systems).

**Provider:** `workato_api_platform`
**Action:** `receive_request`

> **RECOMMENDATION:** Use API endpoint triggers for most recipes. They're easier to test via curl and more practical for real integrations than callable recipes.
>
> **Note:** API endpoint recipes require companion `.api_endpoint.json` and `.api_group.json` files in addition to the recipe JSON. See [patterns/api-platform-artifacts.md](patterns/api-platform-artifacts.md) for the complete artifact set and file formats.

#### Complete API Endpoint Example

```json
{
  "number": 0,
  "provider": "workato_api_platform",
  "name": "receive_request",
  "as": "trigger",
  "keyword": "trigger",
  "input": {
    "request": {
      "content_type": "json",
      "schema": [
        {
          "name": "email",
          "label": "Email",
          "type": "string",
          "control_type": "text",
          "optional": false,
          "hint": "Customer email address"
        },
        {
          "name": "name",
          "label": "Name",
          "type": "string",
          "control_type": "text",
          "optional": false
        },
        {
          "name": "company",
          "label": "Company",
          "type": "string",
          "control_type": "text",
          "optional": true,
          "hint": "Optional company name"
        }
      ]
    },
    "response": {
      "content_type": "json",
      "responses": [
        {
          "name": "Success",
          "http_status_code": "200"
        },
        {
          "name": "Created",
          "http_status_code": "201"
        },
        {
          "name": "Bad Request",
          "http_status_code": "400"
        },
        {
          "name": "Server Error",
          "http_status_code": "500"
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
          "name": "email",
          "label": "Email",
          "type": "string",
          "control_type": "text"
        },
        {
          "name": "name",
          "label": "Name",
          "type": "string",
          "control_type": "text"
        },
        {
          "name": "company",
          "label": "Company",
          "type": "string",
          "control_type": "text"
        }
      ]
    }
  ],
  "block": [
    // Actions go here
  ]
}
```

#### Request Schema Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Field identifier (used in datapills) |
| `label` | Yes | Display label in UI |
| `type` | Yes | Data type: `string`, `integer`, `boolean`, `date`, `date_time` |
| `control_type` | Yes | UI control: `text`, `number`, `checkbox`, `date`, `select` |
| `optional` | Yes | `true` for optional, `false` for required |
| `hint` | No | Help text for the field |

#### Multiple Response Codes

Define all possible HTTP responses in the trigger. The `return_response` action references these by name:

```json
"responses": [
  { "name": "Success", "http_status_code": "200" },
  { "name": "Created", "http_status_code": "201" },
  { "name": "Bad Request", "http_status_code": "400" },
  { "name": "Conflict", "http_status_code": "409" },
  { "name": "Server Error", "http_status_code": "500" }
]
```

#### Datapill Paths for Request Fields

Access request fields directly (no `body` wrapper):

```json
"path": ["request", "email"]
"path": ["request", "name"]
"path": ["request", "company"]
```

**WRONG:**
```json
"path": ["request", "body", "email"]
```

#### Testing with curl

```bash
curl -X POST "https://apim.workato.com/your-workspace/your-endpoint" \
  -H "API-TOKEN: your-api-token" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User"}'
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
| React to messages from other recipes | Messaging Topic (subscriber) |
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

### API Endpoint Response Action (return_response)

**Use when:** Recipe uses `workato_api_platform` trigger and needs to return HTTP response.

**Provider:** `workato_api_platform`
**Action:** `return_response`

#### How pick_list Maps Response Names to HTTP Codes

The `pick_list` in `extended_input_schema` maps the response names (defined in trigger) to HTTP status codes:

```json
"pick_list": [
  ["Success", "200"],      // "Success" from trigger → HTTP 200
  ["Created", "201"],      // "Created" from trigger → HTTP 201
  ["Bad Request", "400"],  // "Bad Request" from trigger → HTTP 400
  ["Server Error", "500"]  // "Server Error" from trigger → HTTP 500
]
```

**CRITICAL:** The first element (e.g., "Success") must match exactly the `name` field from the trigger's `responses` array.

#### Complete return_response Example

```json
{
  "number": 5,
  "provider": "workato_api_platform",
  "name": "return_response",
  "as": "return_success",
  "keyword": "action",
  "uuid": "return-success-005",
  "input": {
    "http_status_code": "200",
    "response": {
      "customer_id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"body\",\"id\"]}')}",
      "success": "true",
      "error_message": "=null"
    }
  },
  "extended_input_schema": [
    {
      "change_on_blur": true,
      "control_type": "select",
      "extends_schema": true,
      "label": "Response",
      "name": "http_status_code",
      "pick_list": [
        ["Success", "200"],
        ["Created", "201"],
        ["Bad Request", "400"],
        ["Server Error", "500"]
      ],
      "type": "string"
    },
    {
      "label": "Response body",
      "name": "response",
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
          "label": "Success",
          "name": "success",
          "type": "boolean"
        },
        {
          "control_type": "text",
          "label": "Error Message",
          "name": "error_message",
          "type": "string"
        }
      ]
    }
  ],
  "extended_output_schema": [
    {
      "change_on_blur": true,
      "control_type": "select",
      "extends_schema": true,
      "label": "Response",
      "name": "http_status_code",
      "pick_list": [
        ["Success", "200"],
        ["Created", "201"],
        ["Bad Request", "400"],
        ["Server Error", "500"]
      ],
      "type": "string"
    },
    {
      "label": "Response body",
      "name": "response",
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
          "label": "Success",
          "name": "success",
          "type": "boolean"
        },
        {
          "control_type": "text",
          "label": "Error Message",
          "name": "error_message",
          "type": "string"
        }
      ]
    }
  ]
}
```

#### Multiple Return Actions Pattern

Use separate `return_response` actions for different scenarios:

```
return_success (200)     → Happy path
return_created (201)     → New record created
return_not_found (200)   → Search found nothing (still success)
return_bad_request (400) → Invalid input
return_error (500)       → Caught exception
```

Each action has the same `extended_input_schema` (with all response codes in pick_list) but different `input.http_status_code` values.

#### Legacy Format Reference

Older recipes may use this more verbose format with `toggleCfg` and `toggle_field`:

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
| `keyword` | Yes | Block type: `trigger`, `action`, `if`, `else`, `try`, `catch`, `foreach`, `stop` |
| `uuid` | Yes | Unique identifier (max 36 chars) |
| `as` | Yes* | Step alias for datapill references |

*Required for actions, triggers, catch, and foreach. Optional for `try`, `if`, and `else` blocks.

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

> **EXCEPTION — Native connector internal parameters:** Native connector actions have built-in parameters handled internally by the connector. These must **NEVER** appear in `extended_input_schema` — if included, Workato creates duplicate fields in the UI, with the `input` value routing to the EIS copy (leaving the native field blank). This applies to ALL native connectors, not just Salesforce. Examples:
> - **Salesforce** `search_sobjects`: `sobject_name`, `limit` are internals. Only user-facing filter fields (`Id`, `AccountId`, `Email`) go in EIS.
> - **Salesforce** `search_sobjects_soql`: `query` is an internal. Empty EIS is correct.
> - **Jira** `search_issues_by_JQL`: `jql` is the internal field name (NOT `query`). Empty EIS is correct. Note: action name is case-sensitive — must be uppercase `JQL`.
> - **General rule:** If an action has a built-in required field visible in the UI, do NOT redeclare it in EIS. Use `input.{field_name}` to set its value; the field name must match the connector's internal name (pull a blank action from the UI to discover it).
> See the connector-specific skill files for details on which parameters are connector internals.

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

Workato formulas use a **restricted subset of Ruby methods** — not all Ruby methods are supported. Using an unsupported method will block recipe activation with no clear error message. **Only use methods from the allowlist below.**

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

### Supported Formula Methods (COMPLETE ALLOWLIST)

Workato formulas are an allowlist of Ruby methods. **If a method is not listed here, do not use it** — it will block recipe activation. This list is sourced from the [Workato formula documentation](https://docs.workato.com/en/formulas.html).

#### String Methods

| Method | Description |
|--------|-------------|
| `blank?` | True if nil, empty, or whitespace only |
| `present?` | True if not blank |
| `presence` | Returns value if present, nil otherwise |
| `include?` | True if string contains substring |
| `exclude?` | True if string does not contain substring |
| `match?` | True if string matches regex pattern |
| `starts_with?` | True if string starts with prefix |
| `ends_with?` | True if string ends with suffix |
| `is_true?` | True if value is truthy |
| `is_not_true?` | True if value is falsy |
| `strip` | Remove leading/trailing whitespace |
| `lstrip` | Remove leading whitespace |
| `rstrip` | Remove trailing whitespace |
| `upcase` | Convert to uppercase |
| `downcase` | Convert to lowercase |
| `capitalize` | Capitalize first letter |
| `titleize` | Capitalize first letter of each word |
| `reverse` | Reverse the string |
| `gsub` | Replace all occurrences of pattern |
| `sub` | Replace first occurrence of pattern |
| `strip_tags` | Remove HTML tags |
| `scrub` | Replace invalid byte sequences |
| `parameterize` | Convert to URL-safe slug |
| `quote` | Wrap in quotes |
| `length` | Number of characters |
| `slice` | Extract substring by position |
| `scan` | Find all matches of pattern |
| `split` | Split into array by delimiter |
| `ljust` | Left-justify with padding |
| `rjust` | Right-justify with padding |
| `encode` | Encode to specified encoding |
| `transliterate` | Transliterate to ASCII |
| `bytes` | Convert to byte array |
| `bytesize` | Size in bytes |
| `byteslice` | Extract bytes by position |
| `to_s` | Convert to string |
| `to_i` | Convert to integer |
| `to_f` | Convert to float |
| `ordinalize` | Convert number to ordinal string (1st, 2nd, 3rd) |
| `to_country_alpha2` | Convert country name to ISO alpha-2 code |
| `to_country_alpha3` | Convert country name to ISO alpha-3 code |
| `to_country_name` | Convert country code to name |
| `to_currency` | Format as currency string |
| `to_currency_code` | Convert to currency code |
| `to_currency_name` | Convert to currency name |
| `to_currency_symbol` | Convert to currency symbol |
| `to_phone` | Format as phone number |
| `to_state_code` | Convert state name to code |
| `to_state_name` | Convert state code to name |

#### Number Methods

| Method | Description |
|--------|-------------|
| `abs` | Absolute value |
| `round` | Round to specified precision |
| `ceil` | Round up |
| `floor` | Round down |
| `even?` | True if even |
| `odd?` | True if odd |
| `blank?` | True if nil |
| `present?` | True if not nil |
| `presence` | Returns value if present, nil otherwise |
| `to_i` | Convert to integer |
| `to_f` | Convert to float |
| `to_s` | Convert to string |
| `to_currency` | Format as currency |
| `to_phone` | Format as phone number |

#### Date/Time Methods

| Method | Description |
|--------|-------------|
| `now` | Current timestamp |
| `today` | Current date |
| `from_now` | Duration from now (e.g., `30.days.from_now`) |
| `ago` | Duration ago (e.g., `1.hour.ago`) |
| `strftime` | Format with pattern (e.g., `strftime('%Y-%m-%dT%H:%M:%SZ')`) |
| `in_time_zone` | Convert to timezone (e.g., `in_time_zone("UTC")`) |
| `beginning_of_hour` | Start of current hour |
| `beginning_of_day` | Start of current day |
| `beginning_of_week` | Start of current week |
| `beginning_of_month` | Start of current month |
| `beginning_of_year` | Start of current year |
| `end_of_month` | End of current month |
| `wday` | Day of week (0=Sunday) |
| `yday` | Day of year |
| `yweek` | Week of year |
| `dst?` | True if daylight saving time |
| `to_date` | Convert to date |
| `to_time` | Convert to time |
| `to_i` | Convert to Unix epoch integer |

#### Array/List Methods

| Method | Description |
|--------|-------------|
| `first` | First element |
| `last` | Last element |
| `index` | Position of element |
| `count` | Number of elements |
| `length` | Number of elements |
| `where` | Filter by condition |
| `except` | Exclude by condition |
| `pluck` | Extract field values |
| `format_map` | Format each element |
| `join` | Combine into string with separator |
| `smart_join` | Join, skipping blank values |
| `concat` | Append another array |
| `reverse` | Reverse order |
| `sum` | Sum of elements |
| `uniq` | Remove duplicates |
| `flatten` | Flatten nested arrays |
| `max` | Maximum value |
| `min` | Minimum value |
| `compact` | Remove nil values |
| `blank?` | True if empty |
| `include?` | True if contains element |
| `exclude?` | True if does not contain element |
| `present?` | True if not empty |
| `presence` | Returns array if present, nil otherwise |
| `to_csv` | Convert to CSV string |
| `to_json` | Convert to JSON string |
| `to_xml` | Convert to XML string |
| `from_xml` | Parse XML string |
| `encode_www_form` | URL-encode as form data |
| `encode_url` | URL-encode a string |
| `to_param` | Convert to URL parameter string |
| `keys` | Hash keys as array |
| `values` | Hash values as array |

**Any method not listed above will block recipe activation.** Workato's formula language is a strict allowlist — standard Ruby methods like `.each`, `.map`, `.chomp`, `.merge`, `.utc`, and `.to_a` do not exist and will cause silent import failures.

**Common equivalents:**
- For UTC timestamps: use `in_time_zone("UTC")` or `strftime('%Y-%m-%dT%H:%M:%SZ')` (not `.utc`)
- For array access: use `.first` / `.last` (not `[0]` or `[n]`)
- For JSON parsing: use the `json_parser` connector's `parse_json_v2` action (not `.parse_json` — no such formula method exists). See [adhoc-http-actions.md](patterns/adhoc-http-actions.md#json-response-handling-nested-data-extraction) for the pattern.
- For filtering/mapping arrays: use `.where`, `.pluck`, `.format_map` (not `.select`, `.map`, `.each`)

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

### Error Handling Return Values (CRITICAL)

When recipes have required return parameters, ALL code paths (success AND catch blocks) must provide values. In catch blocks where data isn't available, use `=null`:

**WRONG:** `"customer_id": ""`
**CORRECT:** `"customer_id": "=null"`

### Selecting Between Multiple Sources (Ternary)

When you need to return a value from one of multiple possible sources (e.g., search result OR create result), use ternary syntax:

```json
"customer_id": "=_dp('{...search_result...}').present? ? _dp('{...search_result...}') : _dp('{...create_result...}')"
```

This avoids the need for intermediate variables and works at both validation and runtime.

---

## Connection Configuration

### Same-Folder References

When connections are in the same folder as recipes, use empty string for `folder`:

```json
"account_id": {
  "zip_name": "my_connection.connection.json",
  "name": "My Connection Name",
  "folder": ""
}
```

### Different-Folder References

When connections are in a different folder:

```json
"account_id": {
  "zip_name": "Connections/my_connection.connection.json",
  "name": "My Connection Name",
  "folder": "Connections"
}
```

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| `recipe.code[]` wrapper | Recipe doesn't render | Use `code` as object directly |
| Non-sequential action numbers | Activation error | Renumber sequentially from 0 |
| `workato` provider in config | Push error | Remove - it's built-in |
| Empty string for required params | Activation error | Use `=null` |
| `+` concat with datapills at import | Validation error | Use ternary or single datapill |
| Random hex UUIDs | Poor maintainability | **Always** use descriptive UUIDs (don't copy existing random UUIDs) |
| Copying patterns from declarative UI recipes | Various errors | Use skill templates, not UI-generated recipes as reference |

---

---

## Validation

See [validation-checklist.md](validation-checklist.md) for the consolidated recipe validation checklist.

---

## References

- **Fundamentals:** See `fundamentals/` directory for recipe structure, config, and datapill syntax
- **Triggers:** See `triggers/` directory for detailed trigger documentation
- **Control Flow:** See `control-flow/` directory for if/else, try/catch, foreach, and stop patterns
- **Templates:** See `templates/` directory for starter templates
