# Genie Skill Trigger

Use the genie skill trigger for recipes that are exposed as callable tools to a Workato Genie (the Workato AI agent runtime). Each genie skill is a recipe that takes typed inputs from the LLM, performs an operation, and returns a typed result the LLM uses to decide its next step.

## Provider Details

| Field | Value |
|-------|-------|
| Provider | `workato_genie` |
| Trigger action | `start_workflow` |
| Return action | `workflow_return_result` |
| Config provider | `workato_genie` with `account_id: null` |

A genie skill recipe pairs with an `.agentic_skill.json` companion file in the same folder. The companion file gives the genie's tool catalog the high-level "what this skill does" description; the recipe holds the actual implementation.

---

## Trigger Structure

```json
{
  "number": 0,
  "provider": "workato_genie",
  "name": "start_workflow",
  "as": "trigger",
  "keyword": "trigger",
  "input": {
    "description": "Look up the requesting user's manager via the master employee table. Returns manager_email, manager_name, manager_employee_id, plus the requester's name and employee id. Use this as the FIRST step before sending any approval-related DM.",
    "parameters_schema_json": "[{\"name\":\"user_email\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"User email\",\"optional\":false,\"hint\":\"Work email of the user whose manager to look up\"}]",
    "result_schema_json": "[{\"name\":\"success\",\"type\":\"boolean\",\"control_type\":\"checkbox\",\"label\":\"Success\"},{\"name\":\"manager_email\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Manager email\"},{\"name\":\"manager_name\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Manager name\"},{\"name\":\"error\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Error\"}]",
    "requires_user_confirmation": "false"
  },
  "extended_output_schema": [
    {
      "label": "Parameters",
      "name": "parameters",
      "type": "object",
      "properties": [
        { "control_type": "text", "label": "User email", "name": "user_email", "type": "string", "optional": false }
      ]
    }
  ],
  "uuid": "trigger-001"
}
```

### Trigger EOS with `metadata_schema_json` (unverified)

When `metadata_schema_json` is defined, server exports show the trigger's `extended_output_schema` includes a `custom_metadata` section alongside `parameters`. This structure has been observed but not activation-tested:

```json
"extended_output_schema": [
  {
    "label": "Parameters",
    "name": "parameters",
    "type": "object",
    "properties": [
      { "control_type": "text", "label": "Input 1", "name": "Input1", "optional": true, "type": "string" }
    ]
  },
  {
    "label": "Custom Metadata",
    "name": "custom_metadata",
    "type": "object",
    "properties": [
      { "control_type": "text", "label": "Label1", "name": "TaskMetadata1", "optional": true, "type": "string" }
    ]
  }
]
```

### Key structural rules

- **`input.description` is the skill description shown in the Workato UI's "When should your genie run this skill?" textarea.** This is what the genie's LLM sees to decide whether to invoke the skill, so write it clearly: when to use, when NOT to use, what each input means, what the outputs mean, what to do with each output. Long descriptions (200–800 words) are fine and recommended.
- **`parameters_schema_json`** is a stringified JSON array — the typed inputs the LLM must supply. (NOT `input_schema` — that name is invalid.)
- **`result_schema_json`** is a stringified JSON array — the fields the recipe will return. The LLM consumes these. (NOT `output_schema`.)
- **`requires_user_confirmation`** is a string `"true"` or `"false"` — controls whether the genie asks the user for confirmation before running the skill.
- **`metadata_schema_json`** (optional) is a stringified JSON array — defines custom metadata fields visible in the genie UI. When present, the trigger's `extended_output_schema` must include a matching `custom_metadata` section (see EOS structure below).

### Datapill paths

Genie triggers expose datapill namespaces based on the schemas defined in the trigger input:

