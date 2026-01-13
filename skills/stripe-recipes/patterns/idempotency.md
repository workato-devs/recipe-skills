# Stripe Idempotency Patterns

## Why Idempotency Matters

Without idempotency keys:
- Retried requests create duplicate customers
- Failed-then-succeeded payments charge twice
- Network timeouts lead to unknown state

With idempotency keys:
- Same key = same result (no duplicates)
- Safe to retry any operation
- Predictable behavior under failures

## Idempotency Key Requirements

### Always Include for Create Operations

- `/v1/customers` - Create customer
- `/v1/payment_intents` - Create PaymentIntent
- `/v1/payment_intents/{id}/confirm` - Confirm payment
- `/v1/refunds` - Create refund
- `/v1/subscriptions` - Create subscription
- `/v1/charges` - Create charge (legacy)

### Not Required for Read Operations

- `/v1/customers/{id}` - Retrieve customer
- `/v1/payment_intents/{id}` - Retrieve PaymentIntent
- `/v1/customers/search` - Search customers

## Recipe Parameter Pattern

Always require `idempotency_token` as input:

```json
"parameters_schema_json": "[...,{\"name\":\"idempotency_token\",\"label\":\"Idempotency token\",\"type\":\"string\",\"control_type\":\"text\",\"optional\":false,\"hint\":\"Client-generated UUID for safe retries\"}]"
```

## Custom HTTP Header Pattern

```json
{
  "provider": "stripe",
  "name": "__adhoc_http_action",
  "input": {
    "path": "/v1/customers",
    "verb": "post",
    "headers": {
      "Idempotency-Key": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"idempotency_token\"]}')}"
    },
    "input": { ... }
  }
}
```

## Built-in Action Pattern

For built-in Stripe connector actions, pass idempotency via `request_headers`:

```json
{
  "provider": "stripe",
  "name": "create_customer",
  "input": {
    "email": "...",
    "request_headers": [
      {
        "name": "Idempotency-Key",
        "value": "#{idempotency_token}"
      }
    ]
  }
}
```

## Idempotency Key Generation

Callers should generate unique keys. Recommended patterns:

### UUID v4
```
550e8400-e29b-41d4-a716-446655440000
```

### Composite Key
```
booking-checkout-{booking_id}-{timestamp}
```

### Hash-based
```
sha256(guest_email + amount + timestamp)
```

## Idempotency Key Lifetime

Stripe retains idempotency keys for 24 hours. After that:
- Same key with same parameters = new request
- Same key with different parameters = error

## Error Handling with Idempotency

### Same Key, Different Parameters

```json
{
  "error": {
    "type": "idempotency_error",
    "message": "Keys for idempotent requests can only be used with the same parameters"
  }
}
```

**Solution:** Generate new idempotency key for different parameters.

### Same Key, Same Parameters (Retry)

No error - Stripe returns the original response.

## Best Practices

1. **Always pass from orchestrator** - Let the calling system generate and track keys
2. **Use UUIDs** - Simplest approach, guaranteed unique
3. **Include in logs** - Log the idempotency key for debugging
4. **Document in API** - Make idempotency_token required in your recipe's input schema
5. **Don't generate in recipe** - Let caller control retry behavior

## Example: Full Idempotent Create Customer

```json
{
  "name": "Create Stripe customer",
  "code": {
    "input": {
      "parameters_schema_json": "[{\"name\":\"email\",...},{\"name\":\"name\",...},{\"name\":\"idempotency_token\",\"optional\":false,...}]"
    },
    "block": [
      {
        "provider": "stripe",
        "name": "__adhoc_http_action",
        "as": "create_customer",
        "input": {
          "path": "/v1/customers",
          "verb": "post",
          "headers": {
            "Idempotency-Key": "#{_dp('...idempotency_token...')}"
          },
          "input": {
            "data": {
              "email": "#{email}",
              "name": "#{name}"
            }
          }
        }
      }
    ]
  }
}
```
