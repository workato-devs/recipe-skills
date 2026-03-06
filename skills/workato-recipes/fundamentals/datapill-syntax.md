# Datapill Syntax

## Overview

Datapills are references to data from previous steps in a Workato recipe. They enable dynamic values by pulling data from triggers, actions, and control flow iterations into subsequent steps.

## JSON Structure

Datapills use a specific format with the `_dp()` function:

```
#{_dp('{JSON_OBJECT}')}
```

The JSON object inside defines which data to reference:

```json
{
  "pill_type": "output",
  "provider": "PROVIDER_NAME",
  "line": "STEP_ALIAS",
  "path": ["field", "nested_field"]
}
```

## Properties Reference

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `pill_type` | string | Yes | Always `"output"` for referencing step outputs |
| `provider` | string | Yes | The provider name of the source step |
| `line` | string | Yes | The `as` alias of the source step |
| `path` | array | Yes | Path to the specific field (supports nesting) |

## Provider Names by Step Type

| Step Type | Provider Value |
|-----------|----------------|
| API endpoint trigger | `workato_api_platform` |
| Callable recipe trigger | `workato_recipe_function` |
| Salesforce action | `salesforce` |
| Stripe action | `stripe` |
| Foreach current item | `foreach` |
| Catch block error | `catch` |

## Common Patterns

### Trigger Parameter (Callable Recipe)

Access input parameters from a callable recipe trigger:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"email\"]}')}"
```

### Trigger Parameter (API Endpoint)

Access request fields from an API endpoint trigger:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"email\"]}')}"
```

**Note:** For API endpoint triggers, fields are accessed directly under `request` (NOT `request.body`).

### Action Output

Reference a field from a previous action's output:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"id\"]}')}"
```

### Nested Field Access

For deeply nested data, extend the path array:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"get_contact\",\"path\":[\"BillingAddress\",\"City\"]}')}"
```

### Foreach Current Item

Inside a foreach loop, reference the current item using `provider: "foreach"` and the loop's alias:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"foreach\",\"line\":\"current_record\",\"path\":[\"Email\"]}')}"
```

### Array Element Access (Explicit)

When you need to explicitly reference an array item:

```json
"path": ["data", {"path_element_type": "current_item"}, "id"]
```

### Catch Block Error

Access error details in a catch block:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"catch\",\"line\":\"catch_error\",\"path\":[\"message\"]}')}"
```

## Multiple Datapills in One Field

When you need to combine multiple datapills, use formula mode (`=` prefix) with Ruby concatenation:

**WRONG (mixing interpolation with concatenation):**
```json
"guest_name": "#{_dp('{...first_name...}')} + ' ' + _dp('{...last_name...}'}"
```

**CORRECT (formula mode with Ruby + operator):**
```json
"guest_name": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"first_name\"]}') + ' ' + _dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"last_name\"]}')"
```

**Key rules:**
- Use `=` prefix (formula mode) for concatenation
- Do NOT wrap with `#{}`
- Use Ruby `+` operator between strings
- Literal strings must be quoted: `' '` or `'-'`

## Conditional Datapill Usage

Use `.present?` checks with ternary operator to conditionally use datapills:

```json
"FirstName": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"first_name\"]}').present? ? _dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"first_name\"]}') : skip"
```

**Pattern:**
```
=datapill.present? ? datapill : skip
```

- `present?` - Checks if value exists and is not empty
- `skip` - Special keyword to exclude field from the action

---

## Ternary Syntax for Multiple Sources

When a value could come from **2 possible sources** (e.g., a search result OR a create result), use Ruby ternary syntax directly in the datapill mapping.

### Pattern

```
=(_dp('{...source1...}').present? ? _dp('{...source1...}') : _dp('{...source2...}'))
```

### Example: Search Result or Create Result

```json
"customer_id": "=(_dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"search_customer\",\"path\":[\"data\",{\"path_element_type\":\"current_item\"},\"id\"]}').present? ? _dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"search_customer\",\"path\":[\"data\",{\"path_element_type\":\"current_item\"},\"id\"]}') : _dp('{\"pill_type\":\"output\",\"provider\":\"stripe\",\"line\":\"create_customer\",\"path\":[\"id\"]}'))"
```

### Advantages Over Variables

- No intermediate variables or config entries needed
- Works reliably across multi-connector recipes
- Cleaner recipe structure with fewer actions
- No datapill resolution issues

### When to Use Variables Instead

For **3 or more sources**, or when accumulating values in a loop, use the `workato_variable` provider instead. See [patterns/variables-and-lists.md](../patterns/variables-and-lists.md)

## Gotchas and Best Practices

1. **JSON escaping**: The JSON inside `_dp()` must have escaped quotes (`\"`). This is because the entire datapill string is itself inside a JSON value.

2. **Line alias matching**: The `line` value must exactly match the `as` field of the source step.

3. **Case sensitivity**: Field names in the `path` array are case-sensitive. Use exact field names from the source.

4. **Trigger alias**: For callable recipe triggers, the line is always `"trigger"`. For API endpoint triggers, use the `as` value you defined.

5. **Formula vs interpolation**: Use `#{}` syntax for single datapills, but switch to `=` prefix when using formula methods like `.present?` or concatenation.

6. **Path array order**: The path array represents the traversal order through the object. `["request", "body", "email"]` means `request.body.email`.

7. **Formula mode: NO outer parentheses**: When using `=` formula mode, do NOT wrap the entire expression in parentheses. Use `=' ' + expr + ' '` not `=(' ' + expr + ' ')`. Outer parentheses break the Workato parser — child actions lose app recognition and display "select app and action" in the UI. The only valid use of outer `()` is in ternary expressions: `=(expr.present? ? a : b)`.

8. **Condition LHS: NO formula mode**: The `lhs` field in if/else conditions does NOT support `=` formula mode — only `#{_dp(...)}` interpolation. See [if-else.md](../control-flow/if-else.md) for details and workarounds.

9. **No `.parse_json['key']` bracket notation in formulas**: Chaining `['field']` after `.parse_json` in a formula causes validation errors. Instead, define response fields in `extended_output_schema` and reference them via datapill path. See [adhoc-http-actions.md](../patterns/adhoc-http-actions.md#json-response-handling-nested-data-extraction) for the correct pattern using `parse_json_v2`.

10. **`now.utc` is invalid**: The `.utc` method is not available on Workato's `now` object. For ISO 8601 UTC timestamps, use `now.strftime('%Y-%m-%dT%H:%M:%SZ')`.

## Validation

See [validation-checklist.md](../validation-checklist.md) for consolidated validation.

## Related Documentation

- [Recipe Structure](recipe-structure.md)
- [Foreach Loop](../control-flow/foreach.md)
- [If/Else Conditions](../control-flow/if-else.md)
