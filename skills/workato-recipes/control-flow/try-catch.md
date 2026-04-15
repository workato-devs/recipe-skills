# Try/Catch Error Handling

## Overview

The try/catch structure enables error handling in Workato recipes. Actions in the try block that fail trigger the catch block, allowing graceful error recovery, logging, or alternative flows.

## JSON Structure

```json
{
  "number": 1,
  "keyword": "try",
  "input": {},
  "block": [
    {
      "number": 2,
      "keyword": "action",
      "provider": "salesforce",
      "name": "create_record",
      "as": "create_contact",
      "input": { ... },
      "uuid": "create-action"
    },
    {
      "number": 3,
      "keyword": "catch",
      "provider": null,
      "as": "catch_error",
      "input": {
        "max_retry_count": "0",
        "retry_interval": "2"
      },
      "block": [
        {
          "number": 4,
          "keyword": "action",
          "provider": "logger",
          "name": "log_message",
          "as": "log_error",
          "input": {
            "message": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"catch\",\"line\":\"catch_error\",\"path\":[\"message\"]}')}"
          },
          "uuid": "log-error-action"
        }
      ],
      "uuid": "catch-uuid"
    }
  ],
  "uuid": "try-uuid"
}
```

## Properties Reference

### Try Block

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `keyword` | string | Yes | Must be `"try"` |
| `number` | integer | Yes | Step number in the recipe |
| `input` | object | Yes | Usually empty `{}` |
| `block` | array | Yes | Actions to attempt (catch is last item) |
| `uuid` | string | Yes | Unique identifier |

**Note:** The try block does NOT have a `provider` field. The `as` field is optional on try blocks — Workato does not enforce it, and validated production recipes omit it. Only the catch block requires `as` (for datapill references to error data).

### Catch Block

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `keyword` | string | Yes | Must be `"catch"` |
| `number` | integer | Yes | Step number (continues from try block) |
| `provider` | null | Yes | Must be explicitly `null` |
| `as` | string | Yes | Alias for referencing error data in datapills |
| `input` | object | Yes | Retry configuration |
| `block` | array | Yes | Error handling actions |
| `uuid` | string | Yes | Unique identifier |

### Catch Input Properties

| Property | Type | Description |
|----------|------|-------------|
| `max_retry_count` | string | Number of retries before executing catch block (0-5) |
| `retry_interval` | string | Seconds between retries |

## Accessing Error Data

