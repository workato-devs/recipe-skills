# API Endpoint Recipe Pattern

## Overview

All Asana recipes in this skill follow the API Endpoint pattern: each recipe exposes a single Asana operation as a callable HTTP endpoint via Workato's API Platform.

## When to Use

Use this pattern for every Asana recipe. The API Platform handles the actual Asana API call — the recipe defines the HTTP interface (request schema, response schema, status codes).

## How It Works

1. **Trigger** (`receive_request`) defines what the caller sends (request body, query params)
2. Workato's API Platform routes the request to the Asana API
3. **Action** (`return_response`) defines what the caller gets back

## Pattern Structure

```json
{
  "name": "Get a task",
  "description": "Get a task by its GID",
  "version": 1,
  "private": true,
  "concurrency": 1,
  "code": {
    "number": 0,
    "provider": "workato_api_platform",
    "name": "receive_request",
    "as": "receive_request",
    "keyword": "trigger",
    "comment": "Define the request and response parameters for this API endpoint",
    "input": {
      "request": {
        "path_params": "[]",
        "content_type": "json",
        "headers": "[]",
        "schema": "<escaped JSON array of input field definitions>"
      },
      "response": {
        "content_type": "json",
        "responses": [
          {
            "name": "200",
            "http_status_code": "200",
            "body_schema": "<escaped JSON array of success response fields>"
          },
          {
            "name": "400",
            "http_status_code": "400",
            "body_schema": "<escaped JSON error response>"
          }
        ]
      }
    },
    "extended_output_schema": [
      {
        "properties": [
          { "control_type": "text", "label": "Calling IP address", "name": "calling_ip", "type": "string", "optional": true },
          {
            "label": "Access profile", "name": "access_profile", "type": "object",
            "properties": [
              { "control_type": "integer", "label": "Access profile ID", "name": "id", "type": "integer", "parse_output": "integer_conversion", "optional": true },
              { "control_type": "text", "label": "Access profile name", "name": "name", "type": "string", "optional": true },
              { "control_type": "text", "label": "Access profile authentication type", "name": "type", "type": "string", "optional": true }
            ],
            "optional": true
          }
        ],
        "label": "Context", "name": "context", "type": "object", "optional": true
      }
    ],
    "block": [
      {
        "number": 1,
        "provider": "workato_api_platform",
        "name": "return_response",
        "as": "return_response",
        "keyword": "action",
        "input": {
          "http_status_code": "200",
          "response": {}
        },
        "uuid": "return-response-001"
      }
    ],
    "uuid": "api-trigger-001"
  },
  "config": [
    {
      "keyword": "application",
      "provider": "workato_api_platform",
      "skip_validation": false,
      "account_id": null
    }
  ]
}
```

## Key Rules

1. **One recipe per operation** — each Asana API operation gets its own recipe
2. **No native Asana provider in config** — only `workato_api_platform`
3. **Schema strings must be escaped** — `schema` and `body_schema` are JSON strings containing escaped JSON
4. **Define all error codes** — 400, 401, 403, 404, 500 at minimum
5. **Use 201 for create operations** — not 200
6. **Wrap success data in `data` object** — Asana API convention

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Schema parse error | Improperly escaped JSON in schema string | Double-check escaping: `\"` for quotes inside the string |
| Missing response code | Not all error codes defined | Add all standard codes (400, 401, 403, 404, 500) |
| Wrong success code | Using 200 for create | Use 201 for POST/create operations |
