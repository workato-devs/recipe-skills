# Search-Before-Create Pattern

## Purpose

Prevent duplicate records by searching for existing entities before creating new ones. Essential for customer management where the same person may trigger multiple requests.

## Pattern Overview

```
1. Search for existing entity (by email, phone, etc.)
2. If found → Return existing entity
3. If not found → Create new entity
4. Return result with created=true/false indicator
```

## Implementation Structure

### Step 1: Search Action

```json
{
  "provider": "stripe",
  "name": "__adhoc_http_action",
  "as": "search_customer",
  "input": {
    "mnemonic": "Search customers",
    "path": "/v1/customers/search",
    "verb": "get",
    "input": {
      "data": {
        "query": "email:'#{_dp('...parameters.email...')}'",
        "limit": "1"
      }
    },
    "output": "[{\"name\":\"data\",\"type\":\"array\",\"of\":\"object\",\"properties\":[{\"name\":\"id\"},{\"name\":\"email\"}]},{\"name\":\"total_count\",\"type\":\"integer\"}]"
  }
}
```

### Step 2: Check If Found

```json
{
  "keyword": "if",
  "as": "check_found",
  "input": {
    "type": "compound",
    "operand": "and",
    "conditions": [{
      "operand": "present",
      "lhs": "#{_dp('...search_customer...path\":[\"data\",{\"path_element_type\":\"current_item\"},\"id\"]...')}",
      "uuid": "condition-found-001"
    }]
  },
  "block": [
    // Return existing
    // Else: Create new
  ]
}
```

### Step 3: Return Existing (If Found)

```json
{
  "provider": "workato_recipe_function",
  "name": "return_result",
  "as": "return_existing",
  "input": {
    "result": {
      "customer_id": "#{_dp('...search_customer...path\":[\"data\",{\"path_element_type\":\"current_item\"},\"id\"]...')}",
      "email": "#{_dp('...parameters.email...')}",
      "created": "false"
    }
  }
}
```

### Step 4: Create New (Else Block)

```json
{
  "keyword": "else",
  "as": "not_found",
  "block": [
    {
      "provider": "stripe",
      "name": "create_customer",
      "as": "create_customer",
      "input": {
        "email": "#{email}",
        "name": "#{name}",
        "metadata": [
          {"key": "guest_id", "value": "#{guest_id}"},
          {"key": "source", "value": "workato_recipe"}
        ]
      }
    },
    {
      "provider": "workato_recipe_function",
      "name": "return_result",
      "as": "return_created",
      "input": {
        "result": {
          "customer_id": "#{_dp('...create_customer...path\":[\"id\"]...')}",
          "email": "#{email}",
          "created": "true"
        }
      }
    }
  ]
}
```

## Result Schema

Always include a `created` boolean to indicate whether a new record was created:

```json
"result_schema_json": "[{\"name\":\"customer_id\",\"type\":\"string\"},{\"name\":\"email\",\"type\":\"string\"},{\"name\":\"created\",\"type\":\"boolean\"}]"
```

## Complete Flow Diagram

```
Caller Request (email, name, guest_id)
        │
        ▼
┌───────────────────────┐
│ Search Customer API   │
│ /v1/customers/search  │
│ query: email:'...'    │
└───────────────────────┘
        │
        ▼
    Found?
    ┌───┴───┐
   Yes     No
    │       │
    ▼       ▼
┌─────────┐ ┌─────────────┐
│ Return  │ │ Create      │
│ Existing│ │ Customer    │
│ created │ │ /v1/customers│
│ =false  │ └─────────────┘
└─────────┘         │
                    ▼
              ┌─────────┐
              │ Return  │
              │ New     │
              │ created │
              │ =true   │
              └─────────┘
```

## Why This Pattern Matters

### Without Search-Before-Create

1. Guest requests checkout
2. Recipe creates Stripe customer
3. Network timeout, retry triggered
4. Recipe creates another Stripe customer
5. **Result: Duplicate customer records**

### With Search-Before-Create

1. Guest requests checkout
2. Recipe searches for customer
3. Not found → creates customer
4. Network timeout, retry triggered
5. Recipe searches for customer
6. Found → returns existing customer
7. **Result: Single customer record**

## Stripe Search Query Syntax

Stripe uses a special query syntax:

```
email:'john@example.com'
name:'John Doe'
metadata['guest_id']:'12345'
```

### Multiple Conditions

```
email:'john@example.com' AND name:'John'
```

### Escaped Quotes

In Workato JSON, escape quotes properly:

```json
"query": "email:'#{_dp('...email...')}'"
```

## Combined with Idempotency

Search-before-create AND idempotency provide defense in depth:

1. **Search-before-create** - Catches duplicates from sequential retries
2. **Idempotency keys** - Catches duplicates from parallel retries

Both should be used together for robust customer creation.

## Edge Cases

### Race Conditions

If two requests search simultaneously before either creates:
- Both searches return "not found"
- Both attempt to create
- Idempotency key prevents second creation (if same key)
- Or: Stripe email uniqueness constraint catches duplicate

### Email Changes

If customer changes email after creation:
- Old email search returns nothing
- New customer created with new email
- **Solution:** Also store guest_id in metadata for secondary lookup

### Metadata Lookup Pattern

For more robust matching, search by multiple criteria:

```json
{
  "query": "email:'#{email}' OR metadata['guest_id']:'#{guest_id}'"
}
```