Inside the catch block, access error details using the catch's `as` alias:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"catch\",\"line\":\"YOUR_CATCH_ALIAS\",\"path\":[\"message\"]}')}"
```

### Available Error Fields

| Path | Description |
|------|-------------|
| `["message"]` | Error message text |
| `["error_type"]` | Type/category of error |

## Common Patterns

### Basic Error Handling

Log errors and continue:

```json
{
  "number": 1,
  "keyword": "try",
  "input": {},
  "block": [
    {
      "number": 2,
      "keyword": "action",
      "provider": "stripe",
      "name": "create_customer",
      "as": "create_stripe_customer",
      "input": { ... },
      "uuid": "stripe-create"
    },
    {
      "number": 3,
      "keyword": "catch",
      "provider": null,
      "as": "handle_stripe_error",
      "input": {
        "max_retry_count": "0",
        "retry_interval": "2"
      },
      "block": [
        {
          "number": 4,
          "keyword": "action",
          "provider": "logger",
          "name": "log_message",
          "as": "log_stripe_error",
          "input": {
            "message": "=('Stripe error: ' + _dp('{\"pill_type\":\"output\",\"provider\":\"catch\",\"line\":\"handle_stripe_error\",\"path\":[\"message\"]}'))"
          },
          "uuid": "log-error"
        }
      ],
      "uuid": "catch-stripe"
    }
  ],
  "uuid": "try-stripe"
}
```

### With Retry

Retry failed operations before handling error:

```json
{
  "number": 1,
  "keyword": "try",
  "input": {},
  "block": [
    {
      "number": 2,
      "keyword": "action",
      "provider": "salesforce",
      "name": "update_record",
      "as": "update_contact",
      "input": { ... },
      "uuid": "sf-update"
    },
    {
      "number": 3,
      "keyword": "catch",
      "provider": null,
      "as": "catch_sf_error",
      "input": {
        "max_retry_count": "3",
        "retry_interval": "5"
      },
      "block": [
        {
          "number": 4,
          "keyword": "action",
          "provider": "logger",
          "name": "log_message",
          "as": "log_final_error",
          "input": {
            "message": "Failed after 3 retries"
          },
          "uuid": "log-retry-fail"
        }
      ],
      "uuid": "catch-sf"
    }
  ],
  "uuid": "try-sf"
}
```

### Return Error Response (API Endpoint)

For API endpoint recipes, return an error response:

```json
{
  "number": 1,
  "keyword": "try",
  "input": {},
  "block": [
    {
      "number": 2,
      "keyword": "action",
      "provider": "salesforce",
      "name": "create_record",
      "as": "create_contact",
      "input": { ... },
      "uuid": "create-contact"
    },
    {
      "number": 3,
      "keyword": "action",
      "provider": "workato_api_platform",
      "name": "return_response",
      "as": "return_success",
      "input": {
        "http_status_code": "200",
        "response": { "success": "true" }
      },
      "uuid": "success-response"
    },
    {
      "number": 4,
      "keyword": "catch",
      "provider": null,
      "as": "catch_error",
      "input": {
        "max_retry_count": "0",
        "retry_interval": "2"
      },
      "block": [
        {
          "number": 5,
          "keyword": "action",
          "provider": "workato_api_platform",
          "name": "return_response",
          "as": "return_error",
          "input": {
            "http_status_code": "500",
            "response": {
              "success": "false",
              "error": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"catch\",\"line\":\"catch_error\",\"path\":[\"message\"]}')}"
            }
          },
          "uuid": "error-response"
        }
      ],
      "uuid": "catch-block"
    }
  ],
  "uuid": "try-block"
}
```

### Wrapping Foreach in Try/Catch

Handle errors during iteration:

```json
{
  "number": 1,
  "keyword": "try",
  "input": {},
  "block": [
    {
      "number": 2,
      "keyword": "foreach",
      "as": "current_item",
      "repeat_mode": "simple",
      "clear_scope": "false",
      "input": {},
      "source": "#{_dp('...')}",
      "block": [
        {
          "number": 3,
          "keyword": "action",
          "provider": "...",
          "as": "process_item",
          "input": { ... },
          "uuid": "process-action"
        }
      ],
      "uuid": "foreach-loop"
    },
    {
      "number": 4,
      "keyword": "catch",
      "provider": null,
      "as": "catch_loop_error",
      "input": {
        "max_retry_count": "0",
        "retry_interval": "2"
      },
      "block": [
        {
          "number": 5,
          "keyword": "action",
          "provider": "logger",
          "name": "log_message",
          "as": "log_loop_error",
          "input": {
            "message": "Loop failed"
          },
          "uuid": "log-loop-error"
        }
      ],
      "uuid": "catch-loop"
    }
  ],
  "uuid": "try-loop"
}
```

## Gotchas and Best Practices

1. **Catch placement**: The catch block is the LAST item in the try block's `block` array. It is NOT a sibling of the try block.

2. **Provider is null**: The catch block must have `"provider": null` (not omitted, explicitly null).

3. **Retry counts**: Use `"max_retry_count": "0"` to immediately execute catch without retries. Maximum value is typically 5.

4. **Retry interval**: Value is in seconds (as a string). Consider API rate limits when setting this.

5. **Error scope**: The catch block only catches errors from actions within its try block. Errors in the catch block itself are not caught.

6. **Step numbering**: The catch block continues the step numbering sequence from the try block's actions.

7. **Try alias is optional**: The try block does not require an `as` field. Only the catch block needs `as` (for error datapill references).

8. **Return placement**: When using with API endpoints, place the success return inside the try block before the catch, not after.

## Validation Checklist

- [ ] Catch block is the LAST element in the try block's `block` array
- [ ] Catch has `"provider": null` (explicit null, not omitted)
- [ ] Catch has an `as` alias (required for error datapill references)
- [ ] Catch `input` has `max_retry_count` and `retry_interval`
- [ ] Try block has NO `provider` field (`as` is optional)
- [ ] Step numbering continues sequentially from try block through catch block
- [ ] Success return is inside the try block BEFORE the catch (for API endpoint recipes)
- [ ] Catch block provides values for ALL required return fields (use `"=null"` for unavailable data)

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

## Related Documentation

- [Datapill Syntax](../fundamentals/datapill-syntax.md)
- [If/Else Conditionals](if-else.md)
- [Foreach Loops](foreach.md)
- [API Endpoint Trigger](../triggers/api-endpoint.md)
