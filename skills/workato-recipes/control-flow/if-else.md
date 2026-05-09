# If/Else Conditional

## Overview

The if/else structure enables conditional branching in Workato recipes. Actions execute based on whether conditions evaluate to true or false. The else block is nested inside the if block's array, not as a separate property.

## JSON Structure

```json
{
  "number": 3,
  "keyword": "if",
  "as": "check_condition",
  "input": {
    "type": "compound",
    "operand": "and",
    "conditions": [
      {
        "operand": "present",
        "lhs": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_results\",\"path\":[\"Id\"]}')}",
        "uuid": "condition-uuid"
      }
    ]
  },
  "block": [
    {
      "number": 4,
      "keyword": "action",
      "provider": "logger",
      "name": "log_message",
      "as": "log_found",
      "input": {
        "message": "Record found"
      },
      "uuid": "action-if-true"
    },
    {
      "number": 5,
      "keyword": "else",
      "as": "else_branch",
      "input": {},
      "block": [
        {
          "number": 6,
          "keyword": "action",
          "provider": "logger",
          "name": "log_message",
          "as": "log_not_found",
          "input": {
            "message": "Record not found"
          },
          "uuid": "action-if-false"
        }
      ],
      "uuid": "else-uuid"
    }
  ],
  "uuid": "if-uuid"
}
```

## Properties Reference

### If Block

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `keyword` | string | Yes | Must be `"if"` |
| `number` | integer | Yes | Step number in the recipe |
| `as` | string | Yes | Alias for the if block |
| `input` | object | Yes | Condition configuration |
| `block` | array | Yes | Actions to execute (includes else as last item) |
| `uuid` | string | Yes | Unique identifier |

### Else Block

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `keyword` | string | Yes | Must be `"else"` |
| `number` | integer | Yes | Step number (continues from if block) |
| `as` | string | Yes | Alias for the else block |
| `input` | object | Yes | Usually empty `{}` |
| `block` | array | Yes | Actions to execute when condition is false |
| `uuid` | string | Yes | Unique identifier |

**CRITICAL:** If and else blocks do NOT have a `provider` field.

## Condition Input Structure

The `input` object defines conditions using this structure:

```json
"input": {
  "type": "compound",
  "operand": "and",
  "conditions": [
    {
      "operand": "equals",
      "lhs": "#{datapill}",
      "rhs": "expected_value",
      "uuid": "cond-uuid-1"
    }
  ]
}
```

### Compound Condition Properties

| Property | Type | Description |
|----------|------|-------------|
| `type` | string | Always `"compound"` |
| `operand` | string | `"and"` or `"or"` to combine conditions |
| `conditions` | array | Array of condition objects |

### Single Condition Properties

| Property | Type | Description |
|----------|------|-------------|
| `operand` | string | Comparison operator |
| `lhs` | string | Left-hand side (usually a datapill) |
| `rhs` | string | Right-hand side (optional, depends on operand) |
| `uuid` | string | Unique identifier for the condition |

## Condition Operands

| Operand | Description | Requires RHS |
|---------|-------------|--------------|
| `present` | Value exists and is not empty | No |
| `blank` | Value is null or empty | No |
| `equals` | LHS equals RHS | Yes |
| `not_equals` | LHS does not equal RHS | Yes |
| `greater_than` | LHS > RHS | Yes |
| `less_than` | LHS < RHS | Yes |
| `contains` | LHS contains RHS | Yes |
| `starts_with` | LHS starts with RHS | Yes |
| `ends_with` | LHS ends with RHS | Yes |

## Common Patterns

### Check if Record Exists

```json
{
  "number": 2,
  "keyword": "if",
  "as": "check_exists",
  "input": {
    "type": "compound",
    "operand": "and",
    "conditions": [
      {
        "operand": "present",
        "lhs": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_contact\",\"path\":[\"Id\"]}')}",
        "uuid": "cond-exists"
      }
    ]
  },
  "block": [
    {
      "number": 3,
      "keyword": "action",
      "provider": "salesforce",
      "name": "update_record",
      "as": "update_existing",
      "input": { ... },
      "uuid": "update-action"
    },
    {
      "number": 4,
      "keyword": "else",
      "as": "else_create",
      "input": {},
      "block": [
        {
          "number": 5,
          "keyword": "action",
          "provider": "salesforce",
          "name": "create_record",
          "as": "create_new",
          "input": { ... },
          "uuid": "create-action"
        }
      ],
      "uuid": "else-uuid"
    }
  ],
  "uuid": "if-exists"
}
```

### Multiple Conditions (AND)

```json
"input": {
  "type": "compound",
  "operand": "and",
  "conditions": [
    {
      "operand": "present",
      "lhs": "#{_dp('{...email...}')}",
      "uuid": "cond-1"
    },
    {
      "operand": "equals",
      "lhs": "#{_dp('{...status...}')}",
      "rhs": "active",
      "uuid": "cond-2"
    }
  ]
}
```

### Multiple Conditions (OR)

```json
"input": {
  "type": "compound",
  "operand": "or",
  "conditions": [
    {
      "operand": "equals",
      "lhs": "#{_dp('{...type...}')}",
      "rhs": "premium",
      "uuid": "cond-1"
    },
    {
      "operand": "equals",
      "lhs": "#{_dp('{...type...}')}",
      "rhs": "enterprise",
      "uuid": "cond-2"
    }
  ]
}
```

### If Without Else

The else block is optional:

