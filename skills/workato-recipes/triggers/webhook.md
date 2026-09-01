# Webhook Trigger

## Overview

**Use when:** An external system needs to push events into a recipe over HTTP,
and you don't control that system's request format (unlike an API Endpoint
trigger, where you define the request schema against a Workato-hosted URL for
callers you coordinate with). A webhook trigger accepts whatever payload shape
the external sender pushes, described after the fact via a schema you author.

**Provider:** `workato_webhooks`
**Action:** `new_event`

This is a **platform provider** (no external connection) — same category as
`workato_api_platform` or `clock`. Its config entry uses `account_id: null`.

---

## Trigger Structure

Verified from two real exported recipes (`wk recipes export`):

```json
{
  "number": 0,
  "provider": "workato_webhooks",
  "name": "new_event",
  "as": "trigger",
  "keyword": "trigger",
  "input": {
    "request": {
      "webhook_type": "json",
      "payload_schema": "[{\"control_type\":\"text\",\"label\":\"Jira ticket\",\"name\":\"JiraTicket\",\"type\":\"string\",\"optional\":false}]"
    },
    "webhook_suffix": "Add RFC"
  },
  "extended_output_schema": [
    { "label": "Headers", "name": "headers", "type": "object", "properties": [] },
    {
      "label": "Payload",
      "name": "payload",
      "type": "object",
      "properties": [
        { "control_type": "text", "label": "Jira ticket", "name": "JiraTicket", "type": "string", "optional": false }
      ]
    }
  ],
  "extended_input_schema": [
    {
      "label": "Payload configuration",
      "name": "request",
      "override": true,
      "type": "object",
      "properties": [
        {
          "control_type": "select",
          "label": "Webhook type",
          "name": "webhook_type",
          "type": "string",
          "default": "json",
          "extends_schema": true,
          "pick_list": [
            ["GET request", "get"],
            ["PUT/POST with JSON payload", "json"],
            ["PUT/POST with XML payload", "xml"],
            ["PUT/POST with FORM encoded payload", "form"],
            ["PUT/POST with raw binary data", "rawdata"],
            ["PUT/POST with unicode text data", "rawdatatxt"]
          ]
        },
        {
          "control_type": "schema-designer",
          "label": "Payload schema",
          "name": "payload_schema",
          "type": "string",
          "sample_data_type": "json_http",
          "extends_schema": true,
          "optional": true,
          "sticky": true,
          "empty_schema_title": "Describe all fields in your response."
        },
        {
          "control_type": "schema-designer",
          "label": "Query params",
          "name": "query_params",
          "type": "string",
          "extends_schema": true,
          "optional": true,
          "sticky": true,
          "empty_schema_title": "Describe all the query params"
        },
        {
          "control_type": "schema-designer",
          "label": "Headers",
          "name": "headers_schema",
          "type": "string",
          "extends_schema": true,
          "optional": true,
          "sticky": true,
          "empty_schema_title": "Describe all the webhook headers"
        }
      ]
    }
  ]
}
```

## Input Fields

| Field | Verified value(s) | Description |
|---|---|---|
| `request.webhook_type` | `"json"` (also `"get"`, `"xml"`, `"form"`, `"rawdata"`, `"rawdatatxt"` per the EIS `pick_list`, not independently verified in a real recipe) | The HTTP method + payload encoding the external sender uses. `"json"` (PUT/POST with a JSON body) is the only value confirmed against a live recipe. |
| `request.payload_schema` | a stringified JSON array of field definitions | Describes the shape of the incoming payload. Can be trivially small (a single field) or arbitrarily deep/nested (see the "Real-world payload" example below, from a Liferay object-action webhook with dozens of nested fields) — Workato does not require this to be flat. |
| `webhook_suffix` | e.g. `"Add RFC"`, `"CiLicenseChanged"` | A human-readable label appended to the generated webhook URL path, distinguishing this trigger's URL from other webhook triggers in the same recipe/workspace. Not itself part of the payload schema. |

## Optional Fields (present in EIS, not populated in the verified examples)

- `request.query_params` — a `schema-designer` field for describing expected URL query parameters, left empty in both verified recipes (no query-param usage observed)
- `request.headers_schema` — a `schema-designer` field for describing which request headers to expose as datapills. When populated (see the second verified recipe below), the trigger's `headers` output object gains matching properties; when left empty, `headers` still exists in the output but with an empty `properties: []`

## Output Shape

The trigger always emits two top-level objects, regardless of `payload_schema`/`headers_schema` contents:

```json
"path": ["headers"]                    // object — populated only if headers_schema declares fields
"path": ["headers", "x_request_id"]    // example header field, if declared in headers_schema
"path": ["payload"]                    // object — mirrors payload_schema
"path": ["payload", "JiraTicket"]      // example payload field, per payload_schema
```

## Gotchas

1. **`payload_schema` can be deeply nested — don't assume a flat shape.** A verified real-world example (a Liferay object-action webhook, recipe 1351773) declares a `payload_schema` with objects nested 4+ levels deep (`payload.originalObjectEntry.values.quantity`, `payload.objectEntry.values.licenseName`, etc.). Author the schema to match whatever the external sender actually sends — don't flatten it "for simplicity."
2. **`extended_input_schema`/`extended_output_schema` are driven entirely by what you put in `payload_schema`/`headers_schema`, not fixed.** Unlike a native connector action with a connector-defined schema, this trigger's shape is 100% author-defined per recipe — there's no "authoritative" webhook payload shape to look up; it's whatever the external system sends, described by you.
3. **A trigger-level `filter` can reference the webhook's own payload datapills**, including comparing two nested fields against each other (e.g. detecting a specific field change between an "old" and "new" snapshot both present in the same payload) — see the compound `filter` block in recipe 1351773, which uses six `not_equals_to` conditions with `operand: "or"` to fire only when any one of several tracked fields actually changed value. This is a real, verified filter pattern for a webhook trigger, not something only trigger types with native `filter` support (like `new_updated_object`-style connector triggers) can do.
4. **This trigger has no connection/authentication of its own** — `webhook_type`/`payload_schema` describe the shape of an unauthenticated (or externally-authenticated) inbound HTTP call. If the external sender needs to be verified, that verification has to happen inside the recipe (e.g. checking a shared secret in `headers` or `payload`), not via the trigger's own config.

## Config Entry

```json
{
  "keyword": "application",
  "name": "workato_webhooks",
  "provider": "workato_webhooks",
  "skip_validation": false,
  "account_id": null
}
```

## Related Documentation

- [API Endpoint Trigger](api-endpoint.md) — for callers you control, with a defined request/response contract instead of an arbitrary external payload
- [Scheduler Trigger](scheduler.md) — another platform-provider trigger, useful as a structural comparison
- `liferay-recipes/patterns/` (recipe-skills-cw) — the real-world example cited above (recipe 1351773) is a Liferay Object Action webhook; that skill's docs cover the Liferay-specific payload shape in more depth