| Namespace | Path prefix | Source | Verified |
|-----------|-------------|--------|----------|
| `parameters` | `["parameters", "field"]` | User-defined inputs from `parameters_schema_json` | Yes (golden recipes 237474, 237651) |
| `context` | `["context", "field"]` | Built-in genie runtime identity fields | Yes (golden recipe 237651 — returns invoking user's name) |
| `custom_metadata` | `["custom_metadata", "field"]` | Custom metadata from `metadata_schema_json` | Unverified (observed in server export) |

**User-defined parameter** (from `parameters_schema_json`):
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_genie\",\"line\":\"trigger\",\"path\":[\"parameters\",\"user_email\"]}')}"
```

**Built-in context field** (genie runtime identity — available without any schema declaration):
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_genie\",\"line\":\"trigger\",\"path\":[\"context\",\"user_name\"]}')}"
```

Known `context` fields: `user_name` (verified), `user_email` (unverified but expected).

---

## Skill Description Placement Gotcha

The companion `.agentic_skill.json` file has its own top-level `trigger_description` field. **It is NOT the field shown in the UI.** The UI reads `code.input.description` from the recipe's `start_workflow` trigger, not from the agentic_skill file.

If you populate `trigger_description` on the agentic_skill file but leave the recipe trigger's `input.description` empty, the UI shows an empty skill description with no warning, no lint hint. The genie's LLM will see a blank tool entry and fail to invoke the skill correctly.

**Always populate `code.input.description` on the recipe trigger.** Keep the two in sync, or treat the recipe trigger as canonical and ignore the agentic_skill `trigger_description` entirely.

---

## Returning a Result

Use `workflow_return_result` to send the typed output back to the genie:

```json
{
  "number": 5,
  "provider": "workato_genie",
  "name": "workflow_return_result",
  "as": "return_success",
  "keyword": "action",
  "toggleCfg": {
    "result.success": true
  },
  "input": {
    "result": {
      "success": "true",
      "manager_email": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"py_eval\",\"line\":\"parse_employee\",\"path\":[\"output\",\"manager_email\"]}')}",
      "manager_name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"py_eval\",\"line\":\"parse_employee\",\"path\":[\"output\",\"manager_name\"]}')}",
      "error": ""
    }
  },
  "extended_input_schema": [
    {
      "label": "Result",
      "name": "result",
      "type": "object",
      "properties": [
        { "control_type": "checkbox", "label": "Success", "name": "success", "optional": true, "type": "boolean", "render_input": "boolean_conversion", "parse_output": "boolean_conversion", "toggle_hint": "Select from option list", "toggle_field": { "label": "Success", "control_type": "text", "toggle_hint": "Use custom value", "name": "success", "type": "boolean" } },
        { "control_type": "text", "label": "Manager email", "name": "manager_email", "optional": true, "type": "string" },
        { "control_type": "text", "label": "Manager name", "name": "manager_name", "optional": true, "type": "string" },
        { "control_type": "text", "label": "Error", "name": "error", "optional": true, "type": "string" }
      ]
    }
  ],
  "extended_output_schema": [
    {
      "label": "Result",
      "name": "result",
      "type": "object",
      "properties": [
        { "control_type": "checkbox", "label": "Success", "name": "success", "optional": true, "type": "boolean", "render_input": "boolean_conversion", "parse_output": "boolean_conversion", "toggle_hint": "Select from option list", "toggle_field": { "label": "Success", "control_type": "text", "toggle_hint": "Use custom value", "name": "success", "type": "boolean" } },
        { "control_type": "text", "label": "Manager email", "name": "manager_email", "optional": true, "type": "string" },
        { "control_type": "text", "label": "Manager name", "name": "manager_name", "optional": true, "type": "string" },
        { "control_type": "text", "label": "Error", "name": "error", "optional": true, "type": "string" }
      ]
    }
  ],
  "uuid": "return-success-001"
}
```

**CRITICAL:** `workflow_return_result` requires both `extended_input_schema` and `extended_output_schema` defining the result fields. Without them, the UI cannot resolve the result object and datapills break. The `toggleCfg` entry controls how boolean fields are rendered.

Each key in `input.result` must match a field name in the trigger's `result_schema_json`. Unknown keys are dropped silently.

### Returning an error

For genie skills, **the canonical "fail with a message" pattern is `workflow_return_result` with `success: false`**, not the generic `stop` keyword:

```json
{
  "number": 99,
  "provider": "workato_genie",
  "name": "workflow_return_result",
  "as": "return_error",
  "keyword": "action",
  "input": {
    "result": {
      "success": "false",
      "error": "Employee not found in master employee table"
    }
  },
  "uuid": "return-error-001"
}
```

> **Note:** `stop` with `stop_with_error: "true"` and a message is rejected by the recipe visualizer in genie skill recipes (`unknown keyword stop`). Only `stop_with_error: "false"` (graceful exit, no error message) is supported for the `stop` keyword. For all error paths, return via `workflow_return_result` with `success: false`.

---

## Companion `.agentic_skill.json` File

The companion file lives next to the recipe and tells the genie's tool catalog where the implementation lives:

```json
{
  "name": "[SK] get user manager",
  "references": {
    "recipe_id": {
      "id": {
        "folder": "Skills & Functions",
        "name": "[SK] get user manager",
        "zip_name": "Skills & Functions/sk_get_user_manager.recipe.json"
      },
      "type": "recipe"
    }
  },
  "trigger_description": "..."
}
```

The `trigger_description` on this file appears to be ignored by the UI (see gotcha above). Treat the recipe's `code.input.description` as the canonical skill description and either mirror it here or leave this field empty.

---

## Validation Checklist

- [ ] Provider is `workato_genie`
- [ ] Trigger action name is `start_workflow`
- [ ] Return action name is `workflow_return_result`
- [ ] `code.input.description` is populated with the skill's "when to use / when NOT to use / inputs / outputs" guidance for the LLM
- [ ] `parameters_schema_json` and `result_schema_json` are stringified JSON arrays (NOT `input_schema`/`output_schema`)
- [ ] Each `workflow_return_result.input.result` key matches a field in `result_schema_json`
- [ ] `requires_user_confirmation` is present (string `"true"` or `"false"`)
- [ ] Error paths use `workflow_return_result` with `success: false` (NOT `stop` with `stop_with_error: "true"`)
- [ ] Config entry for `workato_genie` includes `"name": "workato_genie"`, `"account_id": null`, and `"skip_validation": false`
- [ ] `workflow_return_result` has both `extended_input_schema` and `extended_output_schema` matching the result fields

---

## Related Documentation

- [Recipe Structure](../fundamentals/recipe-structure.md)
- [Datapill Syntax](../fundamentals/datapill-syntax.md)
- [Python Snippets](../patterns/python-snippets.md) — preferred for any non-trivial transformation inside a genie skill
- [Data Table Trigger](./data-table.md) — for background recipes triggered by row events (typically paired with genie skills that write to those tables)
- [Stop Action](../control-flow/stop.md) — `stop_with_error: "true"` is NOT supported in genie skills; use `workflow_return_result` with `success: false` instead
