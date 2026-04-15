# API Platform Artifacts

When a recipe uses the `workato_api_platform` trigger (`receive_request`), it requires companion artifact files to define the API collection and endpoint. These files are managed alongside the recipe JSON and are pushed/pulled together.

---

## Complete Artifact Set

An API endpoint recipe consists of four files:

| File | Type | Purpose |
|------|------|---------|
| `{recipe_name}.recipe.json` | Recipe | The recipe logic (trigger + actions) |
| `{recipe_name}.api_endpoint.json` | API Endpoint | Maps an HTTP method + path to the recipe |
| `{collection_name}.api_group.json` | API Collection | Groups related endpoints under a versioned handle |
| `{connection_name}.connection.json` | Connection | Connection stub for external connectors used by the recipe |

---

## API Collection (`.api_group.json`)

Defines a versioned collection that groups related API endpoints.

```json
{
  "name": "my-api-collection",
  "version": "1.0",
  "description": "Description of what this collection provides",
  "handle": "my-api-collection-v1",
  "use_prefix": true
}
```

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Collection name (lowercase, hyphens) |
| `version` | string | Yes | Semantic version (e.g., `"1.0"`) |
| `description` | string | No | Human-readable description (can be `null`) |
| `handle` | string | Yes | URL path segment — convention: `{name}-v{major}` |
| `use_prefix` | boolean | Yes | Whether the workspace prefix is included in the URL |

### Naming Conventions

- **`name`**: lowercase with hyphens (e.g., `ga4-devrel-api`, `dev-kit-testing`)
- **`handle`**: append the major version to the name (e.g., `ga4-devrel-api-v1`)
- **Filename**: match the `name` field with underscores: `ga4_devrel_api.api_group.json`

---

## API Endpoint (`.api_endpoint.json`)

Maps an HTTP method and path to a specific recipe within a collection.

```json
{
  "name": "Fetch blog metrics",
  "recipe_id": {
    "zip_name": "ga4_blog_metrics_for_devrel_mcp.recipe.json",
    "name": "GA4 Blog Metrics for DevRel MCP",
    "folder": ""
  },
  "api_group_id": {
    "zip_name": "ga4_devrel_api.api_group.json",
    "name": "ga4-devrel-api",
    "folder": ""
  },
  "method": "POST",
  "path": "fetch-blog-metrics",
  "legacy": false,
  "validate_request": false
}
```

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Human-readable endpoint name |
| `recipe_id` | object | Yes | Reference to the recipe file (see below) |
| `api_group_id` | object | Yes | Reference to the API collection file (see below) |
| `method` | string | Yes | HTTP method: `"GET"`, `"POST"`, `"PUT"`, `"DELETE"`, `"PATCH"` |
| `path` | string | Yes | URL path segment (lowercase, hyphens, no leading `/`) |
| `legacy` | boolean | Yes | Set to `false` for new endpoints |
| `validate_request` | boolean | Yes | Whether to validate incoming request schema |

### Cross-Reference Format

Both `recipe_id` and `api_group_id` use the same reference format:

```json
{
  "zip_name": "filename.extension.json",
  "name": "Display Name",
  "folder": ""
}
```

| Field | Description |
|-------|-------------|
| `zip_name` | Path to the referenced file in the export package |
| `name` | Display name of the referenced artifact (must match the `name` field in the target file) |
| `folder` | Folder containing the file — use `""` for same-folder references |

> **Important:** The `name` in `recipe_id` must match the recipe's `"name"` field exactly. The `name` in `api_group_id` must match the collection's `"name"` field exactly.

### Naming Conventions

- **`path`**: lowercase with hyphens (e.g., `fetch-blog-metrics`, `customer-onboarding-orchestrator`)
- **Filename**: match the recipe filename but with `.api_endpoint.json` suffix: `ga4_blog_metrics_for_devrel_mcp.api_endpoint.json`

---

## Connection File (`.connection.json`)

A minimal stub that identifies a connection for the sync system. Credentials are managed server-side (via the Workato UI or CLI), not stored in this file.

```json
{
  "name": "GA4 Service Account",
  "provider": "rest",
  "root_folder": false
}
```

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Connection display name (must match the `name` in recipe `config[].account_id`) |
| `provider` | string | Yes | Provider identifier (e.g., `rest`, `salesforce`, `stripe`) |
| `root_folder` | boolean | Yes | Whether this connection is at the workspace root level |

### Naming Conventions

- **Filename**: `{snake_case_name}.connection.json` (e.g., `ga4_service_account.connection.json`)
- **`name`**: Human-readable, matches what's referenced in recipe `config[].account_id.name`

See [config-section.md](../fundamentals/config-section.md) for how recipes reference connections via the `account_id` object.

---

## URL Construction

When `use_prefix: true`, the full endpoint URL is:

```
https://apim.{region}.workato.com/{workspace_prefix}/{handle}/{path}
```

**Example:**
```
https://apim.trial.workato.com/zaynet0/ga4-devrel-api-v1/fetch-blog-metrics
```

| Component | Source |
|-----------|--------|
| `{region}` | Workato environment (`trial`, `app`, etc.) |
| `{workspace_prefix}` | Configured in workspace API settings |
| `{handle}` | From `.api_group.json` `handle` field |
| `{path}` | From `.api_endpoint.json` `path` field |

---

## Complete Example

For a recipe called "GA4 Blog Metrics for DevRel MCP" in the `ga4-devrel-api` collection:

```
recipes/
├── ga4_blog_metrics_for_devrel_mcp.recipe.json        # Recipe logic
├── ga4_blog_metrics_for_devrel_mcp.api_endpoint.json   # POST /fetch-blog-metrics
├── ga4_devrel_api.api_group.json                       # ga4-devrel-api-v1 collection
└── ga4_service_account.connection.json                 # REST connection stub
```

Multiple recipes can share the same API collection:

```
recipes/
├── customer_onboarding_orchestrator.recipe.json
├── customer_onboarding_orchestrator.api_endpoint.json  ─┐
├── validate_email_format.recipe.json                    │ Both reference
├── validate_email_format.api_endpoint.json             ─┘ the same collection
└── dev_kit_testing.api_group.json                       # Shared collection
```

---

## Validation Checklist

- [ ] `.api_group.json` has all 5 required fields (`name`, `version`, `description`, `handle`, `use_prefix`)
- [ ] `handle` follows `{name}-v{major}` convention
- [ ] `.api_endpoint.json` `recipe_id.name` matches the recipe's `"name"` field exactly
- [ ] `.api_endpoint.json` `api_group_id.name` matches the collection's `"name"` field exactly
- [ ] `recipe_id.zip_name` and `api_group_id.zip_name` point to correct filenames
- [ ] `folder` is `""` for same-folder references (not omitted)
- [ ] `path` is lowercase with hyphens, no leading `/`
- [ ] `.connection.json` `name` matches what's in recipe `config[].account_id.name`
- [ ] `.connection.json` `provider` matches what's in recipe `config[].provider`
- [ ] All filenames follow snake_case convention matching the artifact's `name` field

## Related Documentation

- [Config Section](../fundamentals/config-section.md) — Connection references in recipes
- [API Endpoint Trigger](../triggers/api-endpoint.md) — Recipe trigger configuration
