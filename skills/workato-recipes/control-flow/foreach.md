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

1. **Empty arrays**: The foreach body doesn't execute if the source array is empty. Plan for this case if you need to return a response.

2. **Unique aliases**: If nesting foreach loops, each must have a unique `as` alias.

3. **Step numbering**: Maintain sequential step numbers even inside the foreach block.

4. **Performance**: For large arrays (100+ items), consider:
   - Using `batch` repeat_mode if operations are independent
   - Implementing pagination in the source query
   - Adding delays to respect rate limits

5. **Variable scope**: With `clear_scope: "true"`, variables from previous iterations are cleared. Use `"false"` if you need to accumulate values.

## Validation Checklist

- [ ] Foreach has `as`, `repeat_mode`, `source`, `block`, `input`
- [ ] Foreach has NO `provider` field
- [ ] `source` is a datapill reference to an array
- [ ] When mapping arrays in return_response, uses `____source` pattern (NOT flat string datapill)
- [ ] `____source` value points to the array datapill
- [ ] Individual field mappings use `{"path_element_type":"current_item"}` in path
- [ ] List counts use `{"path_element_type":"size"}` — NOT `current_item.list_size`

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

## Related Documentation

- [Datapill Syntax](../fundamentals/datapill-syntax.md)
- [Try/Catch Error Handling](try-catch.md)
- [If/Else Conditionals](if-else.md)
