# Stripe Error Handling Patterns

## Error Response Flattening

Stripe API errors return nested structures. Workato recipes must flatten these for clean result schemas.

### Stripe Error Response Format

```json
{
  "error": {
    "code": "card_declined",
    "message": "Your card was declined.",
    "decline_code": "insufficient_funds",
    "param": "card_number",
    "type": "card_error"
  }
}
```

### Flattened Result Schema

Define flat fields in `result_schema_json`:

```json
"result_schema_json": "[{\"name\":\"success\",\"type\":\"boolean\"},{\"name\":\"error_code\",\"type\":\"string\",\"optional\":true},{\"name\":\"error_message\",\"type\":\"string\",\"optional\":true},{\"name\":\"decline_code\",\"type\":\"string\",\"optional\":true}]"
```

### Mapping Nested Errors to Flat Fields

```json
{
  "input": {
    "result": {
      "success": "false",
      "error_code": "#{_dp('...path\":[\"error\",\"code\"]...')}",
      "error_message": "#{_dp('...path\":[\"error\",\"message\"]...')}",
      "decline_code": "#{_dp('...path\":[\"error\",\"decline_code\"]...')}"
    }
  }
}
```

## Try/Catch Structure

### Correct Nesting

Catch blocks must be INSIDE the try block:

```json
{
  "keyword": "try",
  "block": [
    // Actions that might fail
    { "provider": "stripe", "as": "action_step", ... },

    // Catch is INSIDE try block
    {
      "keyword": "catch",
      "provider": null,
      "as": "catch_error",
      "input": {
        "max_retry_count": "0",
        "retry_interval": "2"
      },
      "block": [
        // Error handling actions
      ],
      "uuid": "catch-001"
    }
  ],
  "uuid": "try-001"
}
```

### Catch Block Requirements

| Field | Required | Value |
|-------|----------|-------|
| `keyword` | Yes | `"catch"` |
| `provider` | Yes | `null` (not "catch") |
| `as` | Yes | Unique alias for datapill references |
| `uuid` | Yes | Unique identifier |
| `input.max_retry_count` | Recommended | `"0"` for no retries |
| `input.retry_interval` | Recommended | `"2"` seconds |

## Return Schema Contract

Every return block must include ALL fields from `result_schema_json`:

### Success Path

```json
{
  "input": {
    "result": {
      "success": "true",
      "customer_id": "#{actual_value}",
      "error_code": "=null",
      "error_message": "=null"
    }
  }
}
```

### Error Path (Catch Block)

```json
{
  "input": {
    "result": {
      "success": "false",
      "customer_id": "=null",
      "error_code": "internal_error",
      "error_message": "#{_dp('...catch_error...path\":[\"message\"]...')}"
    }
  }
}
```

### Not Found Path

```json
{
  "input": {
    "result": {
      "success": "false",
      "customer_id": "=null",
      "error_code": "not_found",
      "error_message": "Customer not found"
    }
  }
}
```

## Null Value Syntax

Use Workato formula syntax, NOT JSON null:

```json
// CORRECT
"field": "=null"

// WRONG
"field": null
```

## Boolean Error Values

Use string `"false"`, not `"=null"`:

```json
// CORRECT
"success": "false"

// WRONG
"success": "=null"
```

## Common Stripe Error Codes

| Code | Meaning | Recommended Action |
|------|---------|-------------------|
| `card_declined` | Card was declined | Return to user with message |
| `insufficient_funds` | Not enough balance | Return to user |
| `expired_card` | Card has expired | Request new payment method |
| `processing_error` | Temporary processing issue | Retry with backoff |
| `rate_limit` | Too many requests | Retry with exponential backoff |
| `authentication_required` | 3D Secure needed | Return redirect URL |

## Logging Errors

Always log errors before returning:

```json
{
  "keyword": "catch",
  "as": "catch_error",
  "block": [
    {
      "provider": "logger",
      "name": "log_message",
      "as": "log_error",
      "input": {
        "message": "Stripe error: #{_dp('...catch_error...path\":[\"message\"]...')}"
      }
    },
    {
      "provider": "workato_recipe_function",
      "name": "return_result",
      "input": { ... }
    }
  ]
}
```
