# Stripe Recipes Skill - Agent Instructions

> **⚠️ DEPENDENCY: Load `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

This skill provides Stripe-specific knowledge for generating Workato recipes. It extends the **workato-recipes** base skill and focuses on Stripe-specific patterns.

---

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Stripe Config Requirements](#stripe-config-requirements)
3. [Native Stripe Connector Actions](#native-stripe-connector-actions)
4. [Stripe Custom HTTP Actions](#stripe-custom-http-actions)
5. [Stripe Datapill Exception](#stripe-datapill-exception)
6. [Stripe Patterns](#stripe-patterns)
7. [Pre-Push Checklist (Stripe)](#pre-push-checklist-stripe)

---

## When to Use This Skill

Use this skill when building Workato recipes that:
- Create, search, or manage Stripe customers
- Create and confirm PaymentIntents
- Handle 3D Secure authentication flows
- Process refunds for completed payments
- Retrieve payment, subscription, or charge status

**Prerequisites:**
- `workato-recipes` base skill loaded
- Workato workspace with Stripe connection configured

---

## Stripe Config Requirements

Every Stripe recipe requires the `stripe` provider in the config section:

```json
{
  "keyword": "application",
  "provider": "stripe",
  "skip_validation": false,
  "account_id": {
    "zip_name": "Workspace Connections/stripe_connection.connection.json",
    "name": "Stripe Connection Name",
    "folder": "Workspace Connections"
  }
}
```

**Combined with trigger provider:**

For API endpoint trigger:
```json
"config": [
  { "provider": "workato_api_platform", "account_id": null, ... },
  { "provider": "stripe", "account_id": { ... }, ... }
]
```

For callable recipe trigger:
```json
"config": [
  { "provider": "workato_recipe_function", "account_id": null, ... },
  { "provider": "stripe", "account_id": { ... }, ... }
]
```

---

## Native Stripe Connector Actions

The Workato Stripe connector (`provider: "stripe"`) provides **2 agent-usable actions** and **1 trigger**. The native connector has very limited coverage of the Stripe API — most operations require `__adhoc_http_action`.

### Trigger

| Name | Description |
|------|-------------|
| `new_object` | Trigger on new Stripe objects (customers, charges, etc.) |

### Actions

| Name | Description |
|------|-------------|
| `get_customer_by_id` | Retrieve a Stripe customer by their ID |
| `search_charges` | Search for charges with filters |

### Raw HTTP

| Name | Description |
|------|-------------|
| `__adhoc_http_action` | Direct HTTP call to any Stripe API endpoint |

**Use `__adhoc_http_action` for all operations not listed above**, including: customer search/creation, PaymentIntents (create/confirm), refunds, subscriptions, invoices, and payment methods. See [Stripe Custom HTTP Actions](#stripe-custom-http-actions) below for patterns and examples.

---

## Stripe Custom HTTP Actions

### Why Custom HTTP Actions

Given the limited native coverage (2 actions), most Stripe recipes rely on custom HTTP actions (`__adhoc_http_action`). Common operations:

| Endpoint | Use Case |
|----------|----------|
| `/v1/customers/search` | Search customers by email |
| `/v1/payment_intents` | Create PaymentIntents |
| `/v1/payment_intents/{id}/confirm` | Confirm payments with 3D Secure |
| `/v1/refunds` | Create refunds |

### Custom HTTP Action Structure

```json
{
  "number": 2,
  "provider": "stripe",
  "name": "__adhoc_http_action",
  "as": "search_customer",
  "keyword": "action",
  "input": {
    "mnemonic": "Search customers",
    "path": "/v1/customers/search",
    "verb": "get",
    "response_type": "json",
    "input": {
      "schema": "[{\"name\":\"query\",\"type\":\"string\",\"optional\":false,...}]",
      "data": {
        "query": "email:'#{email_datapill}'",
        "limit": "1"
      }
    },
    "output": "[{\"name\":\"data\",\"type\":\"array\",...}]"
  },
  "extended_output_schema": [...],
  "extended_input_schema": [...],  // CRITICAL: See warning below
  "uuid": "search-customer-001"
}
```

> **CRITICAL: extended_input_schema Requirement**
>
> Custom HTTP actions have nested `input.data` structures. The `extended_input_schema` MUST fully define this nested structure or **Workato will silently drop the input data**. See `workato-recipes` base skill for complete documentation.
>
> Always copy `extended_input_schema` from validated templates rather than creating simplified versions.

### HTTP Methods

**GET requests** - Parameters in `input.data`:
```json
{
  "verb": "get",
  "input": {
    "data": { "query": "...", "limit": "1" }
  }
}
```

**POST requests** - Parameters in `input.data` (form-encoded by Stripe):
```json
{
  "verb": "post",
  "input": {
    "data": { "amount": "5000", "currency": "usd", "customer": "cus_xxx" }
  }
}
```

### Idempotency Headers (CRITICAL)

All create/confirm operations MUST include idempotency headers:

```json
{
  "request_headers": [
    {
      "name": "Idempotency-Key",
      "value": "#{idempotency_token_datapill}"
    }
  ]
}
```

**Why:** Retries without idempotency create duplicate customers/charges.

### API Versioning (Recommended)

```json
{
  "request_headers": [
    { "name": "Stripe-Version", "value": "2024-11-20.acacia" }
  ]
}
```

---

## Stripe Datapill Exception

### CRITICAL: No Body Wrapper

**Stripe custom HTTP actions do NOT use the `["body"]` wrapper in datapill paths.**

This is different from other connectors:

```json
// CORRECT for Stripe
"path": ["id"]
"path": ["status"]
"path": ["data", {"path_element_type":"current_item"}, "id"]
"path": ["last_payment_error", "code"]

