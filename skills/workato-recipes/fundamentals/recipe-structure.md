# Recipe JSON Structure

## Overview

Every Workato recipe is a JSON document with a standardized top-level structure. Understanding this structure is essential for generating valid recipes that Workato can import and execute.

## JSON Structure

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

## Properties Reference

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Recipe display name shown in Workato UI |
| `version` | integer | Yes | Recipe version number (typically 1 for new recipes) |
| `private` | boolean | Yes | Whether recipe is private to the workspace |
| `concurrency` | integer | Yes | Maximum concurrent executions (typically 1) |
| `config` | array | Yes | Provider/connection configurations |
| `code` | object | Yes | Trigger and action blocks |

## The `code` Object

The `code` object contains the recipe's executable logic, structured as nested blocks:

```json
"code": {
  "number": 0,
  "keyword": "trigger",
  "provider": "workato_api_platform",
  "name": "receive_request",
  "as": "api_trigger",
  "input": {
    // Trigger configuration
  },
  "block": [
    {
      "number": 1,
      "keyword": "action",
      "provider": "salesforce",
      "name": "search_sobjects",
      "as": "search_contacts",
      "input": {
        // Action inputs
      },
      "uuid": "search-001"
    }
  ],
  "uuid": "trigger-001"
}
```

### Block Hierarchy

- **Trigger** (number: 0): The entry point that starts the recipe
- **Actions** (number: 1+): Operations that execute after the trigger
- **Control Flow** (if/else, try/catch, foreach): Contain nested blocks

## Block Requirements

Every block in a recipe requires these fields:

| Field | Required | Description |
|-------|----------|-------------|
| `number` | Yes | Sequential step number (trigger is 0) |
| `keyword` | Yes | Block type: `trigger`, `action`, `if`, `else`, `try`, `catch`, `foreach` |
| `uuid` | Yes | Unique identifier (max 36 characters) |
| `as` | Yes* | Step alias for datapill references |

*Required for all blocks except some control flow structures.

### Provider Field Rules

| Block Type | Provider |
|------------|----------|
| Trigger | Required (e.g., `workato_api_platform`) |
| Action | Required (e.g., `stripe`, `salesforce`) |
| If/Else | NO provider field |
| Catch | `"provider": null` (explicitly null) |

## UUID Guidelines

- Must be unique within the recipe
- **Maximum 36 characters** (platform rejects longer UUIDs)
- Use descriptive names: `"search-customer-001"`, `"return-success-001"`

> **WARNING:** UUIDs longer than 36 characters will cause the recipe to be rejected during import. Keep names concise.

## Step Numbering

Step numbers (`number` field) must be sequential:
- Trigger: 0
- First action: 1
- Second action: 2
- Control flow blocks and their contents continue the sequence

Nested blocks within control flow (if/else, try/catch, foreach) continue the sequence:

```json
{
  "number": 2,
  "keyword": "if",
  "block": [
    { "number": 3, "keyword": "action", ... },
    { "number": 4, "keyword": "else", "block": [
      { "number": 5, "keyword": "action", ... }
    ]}
  ]
}
```

## Common Patterns

### Minimal Recipe Structure

```json
{
  "name": "Simple API Recipe",
  "version": 1,
  "private": true,
  "concurrency": 1,
  "config": [
    {
      "keyword": "application",
      "provider": "workato_api_platform",
      "skip_validation": false,
      "account_id": null
    }
  ],
  "code": {
    "number": 0,
    "keyword": "trigger",
    "provider": "workato_api_platform",
    "name": "receive_request",
    "as": "api_trigger",
    "input": { ... },
    "block": [
      // Actions here
    ],
    "uuid": "trigger-001"
  }
}
```

## Gotchas and Best Practices

1. **UUID length limit**: Keep UUIDs under 36 characters or the recipe will fail to import.

2. **Sequential numbering**: Always maintain sequential step numbers (0, 1, 2, 3...). Gaps in the `number` field cause "out of sequence" errors that block recipe activation. When adding or removing actions, renumber all blocks sequentially.

3. **Provider in config**: Every provider used in the recipe must have a corresponding entry in the `config` array, **except** the built-in `workato` provider (which should NOT be used — see below). Common providers and their config needs:

   | Provider | Config Required | `account_id` |
   |----------|-----------------|--------------|
   | `workato_api_platform` | Yes | `null` |
   | `workato_recipe_function` | Yes | `null` |
   | `workato_variable` | Yes | `null` |
   | `salesforce`, `snowflake`, etc. | Yes | Connection reference object |
   | `workato` (built-in) | **Do not use** | N/A — use `workato_variable` instead |

   > **WARNING:** The `workato` provider's `set_variable` action is not recognized by the Workato UI and causes "select app and action" errors. Always use `workato_variable`/`declare_variable` for variables. See [variables-and-lists.md](../patterns/variables-and-lists.md).

4. **Alias uniqueness**: The `as` field must be unique across all blocks since it's used for datapill references.

5. **Version field**: Always use `1` for new recipes. Workato manages version increments internally.

6. **Required return fields in ALL paths**: All required fields in `result_schema_json` must have mapped values in EVERY return path, including error handlers. An empty string `""` fails validation. Use appropriate values based on your use case:
   - `"=null"` - Formula returning null when no value is available
   - `"N/A"` or `"error"` - Explicit placeholder string
   - A default value appropriate for the field type

   **WRONG (empty string fails validation):**
   ```json
   "result": {
     "contact_id": "",
     "status": "error"
   }
   ```

   **CORRECT (formula returning null):**
   ```json
   "result": {
     "contact_id": "=null",
     "status": "error"
   }
   ```

## Validation

See [validation-checklist.md](../validation-checklist.md) for consolidated validation.

## Related Documentation

- [Config Section](config-section.md)
- [Datapill Syntax](datapill-syntax.md)
- [API Endpoint Trigger](../triggers/api-endpoint.md)
- [Callable Recipe Trigger](../triggers/callable-recipe.md)
