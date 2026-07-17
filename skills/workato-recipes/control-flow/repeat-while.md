# Repeat While Loop Pattern

## Overview

The `repeat` loop runs a block of actions repeatedly until a condition is met. Unlike [`foreach`](foreach.md), which iterates over a known array, `repeat` is used when the number of iterations is **not known in advance** — keyset/cursor pagination, polling until a resource is ready, or draining a queue.

The defining structural fact: **the exit condition is not a property of the repeat step.** It is a separate child block, with `keyword: "while_condition"`, placed as the **last item** in the repeat block's `block` array. The actions to repeat come before it. Without this `while_condition` child, the loop has no exit clause and the Workato UI cannot reconstruct it after `wk push`.

## JSON Structure

```json
{
  "number": 1,
  "as": "page_loop",
  "keyword": "repeat",
  "block": [
    {
      "number": 2,
      "provider": "asana",
      "name": "list_all_tasks_with_tag",
      "as": "list_tasks",
      "keyword": "action",
      "input": {},
      "uuid": "list-tasks-001"
    },
    {
      "number": 3,
      "keyword": "while_condition",
      "input": {
        "type": "compound",
        "operand": "and",
        "conditions": [
          {
            "operand": "present",
            "lhs": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"asana\",\"line\":\"list_tasks\",\"path\":[\"next_page\"]}')}",
            "rhs": "",
            "uuid": "loop-condition-001"
          }
        ]
      },
      "uuid": "while-condition-001"
    }
  ],
  "uuid": "page-loop-001"
}
```

> **UUIDs and `as` aliases above are descriptive placeholders, per the repo convention** ([SKILL.md UUID Guidelines](../SKILL.md), `UUID_DESCRIPTIVE` lint rule). When you build a loop in the Workato UI and export it, the UI auto-generates v4 hex UUIDs (e.g. `164ab826-…`) and hex `as` tokens (e.g. `eaed46bb`) — those are the anti-pattern the linter flags. Replace them with descriptive names (≤36 chars) like the ones shown here.
>
> The condition `lhs`/`operand`/`rhs` values are illustrative. The verified sample this pattern is drawn from had placeholder condition internals; the loop *shape* (keyword, block layout, `while_condition` placement, field names) is ground truth from a declarative-builder export. Build and export a populated loop to confirm condition internals for your case.

## Properties Reference

### Repeat Block

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `keyword` | string | Yes | Must be `"repeat"` |
| `number` | integer | Yes | Step number in the recipe |
| `as` | string | Yes | Descriptive alias for the loop block (e.g. `page_loop`) |
| `block` | array | Yes | Actions to repeat, followed by the `while_condition` block as the last item |
| `uuid` | string | Yes | Unique identifier — descriptive name, ≤36 chars (e.g. `page-loop-001`) |

**CRITICAL — fields the repeat block does NOT have:**
- NO `provider` field. (A loop is control flow, not an app action.)
- NO `name` field.
- NO `repeat_mode` / `clear_scope`. Those belong to [`foreach`](foreach.md), not `repeat`.

### While Condition Block

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `keyword` | string | Yes | Must be `"while_condition"` |
| `number` | integer | Yes | Step number — continues the sequence, last in the block |
| `input` | object | Yes | Compound condition object (same shape as an `if` condition) |
| `uuid` | string | Yes | Unique identifier — descriptive name, ≤36 chars (e.g. `while-condition-001`) |

The `while_condition` block has NO `provider`, NO `name`, and NO `as`. The loop continues while the condition evaluates true.

## Condition Input Structure

The `while_condition`'s `input` uses the same compound-condition structure as [`if`/`else`](if-else.md):

```json
"input": {
  "type": "compound",
  "operand": "and",
  "conditions": [
    {
      "operand": "present",
      "lhs": "#{_dp('{...cursor/next-page datapill...}')}",
      "rhs": "",
      "uuid": "cond-uuid"
    }
  ]
}
```