// WRONG for Stripe - Do NOT use
"path": ["body", "id"]
```

### Stripe Datapill Examples

**Customer ID from search:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"search_customer\",\"path\":[\"data\",{\"path_element_type\":\"current_item\"},\"id\"]}')}"
```

**Customer ID from create:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"id\"]}')}"
```

**PaymentIntent status:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_payment\",\"path\":[\"status\"]}')}"
```

**Error code from failed payment:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"confirm_payment\",\"path\":[\"last_payment_error\",\"code\"]}')}"
```

---

## Stripe Patterns

### 1. Search-Before-Create (Customer Deduplication)

Always search for existing customer before creating:

```json
// Step 1: Search
{
  "provider": "stripe",
  "name": "__adhoc_http_action",
  "as": "search_customer",
  "input": {
    "path": "/v1/customers/search",
    "verb": "get",
    "input": {
      "data": { "query": "email:'#{email}'", "limit": "1" }
    }
  }
}

// Step 2: Check if found
{
  "keyword": "if",
  "input": {
    "conditions": [{
      "operand": "present",
      "lhs": "#{search_customer.data[].id}"
    }]
  },
  "block": [
    // Return existing
    { "name": "return/response", "input": { "customer_id": "#{existing}", "created": "false" } },
    // Else: Create new
    { "keyword": "else", "block": [ /* create customer */ ] }
  ]
}
```

### 2. Error Response Flattening

Stripe errors have nested structure. Flatten for responses:

```json
// Stripe returns:
{ "error": { "code": "card_declined", "message": "...", "decline_code": "..." } }

// Flatten in your response schema:
{ "success": false, "error_code": "card_declined", "error_message": "...", "decline_code": "..." }
```

### 3. Amount Validation

Stripe requires minimum $0.50 (50 cents):

```json
{
  "keyword": "if",
  "input": {
    "conditions": [{ "operand": "less_than", "lhs": "#{amount}", "rhs": "50" }]
  },
  "block": [
    { "name": "response", "input": { "error": "Amount must be at least 50 cents" } }
  ]
}
```

### 4. 3D Secure Handling

PaymentIntent status after confirm indicates auth requirement:

| Status | Meaning | Action |
|--------|---------|--------|
| `succeeded` | Payment complete | Return success |
| `requires_action` | 3D Secure needed | Return `next_action.redirect_to_url.url` |
| `requires_payment_method` | Failed | Return error |

---

## Pre-Push Checklist (Stripe)

### Stripe-Specific Checks

- [ ] Config includes `stripe` provider with connection reference
- [ ] Custom HTTP actions use `"name": "__adhoc_http_action"`
- [ ] Create/confirm actions include `Idempotency-Key` header
- [ ] Datapill paths do NOT include `["body"]` wrapper
- [ ] Search results use `["data", {"path_element_type":"current_item"}, "id"]`
- [ ] **CRITICAL:** `extended_input_schema` fully defines nested `input.data` structure (see base skill)

### Common Stripe Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "invalid step" | Wrong datapill path | Remove `["body"]` wrapper |
| Duplicate customers | Missing idempotency | Add `Idempotency-Key` header |
| Empty search results | Wrong array access | Use `{"path_element_type":"current_item"}` |
| Missing API params | Incomplete `extended_input_schema` | Ensure schema defines all nested `input.data` fields |
| Input silently dropped | Schema missing nested objects | Copy complete schema from templates |

---

## Templates

See `templates/` directory:
- `create-customer.json` - Search-before-create pattern
- `confirm-payment.json` - PaymentIntent confirmation with 3D Secure
- `create-refund.json` - Refund processing

---

## References

- **Base Skill:** `workato-recipes` - Recipe structure, triggers, control flow
- **Templates:** `templates/` directory
- **Patterns:** `patterns/` directory
- **Stripe API:** https://stripe.com/docs/api
