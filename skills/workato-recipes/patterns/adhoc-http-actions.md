# Adhoc HTTP Actions

Many Workato connectors support **adhoc HTTP actions** (`__adhoc_http_action`), which allow you to call API endpoints directly when built-in actions don't cover your use case.

---

## When to Use

Use adhoc HTTP actions when:
- The connector doesn't have a built-in action for your operation
- You need to call a newer API endpoint not yet supported
- You need fine-grained control over request/response handling

---

## Basic Structure

```json
{
  "number": 1,
  "provider": "<connector_provider>",
  "name": "__adhoc_http_action",
  "as": "api_call",
  "keyword": "action",
  "input": {
    "mnemonic": "Description of the API call",
    "verb": "post",
    "request_type": "json",
    "response_type": "json",
    "path": "api/endpoint/path",
    "input": {
      "schema": "[...]",
      "data": { ... }
    },
    "output": "[...]",
    "response_headers": "[...]"
  },
  "extended_output_schema": [...],
  "extended_input_schema": [...],
  "uuid": "api-call-001"
}
```

---

## Input Fields

| Field | Required | Description |
|-------|----------|-------------|
| `mnemonic` | No | Human-readable description of the action |
| `verb` | Yes | HTTP method: `"get"`, `"post"`, `"put"`, `"patch"`, `"delete"` |
| `request_type` | For POST/PUT/PATCH | Request body format (see below). Optional for GET/DELETE. |
| `response_type` | Yes | Expected response format (see below) |
| `path` | Yes | API endpoint path (appended to connector's base URL) |
| `input.schema` | No | JSON schema string defining request body/query fields |
| `input.data` | Yes | Actual request data with field values |
| `output` | No | JSON schema string for parsing response body |
| `response_headers` | No | JSON schema string for parsing response headers |

### Request Types

| Type | Description |
|------|-------------|
| `json` | JSON request body |
| `urlencoded` | URL-encoded form data |
| `multipart` | Multipart form (for file uploads) |
| `raw` | Raw JSON request body |
| `xml` | XML request body |
| `text` | Plain text |
| `rawdata` | Raw binary data |

### Response Types

| Type | Description |
|------|-------------|
| `json` | JSON response |
| `raw` | Raw JSON response |
| `xml2` | XML response |
| `text` | Raw text response |

---

## Schema Definition

The `schema`, `output`, and `response_headers` fields use JSON schema strings:

```json
"schema": "[{\"control_type\":\"text\",\"label\":\"Name\",\"type\":\"string\",\"name\":\"name\"},{\"control_type\":\"text\",\"label\":\"Email\",\"type\":\"string\",\"name\":\"email\"}]"
```

### Schema Field Properties

| Property | Description |
|----------|-------------|
| `name` | Field name (used in data and datapills) |
| `label` | Display label |
| `type` | Data type: `string`, `number`, `boolean`, `object`, `array` |
| `control_type` | UI control: `text`, `number`, `checkbox`, `select` |
| `optional` | Whether field is optional |
| `properties` | Nested fields for `object` type |
| `of` | Element type for `array` type |

---

## Extended Schemas

For datapill access, define `extended_output_schema`:

```json
"extended_output_schema": [
  {
    "label": "Body",
    "name": "body",
    "optional": true,
    "properties": [
      {
        "control_type": "text",
        "label": "ID",
        "optional": true,
        "type": "string",
        "name": "id"
      },
      {
        "control_type": "text",
        "label": "Name",
        "optional": true,
        "type": "string",
        "name": "name"
      }
    ],
    "type": "object"
  },
  {
    "label": "Headers",
    "name": "headers",
    "optional": true,
    "properties": [...],
    "type": "object"
  }
]
```

---

## Accessing Response Data

Adhoc HTTP responses are wrapped in `body`:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"<connector>\",\"line\":\"api_call\",\"path\":[\"body\",\"id\"]}')}"
```

For nested data:
```json
"path": ["body", "channel", "id"]
"path": ["body", "user", "profile", "email"]
```

---

## Connectors Supporting Adhoc HTTP

Most OAuth/API-based connectors support adhoc HTTP actions, including:
- `slack_bot` (Workbot for Slack)
- `slack` (Slack)
- `gmail` (Gmail - base URL: `https://www.googleapis.com/gmail/v1/users/`)
- `salesforce`
- `stripe`
- Custom SDK connectors

The base URL and authentication are handled by the connector's connection.

---

## Optional Parameters Pattern

For optional query parameters, use `.presence || skip` to omit blank values:

```json
"input": {
  "data": {
    "maxResults": "=_dp('{...}').presence || skip",
    "pageToken": "=_dp('{...}').presence || skip",
    "q": "=_dp('{...}').presence || skip"
  }
}
```

This pattern:
- Checks if the datapill has a value (`.presence`)
- If blank/nil, uses `skip` to exclude the parameter from the request
- Prevents sending empty query parameters to the API

**When to use:** Any optional query parameter that should only be sent if it has a value.

---

## Example: Slack API Call

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "__adhoc_http_action",
  "as": "create_channel",
  "keyword": "action",
  "input": {
    "mnemonic": "Create Slack channel",
    "verb": "post",
    "request_type": "json",
    "response_type": "json",
    "path": "conversations.create",
    "input": {
      "schema": "[{\"control_type\":\"text\",\"label\":\"Name\",\"type\":\"string\",\"name\":\"name\"}]",
      "data": {
        "name": "my-new-channel"
      }
    },
    "output": "[{\"control_type\":\"text\",\"label\":\"Ok\",\"type\":\"boolean\",\"name\":\"ok\"},{\"properties\":[{\"control_type\":\"text\",\"label\":\"ID\",\"type\":\"string\",\"name\":\"id\"}],\"label\":\"Channel\",\"type\":\"object\",\"name\":\"channel\"}]"
  }
}
```

---

## Example: Generic REST API Call

```json
{
  "number": 1,
  "provider": "http",
  "name": "__adhoc_http_action",
  "as": "fetch_data",
  "keyword": "action",
  "input": {
    "mnemonic": "Fetch resource data",
    "verb": "get",
    "request_type": "json",
    "response_type": "json",
    "path": "https://api.example.com/v1/resources/123",
    "input": {
      "schema": "[]",
      "data": {}
    },
    "output": "[{\"control_type\":\"text\",\"label\":\"ID\",\"type\":\"string\",\"name\":\"id\"},{\"control_type\":\"text\",\"label\":\"Name\",\"type\":\"string\",\"name\":\"name\"}]"
  }
}
```

---

## Validation

See [validation-checklist.md](../validation-checklist.md) for consolidated validation.

## Tips

1. **Copy schemas from working recipes** - Building schemas by hand is error-prone; copy from Workato UI exports
2. **Use absolute URLs** - If the path starts with `http://` or `https://`, it overrides the connector's base URL
3. **Check connector docs** - Some connectors have specific base URLs or authentication requirements
4. **Test incrementally** - Start with minimal schemas and add fields as needed
