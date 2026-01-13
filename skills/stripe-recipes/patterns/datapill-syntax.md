# Stripe Datapill Syntax Patterns

## CRITICAL: Stripe Does NOT Use Body Wrapper

Unlike other HTTP connectors, Stripe custom HTTP actions return responses **without** a `["body"]` wrapper. This is the most common source of errors when writing Stripe recipes.

### Correct Stripe Datapill Paths

```json
// Simple field access
"path": ["id"]
"path": ["status"]
"path": ["email"]

// Nested field access
"path": ["last_payment_error", "code"]
"path": ["last_payment_error", "message"]
"path": ["metadata", "guest_id"]

// Array access
"path": ["data", {"path_element_type":"current_item"}, "id"]
"path": ["charges", "data", {"path_element_type":"current_item"}, "id"]
```

### WRONG: Do Not Use Body Wrapper for Stripe

```json
// INCORRECT - Will return null/empty values
"path": ["body", "id"]
"path": ["body", "status"]
"path": ["body", "data", {"path_element_type":"current_item"}, "id"]
```

## Complete Datapill Format

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"PROVIDER\",\"line\":\"STEP_ALIAS\",\"path\":[PATH_ARRAY]}')}"
```

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| `pill_type` | Always "output" for reading values | `"output"` |
| `provider` | The connector/service name | `"stripe"`, `"workato_recipe_function"` |
| `line` | The step's `as` alias | `"search_customer"`, `"trigger"` |
| `path` | Array of field path elements | `["id"]`, `["parameters", "email"]` |

## Trigger Parameter References

Callable recipes always nest parameters under `["parameters"]`:

```json
{
  "provider": "workato_recipe_function",
  "line": "trigger",
  "path": ["parameters", "field_name"]
}
```

**Full datapill:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"email\"]}')}"
```

## Stripe Action Output References

### Simple Field

```json
// Action definition
{
  "provider": "stripe",
  "as": "create_customer",
  ...
}

// Reference the output
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"id\"]}')}"
```

### Array Access (Search Results)

When accessing items from array responses (like `/v1/customers/search`):

```json
// Use current_item for array iteration
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"search_customer\",\"path\":[\"data\",{\"path_element_type\":\"current_item\"},\"id\"]}')}"
```

**Never use numeric index:**
```json
// WRONG
"path": ["data", "0", "id"]

// CORRECT
"path": ["data", {"path_element_type":"current_item"}, "id"]
```

### Nested Field Access

For nested objects in Stripe responses:

```json
// PaymentIntent.last_payment_error.code
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"confirm_payment\",\"path\":[\"last_payment_error\",\"code\"]}')}"

// Customer.metadata.guest_id
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"metadata\",\"guest_id\"]}')}"
```

## Catch Block Error References

Catch blocks use a special provider:

```json
{
  "provider": "catch",
  "line": "catch_error",  // Must match catch block's "as" value
  "path": ["message"]
}
```

**Full datapill:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"catch\",\"line\":\"catch_error\",\"path\":[\"message\"]}')}"
```

## Comparison: Stripe vs Other Connectors

| Connector | Body Wrapper | Example Path |
|-----------|-------------|--------------|
| Stripe | NO | `["id"]` |
| Generic HTTP | YES | `["body", "id"]` |
| Salesforce | NO (built-in) | `["Contact", {"path_element_type":"current_item"}, "Id"]` |

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Datapill shows empty/null | Using `["body"]` wrapper | Remove `["body"]` from path |
| "invalid step" error | Wrong `line` value | Verify `line` matches target step's `as` |
| "unknown step" error | Missing `as` on target block | Add `"as": "step_name"` to target |
| Array always empty | Using index instead of current_item | Use `{"path_element_type":"current_item"}` |
