# Stop Action

## Overview

The stop action halts recipe execution at the current step. It uses `keyword: "stop"` — NOT `keyword: "action"`. It has no `provider` or `name` fields.

Stop is typically used inside an `else` block to bail out when input validation fails. The recipe ends immediately — no subsequent steps execute.

## JSON Structure

```json
{
  "number": 5,
  "keyword": "stop",
  "input": {
    "stop_with_error": "false",
    "stop_reason": "Request ID was not provided"
  },
  "uuid": "stop-missing-input-005"
}
```

## Properties Reference

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `keyword` | string | Yes | Must be `"stop"` |
| `number` | integer | Yes | Step number in the recipe |
| `input` | object | Yes | Stop configuration |
| `uuid` | string | Yes | Unique identifier |

**NOT allowed:** `provider`, `name`, `as` — stop blocks do not have these fields.

### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `stop_with_error` | string | Yes | `"true"` or `"false"` — whether the job is marked as failed |
| `stop_reason` | string | When `stop_with_error` is `"true"` | Human-readable reason for the stop |
| `message` | string | No | Optional message logged with the stop |

When `stop_with_error` is `"false"`, `stop_reason` may be present but is stripped by the server on export.

## Placement

Stop blocks go inside a `block` array — typically inside an `else` block for input validation:

```json
{
  "keyword": "if",
  "as": "validate_input",
  "input": {
    "type": "compound",
    "operand": "and",
    "conditions": [
      {
        "operand": "present",
        "lhs": "#{_dp('{...request_id...}')}",
        "uuid": "cond-id-present"
      }
    ]
  },
  "block": [
    { "keyword": "action", "...": "happy path actions" },
    {
      "keyword": "else",
      "as": "else_missing_input",
      "input": {},
      "block": [
        {
          "keyword": "stop",
          "number": 5,
          "input": {
            "stop_with_error": "false",
            "stop_reason": "Required field missing"
          },
          "uuid": "stop-missing-005"
        }
      ],
      "uuid": "else-missing-004"
    }
  ],
  "uuid": "if-validate-001"
}
```

**CRITICAL:** The else block must be the **last item** in the if's `block` array (nested inside), NOT a sibling of the if block. Import accepts sibling placement silently, but activation rejects it.

## Behavior by Trigger Type

### API Endpoint Recipes

When stop fires, the API response is **empty** (no body) with HTTP 200. The `return_response` action never executes, so no structured response is returned. Callers see a successful HTTP status but no payload.

To return a proper error response instead of stopping, use a `return_response` action in the else block with an error HTTP status code.

### Genie Skill Recipes

**`stop` with `stop_with_error: "true"` is NOT supported in genie skills.** The recipe visualizer rejects it as `unknown keyword stop`.

Only `stop_with_error: "false"` works — but it provides no error message to the user. For error paths in genie skills, use `workflow_return_result` with `success: false` instead:

```json
{
  "keyword": "action",
  "provider": "workato_genie",
  "name": "workflow_return_result",
  "as": "return_error",
  "input": {
    "result": {
      "Output1": "Error: user_email is required"
    }
  },
  "extended_input_schema": [
    {
      "label": "Result",
      "name": "result",
      "properties": [
        { "control_type": "text", "label": "Output 1", "name": "Output1", "optional": true, "type": "string" }
      ],
      "type": "object"
    }
  ],
  "uuid": "return-error-002"
}
```

### Callable Recipes

When stop fires, the callable recipe returns without sending a reply. The caller receives no output data — the `call` action output is empty.

## Gotchas

1. **No `as` field**: Stop blocks do not use an `as` alias (there are no output datapills to reference).

2. **String booleans**: `stop_with_error` is a string `"true"` or `"false"`, not a JSON boolean.

3. **Job status**: `stop_with_error: "false"` marks the job as **succeeded**. `stop_with_error: "true"` marks it as **failed**.

4. **Empty API response**: In API endpoint recipes, stop produces an empty 200 response — not a timeout or error. If you need structured error responses, use `return_response` instead.

5. **Genie limitation**: `stop_with_error: "true"` is rejected in genie skill recipes. Use `workflow_return_result` with `success: false` for genie error paths.

## Validation Checklist

- [ ] Uses `keyword: "stop"` (not `keyword: "action"`)
- [ ] No `provider`, `name`, or `as` fields on the stop block
- [ ] `stop_with_error` is a string, not a boolean
- [ ] `stop_reason` is present when `stop_with_error` is `"true"`
- [ ] Stop block is inside a `block` array (typically in an `else` block)
- [ ] If in a genie skill: NOT using `stop_with_error: "true"` (use `workflow_return_result` instead)

## Related Documentation

- [If/Else Conditional](if-else.md)
- [Genie Skill Trigger](../triggers/genie-skill.md)
- [API Endpoint Trigger](../triggers/api-endpoint.md)
