# Config Section

## Overview

The config section defines which providers and connections a recipe uses. Every provider referenced in the recipe's actions must have a corresponding entry in the config array.

## JSON Structure

```json
"config": [
  {
    "keyword": "application",
    "provider": "PROVIDER_NAME",
    "skip_validation": false,
    "account_id": null
  }
]
```

## Properties Reference

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `keyword` | string | Yes | Always `"application"` |
| `provider` | string | Yes | Provider identifier (e.g., `salesforce`, `stripe`) |
| `skip_validation` | boolean | Yes | Whether to skip connection validation |
| `account_id` | object/null | Yes | Connection reference or `null` for platform providers |

## Provider Types

### Platform Providers (No Connection Needed)

These are built-in Workato providers that don't require external connections:

| Provider | Description |
|----------|-------------|
| `workato_api_platform` | API endpoint triggers |
| `workato_recipe_function` | Callable recipe triggers |
| `logger` | Logging/debugging actions |

**Config entry for platform providers:**
```json
{
  "keyword": "application",
  "provider": "workato_api_platform",
  "skip_validation": false,
  "account_id": null
}
```

### Connector Providers (Connection Required)

External service connectors require a connection reference:

| Provider | Description |
|----------|-------------|
| `salesforce` | Salesforce CRM |
| `stripe` | Stripe payments |
| `netsuite` | NetSuite ERP |
| `slack` | Slack messaging |

**Config entry for connector providers:**
```json
{
  "keyword": "application",
  "provider": "salesforce",
  "skip_validation": false,
  "account_id": {
    "zip_name": "Workspace Connections/salesforce_production.connection.json",
    "name": "Salesforce Production",
    "folder": "Workspace Connections"
  }
}
```

## Connection Reference Format

When a provider requires a connection, the `account_id` object specifies the connection file:

```json
"account_id": {
  "zip_name": "Workspace Connections/connection_name.connection.json",
  "name": "Connection Display Name",
  "folder": "Workspace Connections"
}
```

| Field | Description |
|-------|-------------|
| `zip_name` | Path to connection JSON file in the export package |
| `name` | Human-readable connection name |
| `folder` | Folder containing the connection |

## Common Patterns

### API Endpoint Recipe

Recipes triggered by external HTTP requests:

```json
"config": [
  {
    "keyword": "application",
    "provider": "workato_api_platform",
    "skip_validation": false,
    "account_id": null
  }
]
```

### Callable Recipe

Recipes invoked by other Workato recipes:

```json
"config": [
  {
    "keyword": "application",
    "provider": "workato_recipe_function",
    "skip_validation": false,
    "account_id": null
  }
]
```

### Multiple Providers

When a recipe uses multiple services:

```json
"config": [
  {
    "keyword": "application",
    "provider": "workato_api_platform",
    "skip_validation": false,
    "account_id": null
  },
  {
    "keyword": "application",
    "provider": "salesforce",
    "skip_validation": false,
    "account_id": {
      "zip_name": "Workspace Connections/salesforce_prod.connection.json",
      "name": "Salesforce Production",
      "folder": "Workspace Connections"
    }
  },
  {
    "keyword": "application",
    "provider": "stripe",
    "skip_validation": false,
    "account_id": {
      "zip_name": "Workspace Connections/stripe_live.connection.json",
      "name": "Stripe Live",
      "folder": "Workspace Connections"
    }
  }
]
```

### With Logger for Debugging

Adding the logger provider for debugging:

```json
"config": [
  {
    "keyword": "application",
    "provider": "workato_recipe_function",
    "skip_validation": false,
    "account_id": null
  },
  {
    "keyword": "application",
    "provider": "logger",
    "skip_validation": false,
    "account_id": null
  }
]
```

## Gotchas and Best Practices

1. **Include all providers**: Every provider used anywhere in the recipe must have a config entry. Missing entries cause import failures.

2. **Platform providers use null**: `workato_api_platform`, `workato_recipe_function`, and `logger` always use `"account_id": null`.

3. **Do NOT include these as providers**:
   - `workato` - Not a valid provider
   - `catch` - Control flow keyword, not a provider

4. **Connection path consistency**: The `zip_name` path must match the actual location in the export package.

5. **Order doesn't matter**: Config entries can be in any order, but maintaining a consistent order (trigger provider first) improves readability.

6. **skip_validation**: Generally set to `false`. Only set to `true` if you want to import the recipe without validating the connection exists.

## Related Documentation

- [Recipe Structure](recipe-structure.md)
- [API Endpoint Trigger](../triggers/api-endpoint.md)
- [Callable Recipe Trigger](../triggers/callable-recipe.md)
