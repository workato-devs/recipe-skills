# Adhoc HTTP Actions

Many Workato connectors support **adhoc HTTP actions**, which allow you to call API endpoints directly when built-in actions don't cover your use case.

**CRITICAL: The action name depends on the provider type.** Using the wrong action name causes Workato to silently strip all input config on import.

| Provider type | Action name | Examples |
|---|---|---|
| `http` | `__adhoc_http_action` | Generic HTTP connector |
| Native connectors | `__adhoc_http_action` | `slack_bot`, `salesforce`, `gmail`, `stripe` |
| `rest` | `make_request_v2` | Generic REST connector (e.g., ElevenLabs, custom REST APIs) |

---

## When to Use

Use adhoc HTTP actions when:
- The connector doesn't have a built-in action for your operation
- You need to call a newer API endpoint not yet supported
- You need fine-grained control over request/response handling

---

## `__adhoc_http_action` (for `http` and native providers)

### Basic Structure

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
    "path": "/api/endpoint/path",
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

### Input Fields

| Field | Required | Description |
|-------|----------|-------------|
| `mnemonic` | No | Human-readable description of the action |
| `verb` | Yes | HTTP method: `"get"`, `"post"`, `"put"`, `"patch"`, `"delete"` |
| `request_type` | For POST/PUT/PATCH | Request body format (see below). Optional for GET/DELETE. |
| `response_type` | Yes | Expected response format (see below) |
| `path` | Yes | API endpoint path (appended to connector's base URL). Format depends on the base URL — see [Path Rules](#path-rules). |
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

### Extended Schemas

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

### Accessing Response Data

`__adhoc_http_action` responses are wrapped in `body`:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"<connector>\",\"line\":\"api_call\",\"path\":[\"body\",\"id\"]}')}"
```

For nested data:
```json
"path": ["body", "channel", "id"]
"path": ["body", "user", "profile", "email"]
```

### Example: Slack API Call

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

## `make_request_v2` (for `rest` provider)

The generic REST connector (`rest` provider) uses `make_request_v2` instead of `__adhoc_http_action`. The input structure is completely different.

### Basic Structure

```json
{
  "number": 1,
  "provider": "rest",
  "name": "make_request_v2",
  "as": "api_call",
  "keyword": "action",
  "toggleCfg": {
    "response.ignore_http_errors": true,
    "disable_retries": true
  },
  "input": {
    "request_name": "Description of the API call",
    "request": {
      "method": "POST",
      "content_type": "application/json",
      "url": "/v1/endpoint/path",
      "body": "raw JSON string or formula"
    },
    "response": {
      "output_type": "json",
      "expected_encoding": "UTF-8",
      "ignore_http_errors": "false"
    },
    "wait_for_response": "true",
    "disable_retries": "false"
  },
  "extended_output_schema": [...],
  "extended_input_schema": [...],
  "uuid": "api-call-001",
  "wizardFinished": true
}
```

### Input Fields

| Field | Required | Description |
|-------|----------|-------------|
| `request_name` | No | Human-readable description |
| `request.method` | Yes | `"GET"`, `"POST"`, `"PUT"`, `"DELETE"`, `"HEAD"`, `"PATCH"` (uppercase) |
| `request.url` | Yes | Relative path (appended to connection base URL). Format depends on the base URL — see [Path Rules](#path-rules). |
| `request.content_type` | For POST/PUT/PATCH | See content types below |
| `request.body` | For raw content types | Raw request body string |
| `response.output_type` | Yes | Expected response format (see below) |
| `response.expected_encoding` | No | Default: `"UTF-8"` |
| `response.ignore_http_errors` | No | `"true"` to treat non-2xx as success |
| `wait_for_response` | No | `"true"` to wait (default) |
| `disable_retries` | No | `"true"` to disable automatic retries |

### Content Types

| Value | Description |
|-------|-------------|
| `json` | Structured JSON body (schema-designed fields) |
| `application/json` | **Raw JSON body** (free-text string — use this for dynamic payloads with datapills) |
| `application/xml` | XML |
| `text/plain` | Plain text |
| `application/x-www-form-urlencoded` | URL-encoded form data |
| `application/octet-stream` | Binary |
| `multipart/form-data` | Multipart form |

### Response Output Types

| Value | Description |
|-------|-------------|
| `json` | JSON response (parsed into fields) |
| `rawdatatxt` | Text response (raw string) |
| `rawdata` | Binary response (for audio, images, files) |
| `xml2` | XML response |
| `multipart` | Multipart response |

### toggleCfg

Controls toggle-field behaviors. Common toggles:

```json
"toggleCfg": {
  "response.ignore_http_errors": true,
  "disable_retries": true
}
```

### Accessing Response Data

**`make_request_v2` response data is at the top level**, NOT nested under `body` like `__adhoc_http_action`:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"api_call\",\"path\":[\"body\"]}')}"`
```

Top-level output fields:
- `body` — response body content (or parsed fields for JSON)
- `headers` — response headers
- `response` — mirrors `body` for binary responses

For JSON responses with defined `response_schema`, fields are nested under `response`:
```json
"path": ["response", "field_name"]
```

### Raw JSON Body with Datapills

For `content_type: "application/json"` (raw JSON), use Ruby hash `.to_json` for safe JSON construction:

```json
"body": "={'text' => _dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"text\"]}'), 'model_id' => 'default_value', 'settings' => {'key' => 0.5}}.to_json"
```

This approach:
- Properly escapes special characters in datapill values (quotes, newlines)
- Handles nested objects naturally with Ruby hash syntax
- Uses `.to_json` to produce valid JSON output

For optional fields with defaults:

```json
"body": "={'text' => _dp('{...text...}'), 'model' => (_dp('{...model...}').present? ? _dp('{...model...}') : 'default_model')}.to_json"
```

### Binary Response Handling

For APIs returning binary data (audio, images, files), set `output_type: "rawdata"`. The binary content is at the top-level `body` path.

**To return binary data as base64 in a JSON response, you MUST encode it and strip newlines:**

```json
"audio_base64": "=_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"api_call\",\"path\":[\"body\"]}').encode_base64.gsub(\"\\n\", '')"
```

Why `.gsub("\n", '')`: Ruby's `encode_base64` inserts newlines every 76 characters. These newlines break JSON serialization — Workato returns 422 (unprocessable entity) without the gsub.

Without `.encode_base64`: raw binary in a JSON string field causes Workato to return 500 (internal server error) because binary bytes can't be serialized as UTF-8 JSON.

### Extended Input Schema

`make_request_v2` requires EIS with `override: true` on both `request` and `response` sections to render the form UI correctly. Include the standard form field definitions:

```json
"extended_input_schema": [
  {
    "label": "Request",
    "name": "request",
    "override": true,
    "properties": [
      {
        "control_type": "select",
        "label": "Method",
        "pick_list": [
          ["GET", "GET"], ["POST", "POST"], ["PUT", "PUT"],
          ["DELETE", "DELETE"], ["HEAD", "HEAD"], ["PATCH", "PATCH"]
        ],
        "hint": "Select a HTTP method",
        "default": "GET",
        "type": "string",
        "name": "method"
      },
      {
        "control_type": "text",
        "label": "Request URL",
        "check_secrets": true,
        "hint": "Provide an <b>absolute URL</b> or <b>relative URL</b> (if <b>Base URL</b> is configured in connection).",
        "placeholder": "https://api.example.com/v1/leads",
        "type": "string",
        "name": "url"
      },
      {
        "control_type": "select",
        "label": "Request content type",
        "extends_schema": true,
        "pick_list": [
          ["JSON request body", "json"],
          ["Raw JSON request body", "application/json"],
          ["XML", "application/xml"],
          ["Text", "text/plain"],
          ["URL encoded form", "application/x-www-form-urlencoded"],
          ["Binary", "application/octet-stream"],
          ["Multipart form", "multipart/form-data"]
        ],
        "ngIf": "input.request.method === 'POST' || input.request.method === 'PUT' || input.request.method === 'DELETE' || input.request.method === 'PATCH'",
        "optional": true,
        "default": "application/json",
        "type": "string",
        "name": "content_type"
      },
      {
        "control_type": "text-area",
        "label": "Request body",
        "sticky": true,
        "check_secrets": true,
        "ngIf": "input.request.content_type !== 'json' && input.request.content_type !== 'application/x-www-form-urlencoded' && input.request.content_type !== 'multipart/form-data' && (input.request.method === 'POST' || input.request.method === 'PUT' || input.request.method === 'DELETE' || input.request.method === 'PATCH')",
        "optional": true,
        "type": "string",
        "name": "body"
      },
      {
        "label": "Request headers",
        "control_type": "key_value",
        "optional": true,
        "check_secrets": true,
        "item_label": "Header",
        "sticky": true,
        "of": "object",
        "properties": [
          {"control_type": "text", "label": "Header name", "type": "string", "name": "header"},
          {"control_type": "text", "label": "Value", "type": "string", "name": "value"}
        ],
        "type": "array",
        "name": "headers"
      }
    ],
    "type": "object"
  },
  {
    "label": "Response",
    "name": "response",
    "override": true,
    "properties": [
      {
        "control_type": "select",
        "label": "Response content type",
        "pick_list": [
          ["Text", "rawdatatxt"], ["Binary", "rawdata"],
          ["JSON", "json"], ["XML", "xml2"], ["Multipart", "multipart"]
        ],
        "default": "json",
        "extends_schema": true,
        "type": "string",
        "name": "output_type"
      },
      {
        "control_type": "select",
        "label": "Encoding",
        "pick_list": "supported_encodings_without_binary_global_pick_list",
        "pick_list_connection_less": true,
        "optional": true,
        "default": "UTF-8",
        "type": "string",
        "name": "expected_encoding"
      },
      {
        "control_type": "checkbox",
        "label": "Mark non-2xx response codes as success?",
        "default": "false",
        "optional": true,
        "toggle_hint": "Select from option list",
        "toggle_field": {
          "label": "Mark non-2xx response codes as success?",
          "control_type": "text",
          "toggle_hint": "Use custom value",
          "default": false,
          "optional": true,
          "type": "boolean",
          "name": "ignore_http_errors"
        },
        "type": "boolean",
        "name": "ignore_http_errors"
      }
    ],
    "type": "object"
  }
]
```

### Example: REST API POST with Binary Response

```json
{
  "number": 3,
  "provider": "rest",
  "name": "make_request_v2",
  "as": "tts_request",
  "keyword": "action",
  "toggleCfg": {
    "response.ignore_http_errors": true,
    "disable_retries": true
  },
  "input": {
    "request_name": "Convert text to speech",
    "request": {
      "method": "POST",
      "content_type": "application/json",
      "url": "='/v1/text-to-speech/' + _dp('{...voice_id...}')",
      "body": "={'text' => _dp('{...text...}'), 'model_id' => 'eleven_multilingual_v2', 'voice_settings' => {'stability' => 0.5, 'similarity_boost' => 0.5}}.to_json"
    },
    "response": {
      "output_type": "rawdata",
      "expected_encoding": "UTF-8",
      "ignore_http_errors": "false"
    },
    "wait_for_response": "true",
    "disable_retries": "false"
  },
  "extended_output_schema": [
    {
      "label": "Headers",
      "name": "headers",
      "optional": true,
      "properties": [
        {"control_type": "text", "label": "Content-Type", "name": "content-type", "optional": true, "type": "string"}
      ],
      "type": "object"
    },
    {
      "label": "Response",
      "name": "response",
      "optional": true,
      "properties": [
        {"control_type": "text", "label": "Body", "name": "body", "optional": true, "type": "string"}
      ],
      "type": "object"
    }
  ],
  "extended_input_schema": ["... (see EIS template above)"],
  "uuid": "tts-request-003",
  "wizardFinished": true
}
```

---

## Comparing `__adhoc_http_action` vs `make_request_v2`

| Aspect | `__adhoc_http_action` | `make_request_v2` |
|--------|----------------------|-------------------|
| **Providers** | `http`, native connectors | `rest` |
| **Method field** | `verb` (lowercase: `"post"`) | `request.method` (uppercase: `"POST"`) |
| **URL field** | `path` | `request.url` |
| **Content type** | `request_type` | `request.content_type` |
| **Request body** | `input.data` (structured object) | `request.body` (raw string for `application/json`) |
| **Response type** | `response_type` | `response.output_type` |
| **Response data path** | `["body", "field"]` | `["body"]` or `["response", "field"]` |
| **Schema for body** | `input.schema` (JSON string) | Not needed for raw body |
| **Output schema** | `output` (JSON string) | `response.response_schema` (extends_schema) |
| **EIS** | Flat fields (`verb`, `path`, etc.) | Nested with `override: true` on `request`/`response` |
| **Required extras** | None | `wizardFinished: true`, `toggleCfg` |

---

## Path Rules

- **Paths are appended to the connector's base URL.** The correct format depends on whether the base URL includes a trailing `/`:

| Base URL format | Path format | Example |
|---|---|---|
| `https://slack.com/api/` (trailing `/`) | No leading `/` | `conversations.create` |
| `https://www.googleapis.com/gmail/v1/users/` (trailing `/`) | No leading `/` | `me/messages` |
| `https://api.stripe.com` (no trailing `/`) | Leading `/` | `/v1/customers/search` |
| `https://api.elevenlabs.io` (no trailing `/`) | Leading `/` | `/v1/text-to-speech/` |

- **Check the connector's base URL** to determine the right path format. Base URLs are inconsistent across connectors — some include a trailing `/`, some don't.
- **Do not use absolute URLs** when the connection has a base URL — the path is concatenated directly, which produces a malformed URL (e.g., `https://api.example.com/https://api.example.com/v1/...`).
- **Absolute URLs** (`https://...`) override the base URL and should only be used when intentionally bypassing the connection's base URL.

---

## Formula Syntax in URL and Body Fields

When using `=` formula mode for dynamic URLs or body content:

**Do NOT wrap the entire formula in extra parentheses:**
```
CORRECT: ='/v1/endpoint/' + expr
WRONG:   =('/v1/endpoint/' + expr)
```

**Datapills in formula mode use bare `_dp()`, not `#{_dp()}`:**
```
CORRECT (formula mode): ='/v1/' + _dp('{...}')
WRONG (formula mode):   ='/v1/' + #{_dp('{...}')}
```

**`#{}` interpolation is for string values outside formula context:**
```
CORRECT (string context): "#{_dp('{...}')}"
```

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

## Schema Definition

The `schema`, `output`, and `response_headers` fields (for `__adhoc_http_action`) use JSON schema strings:

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

## Connectors Supporting Adhoc HTTP

Most OAuth/API-based connectors support adhoc HTTP actions, including:
- `slack_bot` (Workbot for Slack) — `__adhoc_http_action`
- `slack` (Slack) — `__adhoc_http_action`
- `gmail` (Gmail) — `__adhoc_http_action`
- `salesforce` — `__adhoc_http_action`
- `stripe` — `__adhoc_http_action`
- `rest` (Generic REST connector) — `make_request_v2`
- Custom SDK connectors — `__adhoc_http_action`

The base URL and authentication are handled by the connector's connection.

---

## Validation

See [validation-checklist.md](../validation-checklist.md) for consolidated validation.

## Tips

1. **Copy schemas from working recipes** — Building schemas by hand is error-prone; copy from Workato UI exports
2. **Check connection base URL** — The path format must match the connector's base URL (see [Path Rules](#path-rules)). Only use absolute URLs when intentionally overriding the connection's base URL.
3. **Check connector docs** — Some connectors have specific base URLs or authentication requirements
4. **Test incrementally** — Start with minimal schemas and add fields as needed
5. **Pull after push** — After pushing a recipe, pull it back to see what Workato normalized (added EOS, changed structure, etc.)