For the full operand table (`present`, `blank`, `equals_to`, `greater_than`, etc.), RHS requirements, and the "no formula mode in `lhs`" rule, see [if-else.md](if-else.md#condition-operands). The same rules apply here.

## Common Patterns

### Keyset / Cursor Pagination

The canonical use: fetch a page, then loop while the API reports more results. Typical loop body —

1. An action that fetches the next page (using a cursor/page-token from a variable or the previous iteration's output).
2. Processing of that page (often a nested [`foreach`](foreach.md) over the page's records).
3. Update the cursor variable for the next iteration.
4. The `while_condition` block, last, testing whether the cursor/next-page token is still `present`.

```json
{
  "number": 4,
  "as": "page_loop",
  "keyword": "repeat",
  "block": [
    {
      "number": 5,
      "provider": "salesforce",
      "name": "search_sobjects",
      "as": "fetch_page",
      "keyword": "action",
      "input": { "...": "...query using the cursor..." },
      "uuid": "..."
    },
    {
      "number": 6,
      "keyword": "while_condition",
      "input": {
        "type": "compound",
        "operand": "and",
        "conditions": [
          {
            "operand": "present",
            "lhs": "#{_dp('{...next-cursor datapill...}')}",
            "rhs": "",
            "uuid": "..."
          }
        ]
      },
      "uuid": "..."
    }
  ],
  "uuid": "..."
}
```

> Note from the golden recipes: the declarative builder uses [`foreach`](foreach.md) for iterating over results that are already in hand. Reach for `repeat` only when iteration count is genuinely unknown ahead of time (pagination, polling). When in doubt, prefer `foreach`.

## Common Malformations

These are the field-level mistakes that pass JSON validation and even the visualizer but cause the loop to fail to reconstruct in the Workato UI after `wk push`:

| Malformation | Correct |
|---|---|
| `"uid": "loop-paginate-001"` | `"uuid": "page-loop-001"` — the key is `uuid` (not `uid`); value is a descriptive name ≤36 chars |
| `"provider": "loop"` on the repeat block | no `provider` field |
| `"name": "repeat_while"` on the repeat block | no `name` field |
| inline `"condition": "#{...} == 1"` string on the repeat block | a separate `while_condition` child block with a compound `input`, placed last |

The last row is the critical one: an inline condition string has no `while_condition` block for the UI to render, so the loop appears to deploy (JSON is valid, visualizer is permissive) but collapses on UI reconstruction.

## Gotchas and Best Practices

1. **`while_condition` is the last block item**, not a property on the repeat step and not a sibling of it.

2. **Use `uuid`, not `uid`.** The value should be a **descriptive name** (≤36 chars, e.g. `page-loop-001`), NOT an auto-generated v4 hex UUID. The UI emits hex UUIDs on export; the linter flags those via `UUID_DESCRIPTIVE`. Do not copy them into authored recipes.

3. **No `provider`/`name` on control-flow blocks.** Both the `repeat` and `while_condition` blocks omit them.

4. **Guard against infinite loops.** The condition must eventually become false. For pagination, ensure the cursor advances each iteration; consider a max-pages safeguard variable checked in the condition.

5. **Step numbering** continues sequentially through the loop body and the `while_condition` block.

6. **Variables don't persist across recipe runs** — only within a single run's loop iterations. Use a [Data/Lookup table](../patterns/variables-and-lists.md) if you need state across runs.

## Validation Checklist

- [ ] Repeat block has `keyword: "repeat"`, `as`, `block`, `uuid` — and NO `provider`, `name`, `repeat_mode`, or `clear_scope`
- [ ] `uuid` (not `uid`) is present and is a descriptive name ≤36 chars — NOT an auto-generated v4 hex UUID
- [ ] The loop body ends with a `while_condition` block as the LAST item in `block`
- [ ] The `while_condition` block has `keyword: "while_condition"`, a compound `input`, a `uuid`, and NO `provider`/`name`/`as`
- [ ] The exit condition can actually become false (cursor advances / safeguard present)
- [ ] Condition `lhs` uses `#{_dp(...)}` interpolation only (no `=` formula mode)

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).

## Related Documentation

- [Foreach Loops](foreach.md)
- [If/Else Conditionals](if-else.md)
- [Datapill Syntax](../fundamentals/datapill-syntax.md)
- [Variables and Lists](../patterns/variables-and-lists.md)