```json
{
  "number": 2,
  "keyword": "if",
  "as": "check_valid",
  "input": {
    "type": "compound",
    "operand": "and",
    "conditions": [
      {
        "operand": "present",
        "lhs": "#{_dp('{...email...}')}",
        "uuid": "cond-valid"
      }
    ]
  },
  "block": [
    {
      "number": 3,
      "keyword": "action",
      "provider": "logger",
      "name": "log_message",
      "as": "log_valid",
      "input": {
        "message": "Email is valid"
      },
      "uuid": "log-valid"
    }
  ],
  "uuid": "if-valid"
}
```

### Nested If/Else

```json
{
  "number": 2,
  "keyword": "if",
  "as": "outer_check",
  "input": { ... },
  "block": [
    {
      "number": 3,
      "keyword": "if",
      "as": "inner_check",
      "input": { ... },
      "block": [
        { "number": 4, "keyword": "action", ... },
        {
          "number": 5,
          "keyword": "else",
          "as": "inner_else",
          "input": {},
          "block": [
            { "number": 6, "keyword": "action", ... }
          ],
          "uuid": "inner-else"
        }
      ],
      "uuid": "inner-if"
    },
    {
      "number": 7,
      "keyword": "else",
      "as": "outer_else",
      "input": {},
      "block": [
        { "number": 8, "keyword": "action", ... }
      ],
      "uuid": "outer-else"
    }
  ],
  "uuid": "outer-if"
}
```

### Multi-Way Branching (else-if chains)

Workato does **NOT** support `elsif` as a keyword. To implement multi-way branching (if/else-if/else), nest a new `if` block inside the `else` block:

```json
{
  "number": 2,
  "keyword": "if",
  "as": "check_first",
  "input": {
    "type": "compound",
    "operand": "and",
    "conditions": [
      { "operand": "equals", "lhs": "#{_dp('{...status...}')}", "rhs": "active", "uuid": "cond-active" }
    ]
  },
  "block": [
    { "number": 3, "keyword": "action", "provider": "logger", "name": "log_message", "as": "log_active", "input": { "message": "Active" }, "uuid": "log-active" },
    {
      "number": 4,
      "keyword": "else",
      "as": "else_not_active",
      "input": {},
      "block": [
        {
          "number": 5,
          "keyword": "if",
          "as": "check_second",
          "input": {
            "type": "compound",
            "operand": "and",
            "conditions": [
              { "operand": "equals", "lhs": "#{_dp('{...status...}')}", "rhs": "pending", "uuid": "cond-pending" }
            ]
          },
          "block": [
            { "number": 6, "keyword": "action", "provider": "logger", "name": "log_message", "as": "log_pending", "input": { "message": "Pending" }, "uuid": "log-pending" },
            {
              "number": 7,
              "keyword": "else",
              "as": "else_default",
              "input": {},
              "block": [
                { "number": 8, "keyword": "action", "provider": "logger", "name": "log_message", "as": "log_other", "input": { "message": "Other" }, "uuid": "log-other" }
              ],
              "uuid": "else-default"
            }
          ],
          "uuid": "if-pending"
        }
      ],
      "uuid": "else-not-active"
    }
  ],
  "uuid": "if-active"
}
```

Each additional branch adds one nesting level: `else` > `if` > (actions + `else` > `if` > ...).

## Gotchas and Best Practices

1. **Else placement**: The else block is the LAST item in the if block's `block` array. It is NOT a sibling of the if block or a property on it.

2. **No provider field**: If and else blocks do NOT have a `provider` field. Including one will cause errors.

3. **Condition UUIDs**: Each condition in the `conditions` array needs its own unique UUID.

4. **Step numbering**: Steps inside the if block continue the sequence. The else block and its contents also continue the same sequence.

5. **Empty else input**: The else block's `input` is always an empty object `{}`.

6. **Present vs blank**: Use `present` to check for existence, `blank` for the opposite. These don't require an `rhs` value.

7. **String comparison**: The `equals` operand performs string comparison. Ensure both sides are the same type.

8. **`elsif` is NOT a valid keyword**: Workato does not support `elsif`. Using it causes the block to render as "misconfigured" in the UI. For multi-way branching, nest a new `if` inside the `else` block (see Multi-Way Branching pattern above).

9. **Condition LHS: NO formula mode**: The `lhs` field in conditions does **NOT** support formula mode (`=` prefix). It only supports `#{_dp(...)}` interpolation. Using formula mode (e.g., `"lhs": "=' ' + _dp('...').upcase + ' '"`) strips app recognition from child actions, causing them to display "select app and action" in the UI. To transform data before comparing, use a `declare_variable` step (see [variables-and-lists.md](../patterns/variables-and-lists.md)) to pre-compute the value, then reference it with `#{_dp(...)}` in the condition LHS.

## Validation Checklist

- [ ] No `elsif` keyword anywhere — use nested `else` > `if` instead
- [ ] Condition `lhs` values use `#{_dp(...)}` interpolation only (no `=` formula mode prefix)
- [ ] Every `if` block has `keyword: "if"` with NO `provider` field
- [ ] Every `else` block has `keyword: "else"` with NO `provider` field and `input: {}`
- [ ] `else` is always the LAST item in the parent `if` block's `block` array
- [ ] Each condition has its own unique `uuid`
- [ ] Compound conditions have `type: "compound"` and an `operand` of `"and"` or `"or"`

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

## Related Documentation

- [Stop Action](stop.md) — commonly used inside else blocks for input validation
- [Datapill Syntax](../fundamentals/datapill-syntax.md)
- [Try/Catch Error Handling](try-catch.md)
- [Foreach Loops](foreach.md)
