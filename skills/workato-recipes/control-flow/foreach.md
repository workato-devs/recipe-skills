# Foreach Loop Pattern

## Overview

The `foreach` loop iterates over an array from a previous step, executing a block of actions for each item. This is essential for processing lists of records, transforming collections, or performing batch operations.

## JSON Structure

```json
{
  "number": 3,
  "keyword": "foreach",
  "as": "current_record",
  "repeat_mode": "simple",
  "clear_scope": "false",
  "input": {},
  "source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_results\",\"path\":[\"records\"]}')}",
  "block": [
    {
      "number": 4,
      "keyword": "action",
      "provider": "...",
      "name": "...",
      "as": "...",
      "input": {
        // Reference current item fields via the loop alias
      },
      "uuid": "..."
    }
  ],
  "uuid": "foreach-uuid"
}
```

## Properties Reference

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `keyword` | string | Yes | Must be `"foreach"` |
| `number` | integer | Yes | Step number in the recipe |
| `as` | string | Yes | Alias used to reference the current item in datapills |
| `repeat_mode` | string | Yes | `"simple"` (one at a time) or `"batch"` (parallel processing) |
| `clear_scope` | string | No | `"true"` or `"false"` - clear variables between iterations |
| `source` | string | Yes | Datapill reference to the array to iterate over |
| `block` | array | Yes | Actions to execute for each item |
| `input` | object | Yes | Usually empty `{}` |
| `uuid` | string | Yes | Unique identifier for the step |

## Accessing Current Item Data

Inside the loop body, reference fields from the current item using the loop's `as` alias:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"foreach\",\"line\":\"YOUR_LOOP_ALIAS\",\"path\":[\"field_name\"]}')}"
```

### Examples

**Simple field access:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"foreach\",\"line\":\"current_record\",\"path\":[\"Email\"]}')}"
```

**Nested field access:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"foreach\",\"line\":\"current_record\",\"path\":[\"BillingAddress\",\"City\"]}')}"
```

**Current item marker (explicit):**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_results\",\"path\":[\"records\",{\"path_element_type\":\"current_item\"},\"Name\"]}')}"
```

## Common Patterns

### Iterate Over Search Results

Process each record returned from a Salesforce search:

```json
{
  "number": 2,
  "keyword": "action",
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "search_contacts",
  "input": {
    "sobject_name": "Contact",
    "limit": "100"
  },
  "uuid": "search-uuid"
},
{
  "number": 3,
  "keyword": "foreach",
  "as": "contact",
  "repeat_mode": "simple",
  "clear_scope": "false",
  "input": {},
  "source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_contacts\",\"path\":[\"Contact\"]}')}",
  "block": [
    {
      "number": 4,
      "keyword": "action",
      "provider": "logger",
      "name": "log_message",
      "as": "log_contact",
      "input": {
        "message": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"foreach\",\"line\":\"contact\",\"path\":[\"Email\"]}')}"
      },
      "uuid": "log-uuid"
    }
  ],
  "uuid": "foreach-uuid"
}
```

### Foreach with Error Handling

Wrap the foreach in a try/catch to handle errors gracefully:

```json
{
  "number": 1,
  "keyword": "try",
  "input": {},
  "block": [
    {
      "number": 2,
      "keyword": "foreach",
      "as": "item",
      "repeat_mode": "simple",
      "clear_scope": "false",
      "input": {},
      "source": "#{_dp('...')}",
      "block": [
        // Actions that might fail
      ],
      "uuid": "foreach-uuid"
    },
    {
      "number": 5,
      "keyword": "catch",
      "as": "error_handler",
      "input": {
        "max_retry_count": "0",
        "retry_interval": "2"
      },
      "block": [
        // Error handling actions
      ],
      "uuid": "catch-uuid"
    }
  ],
  "uuid": "try-uuid"
}
```

## Array Mapping Alternative (____source)

For mapping arrays directly in response bodies without explicit iteration, use the `____source` pattern:

```json
{
  "provider": "workato_api_platform",
  "name": "return_response",
  "keyword": "action",
  "input": {
    "http_status_code": "200",
    "response": {
      "rooms": {
        "____source": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_rooms\",\"path\":[\"Hotel_Room__c\"]}')}",
        "Id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_rooms\",\"path\":[\"Hotel_Room__c\",{\"path_element_type\":\"current_item\"},\"Id\"]}')}",
        "Name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_rooms\",\"path\":[\"Hotel_Room__c\",{\"path_element_type\":\"current_item\"},\"Name\"]}')}"
      },
      "count": "#{_dp('{...list_size...}')}"
    }
  }
}
```

