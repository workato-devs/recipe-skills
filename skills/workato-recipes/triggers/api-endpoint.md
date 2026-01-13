# API Endpoint Trigger

Use the API endpoint trigger when your recipe needs to be callable via external HTTP requests.

## Provider Details

| Field | Value |
|-------|-------|
| Provider | `workato_api_platform` |
| Action | `receive_request` |
| Config provider | `workato_api_platform` with `account_id: null` |

## Complete Trigger Structure

```json
{
  "number": 0,
  "provider": "workato_api_platform",
  "name": "receive_request",
  "as": "api_trigger",
  "keyword": "trigger",
  "input": {
    "request": {
      "content_type": "json",
      "schema": "[{\"name\":\"email\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Email\",\"optional\":false,\"hint\":\"Customer email address\"},{\"name\":\"name\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Name\",\"optional\":false,\"hint\":\"Customer name\"}]"
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
          "body_schema": "[{\"name\":\"error\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Error\"}]"
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
  ],
  "uuid": "api-trigger-001",
  "format_version": 2
}
```

**CRITICAL: Correct Format**
- Use `request.schema` (NOT `body_schema` or `path_params`)
- Fields go directly under `request.properties` in `extended_output_schema`
- Access fields via: `["request", "field_name"]` (NOT `["request", "body", "field_name"]`)

## Request Configuration

### Request Schema

Define the expected request fields using `schema`:

```json
"request": {
  "content_type": "json",
  "schema": "[{\"name\":\"email\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"Email\",\"hint\":\"Customer email address\"},{\"name\":\"name\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"Name\",\"hint\":\"Customer full name\"}]"
}
```

**Field properties:**
- `name` - Field identifier (used in datapills)
- `type` - Data type: `string`, `number`, `boolean`, `date`, `date_time`, etc.
- `control_type` - UI control: `text`, `number`, `checkbox`, `date`, etc.
- `label` - Display label
- `optional` - Whether field is required (`false` = required)
- `hint` - Help text for the field

## Response Configuration

Define multiple response types with different HTTP status codes:

```json
"responses": [
  {
    "name": "Success",
    "http_status_code": "200",
    "body_schema": "[{\"name\":\"customer_id\",\"type\":\"string\"},{\"name\":\"created\",\"type\":\"boolean\"}]"
  },
  {
    "name": "Not Found",
    "http_status_code": "404",
    "body_schema": "[{\"name\":\"error\",\"type\":\"string\"}]"
  },
  {
    "name": "Bad Request",
    "http_status_code": "400",
    "body_schema": "[{\"name\":\"error\",\"type\":\"string\"},{\"name\":\"field\",\"type\":\"string\"}]"
  }
]
```

## Returning Responses

Use the `return_response` action to return data (see base skill Response Actions section for complete details):

```json
{
  "number": 5,
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
      "id": "#{_dp('...')}",
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

### HTTP Status Code

The `http_status_code` must match one of the status codes defined in the trigger's `response.responses` array.
The `pick_list` in `extended_input_schema` must map response names to their status codes.

## Accessing Request Data

### Request Fields

Access fields directly from the request object:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"email\"]}')}"
```

**Pattern:**
```json
{
  "pill_type": "output",
  "provider": "workato_api_platform",
  "line": "api_trigger",        // The "as" value from your trigger
  "path": ["request", "field_name"]
}
```

**Examples:**
```json
// String field
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"name\"]}')}"

// Number field
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"amount\"]}')}"

// Boolean field
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"is_active\"]}')}"
```

## Required Config Entry

```json
{
  "keyword": "application",
  "provider": "workato_api_platform",
  "skip_validation": false,
  "account_id": null
}
```

## Complete Example

See: [templates/api-endpoint-trigger.template.json](../templates/api-endpoint-trigger.template.json)
