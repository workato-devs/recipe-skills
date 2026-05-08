# Python Snippets

Workato's "Python snippets by Workato" connector exposes a `py_eval` provider with an `invoke_custom_py_code` action that runs arbitrary Python inside a recipe step. This pattern is **strongly preferred** over formula chains and `parse_json_v2` for any non-trivial data transformation.

---

## When to Use Python

Use `py_eval` when:

- Walking nested JSON structures (especially arrays-of-arrays from `parse_json_v2`)
- Extracting positional elements from arrays — datapill paths can't index arrays (see [datapill-syntax.md](../fundamentals/datapill-syntax.md#array-element-access-explicit))
- Building HTTP request bodies that need integer typing or operator-style keys (see [adhoc-http-actions.md](./adhoc-http-actions.md#raw-json-body-with-datapills) Pattern 1)
- Conditional logic more involved than a single ternary
- String manipulation (regex extraction, normalization, parsing)
- Any transformation that would otherwise span 3+ chained Workato primitives (`make_request_v2` → `parse_json_v2` → `declare_variable` → `update_variables` → ...)

Use the formula/datapill chain when:

- The transformation is a one-liner field rename or simple datapill mapping
- You need a single ternary between two sources (use the [ternary syntax](../fundamentals/datapill-syntax.md#ternary-syntax-for-multiple-sources) instead)

---

## Why Python Over Formula Chains

Each Workato primitive has its own escaping rules, datapill quirks, and silent-failure modes. A typical "extract field N from a nested array" workflow stitched from formulas + `parse_json_v2` + `workato_variable` runs into:

- Bare numeric `#{}` interpolation rejected by the body validator (see [adhoc-http-actions.md](./adhoc-http-actions.md#body-field-gotchas))
- Method chains in body fields don't render
- `parse_json_v2` schematizes nested arrays as `array of object with property "array"` — ugly to navigate
- Datapill paths can't use integer indices
- Structured `update_variables` form silently dropped on import (see [variables-and-lists.md](./variables-and-lists.md#update-variable))

A single `py_eval` step replaces the chain:

```python
import json

def main(input):
    data = json.loads(input['raw_response'])
    return {'value': data['records'][0]['fields'][3]}
```

Standard Python is universally understood, agent-LLMs author it reliably, `print()` produces real stack traces, and the `main()` function is unit-testable in isolation.

---

## Config Entry

```json
{
  "keyword": "application",
  "provider": "py_eval",
  "skip_validation": false
}
```

> **Note:** `py_eval` does NOT take an `account_id` field — omit it entirely (do not write `"account_id": null`). Including `account_id` in the config entry can cause `Passed nil into T.must` errors at import time.

---

## Action Structure

```json
{
  "number": 3,
  "provider": "py_eval",
  "name": "invoke_custom_py_code",
  "as": "extract_value",
  "keyword": "action",
  "input": {
    "name": "Extract value from response",
    "code": "import json\n\ndef main(input):\n    data = json.loads(input['raw_response'])\n    return {'value': data['records'][0]['fields'][3]}\n",
    "code_input": {
      "schema": "[{\"name\":\"raw_response\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"Raw response\",\"parent\":[\"code_input\",\"data\"]}]",
      "data": {
        "raw_response": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"rest\",\"line\":\"api_call\",\"path\":[\"body\"]}')}"
      }
    },
    "code_output_schema_json": "[{\"name\":\"value\",\"type\":\"string\",\"optional\":false,\"control_type\":\"text\",\"label\":\"Value\"}]"
  },
  "extended_input_schema": [
    {
      "control_type": "form-schema-builder",
      "label": "Input fields",
      "name": "code_input",
      "optional": true,
      "override": true,
      "properties": [
        { "control_type": "text", "extends_schema": true, "label": "Schema", "name": "schema", "type": "string" },
        {
          "label": "Data",
          "name": "data",
          "type": "object",
          "properties": [
            { "control_type": "text", "label": "Raw response", "name": "raw_response", "optional": false, "parent": ["code_input", "data"], "type": "string" }
          ]
        }
      ],
      "sticky": true,
      "type": "object"
    }
  ],
  "extended_output_schema": [
    {
      "label": "Output",
      "name": "output",
      "type": "object",
      "properties": [
        { "control_type": "text", "label": "Value", "name": "value", "optional": false, "type": "string" }
      ]
    }
  ],
  "uuid": "extract-value-py-001"
}
```

### Key structural rules

- **Action name** must be `invoke_custom_py_code` (NOT `py_eval`, NOT `python_snippet`).
- **`code`** is a string containing the full Python source. Must define a `def main(input):` function that returns a dict.
- **`code_input.schema`** is a stringified JSON array of input field definitions. Each must include `"parent": ["code_input", "data"]`.
- **`code_input.data`** maps each declared input field name to its value (datapill, formula, or literal).
- **`code_output_schema_json`** is a stringified JSON array of output field definitions. The Python function's return-dict keys must match these names.
- **EIS** uses `control_type: "form-schema-builder"` with `schema` + `data` properties (mirrors `declare_variable`).
- **EOS** wraps the output dict in an `output` object — datapill access uses `path: ["output", "<field-name>"]`.

---

## Datapill Reference

The output is wrapped in `output`:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"py_eval\",\"line\":\"extract_value\",\"path\":[\"output\",\"value\"]}')}"
```

---

## Common Patterns

### Pattern: Build an HTTP body with proper typing

When a downstream `make_request_v2` body needs an integer or operator-style keys, build the JSON in Python:

```python
import json

def main(input):
    body = {
        'where': {'employee_id': {'$eq': int(input['emp_id'])}},
        'limit': 1,
        'select': ['Work Email', 'First Name', 'Last Name']
    }
    return {'body': json.dumps(body)}
```

The downstream HTTP action sets `body: "#{_dp('...py_eval...output.body')}"` — a single `#{}` interpolation around a fully-formed JSON string sidesteps every body-field gotcha.

### Pattern: Extract positional elements from a nested array

A `parse_json_v2` of a `{"data":[[...]]}` response gives an awkward shape. Skip `parse_json_v2` and parse the raw response in Python:

```python
import json

def main(input):
    parsed = json.loads(input['raw'])
    row = parsed['data'][0]
    return {
        'first_name': row[0],
        'last_name': row[1],
        'email': row[2]
    }
```

### Pattern: Normalize / regex-extract a string

Workbot button click can deliver a single concatenated string into a single-parameter receiver. Defensive normalization in `py_eval`:

```python
import re

def main(input):
    raw = input['raw_param']
    m = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', raw)
    return {'approval_id': m.group(0) if m else raw}
```

### Pattern: Conditional routing decision

Decide between two values based on the presence of a third — without three nested ternaries:

```python
def main(input):
    if input.get('override_approver'):
        return {
            'approver_email': input['override_approver'],
            'approver_name': _email_to_display_name(input['override_approver'])
        }
    return {
        'approver_email': input['manager_email'],
        'approver_name': input['manager_name']
    }

def _email_to_display_name(email):
    local = email.split('@')[0]
    parts = local.split('.')
    return ' '.join(p.capitalize() for p in parts)
```

---

## Validation Checklist

- [ ] Action name is `invoke_custom_py_code` (NOT `py_eval`)
- [ ] Provider is `py_eval` (NOT `python_snippet`, NOT `python`)
- [ ] Config entry omits `account_id` entirely
- [ ] `code` defines `def main(input):` returning a dict
- [ ] Each input schema field includes `"parent": ["code_input", "data"]`
- [ ] EIS uses `control_type: "form-schema-builder"` with `schema` + `data` properties
- [ ] Output schema fields match the keys returned from `main()`
- [ ] Datapill references use `path: ["output", "<field-name>"]`

---

## Related Documentation

- [Datapill Syntax](../fundamentals/datapill-syntax.md) — array element access constraints
- [Adhoc HTTP Actions](./adhoc-http-actions.md) — body field gotchas, raw-JSON body patterns
- [Variables and Lists](./variables-and-lists.md) — when a single Python step replaces a multi-step variable chain