**Key points:**
- `____source` specifies the array to map over
- Use `{"path_element_type": "current_item"}` in the path to reference each item's fields
- This pattern is useful for transforming arrays in API responses without side effects
- Use explicit foreach when you need to perform actions (API calls, logging) per item
- **Nested array-of-primitive fields (2+ `current_item` levels deep) get silently stringified, not preserved as arrays** — wrap the primitive in a single-field object before mapping. See the gotcha below.

## Repeat Modes

### Simple Mode (`"simple"`)

Processes items one at a time, sequentially. Use for:
- Operations that depend on order
- When you need to respect API rate limits
- When each iteration might update shared state

### Batch Mode (`"batch"`)

Processes multiple items in parallel. Use for:
- Independent operations that don't affect each other
- Performance-critical bulk processing
- When API rate limits allow concurrent requests

## Gotchas and Best Practices

0. **No block-form filtering (`.select`/`.reject`/`.filter`) on arrays, even nested/complex ones.** Workato's formula engine does not support a `.filter`-style method on arrays — per a community forum answer (not an official Workato statement): ["Can we filter a complex structure?"](https://systematic.workato.com/t5/workato-pros-discussion-board/can-we-filter-a-complex-structure/m-p/5777) ("Workato doesn't support the filter method for arrays, which would allow you [to] block process all of the array's items"). The two alternatives that answer describes: (a) `foreach` + `if` + `insert_to_list` as shown in this doc — fine for a handful of steps; or (b) a single `py_eval` step (see [python-snippets.md](../patterns/python-snippets.md)) once the chain would otherwise span 3+ primitives (declare_list → foreach → if → insert_to_list is already 4) — that forum answer's suggestion for this case is a code-execution action, not a formula.

1. **Empty arrays**: The foreach body doesn't execute if the source array is empty. Plan for this case if you need to return a response.

2. **Unique aliases**: If nesting foreach loops, each must have a unique `as` alias.

3. **Step numbering**: Maintain sequential step numbers even inside the foreach block.

4. **Performance**: For large arrays (100+ items), consider:
   - Using `batch` repeat_mode if operations are independent
   - Implementing pagination in the source query
   - Adding delays to respect rate limits

5. **Variable scope**: With `clear_scope: "true"`, variables from previous iterations are cleared. Use `"false"` if you need to accumulate values.

6. **Array-of-primitive fields nested 2+ `current_item` levels deep get silently stringified, not iterated.** A field that is itself an array of primitives (e.g. `array of string`) nested inside a multi-level `____source`/`current_item` chain — for example `quote[current_item].lines[current_item].serial_numbers` — does not survive as a real array by the time a downstream recipe consumes it. It arrives as literal bracket-and-quote text (e.g. `["f5-leih-pcdc"]`), whether consumed via a `foreach`'s `source` or a `py_eval` structured input. Confirmed from a live recipe pair (2173209 → 2173215, 2026-07-03): `serial_numbers` was mapped as array-of-string at that nesting depth; every downstream consumer received the stringified form, and a `foreach` over it just ran once with the whole string as the single item. **Fix:** wrap the primitive in a single-field object (e.g. `{"serial_number": "..."}` instead of a bare string) so the field becomes array-of-OBJECT — the same `____source`/`current_item` per-field decomposition that already works for object arrays (see "Array Mapping Alternative" above) then works correctly at any nesting depth. This is distinct from the `return_response` list-mapping gotcha in [variables-and-lists.md](../patterns/variables-and-lists.md): that one is single-level and fails by *stripping* the value entirely; this one is multi-level and fails by silently *stringifying* it instead.

## Validation Checklist

- [ ] Foreach has `as`, `repeat_mode`, `source`, `block`, `input`
- [ ] Foreach has NO `provider` field
- [ ] `source` is a datapill reference to an array
- [ ] When mapping arrays in return_response, uses `____source` pattern (NOT flat string datapill)
- [ ] Array-of-primitive fields nested 2+ `current_item` levels deep are wrapped as array-of-object (e.g. `{"field": "value"}`) before being consumed downstream — otherwise they arrive silently stringified
- [ ] `____source` value points to the array datapill
- [ ] Individual field mappings use `{"path_element_type":"current_item"}` in path
- [ ] List counts use `{"path_element_type":"size"}` — NOT `current_item.list_size`

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

## Related Documentation

- [Datapill Syntax](../fundamentals/datapill-syntax.md)
- [Try/Catch Error Handling](try-catch.md)
- [If/Else Conditionals](if-else.md)
- [Python Snippets](../patterns/python-snippets.md) — single-step alternative to a long foreach/if/insert_to_list chain when filtering or transforming a complex/nested array
