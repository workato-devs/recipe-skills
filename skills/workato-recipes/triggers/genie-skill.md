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
    "input_schema": "[{\"name\":\"user_email\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"User email\",\"optional\":false,\"hint\":\"Work email of the user whose manager to look up\"}]",
    "output_schema": "[{\"name\":\"success\",\"type\":\"boolean\",\"control_type\":\"checkbox\",\"label\":\"Success\"},{\"name\":\"manager_email\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Manager email\"},{\"name\":\"manager_name\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Manager name\"},{\"name\":\"error\",\"type\":\"string\",\"control_type\":\"text\",\"label\":\"Error\"}]"
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

### Key structural rules

- **`input.description` is the skill description shown in the Workato UI's "When should your genie run this skill?" textarea.** This is what the genie's LLM sees to decide whether to invoke the skill, so write it clearly: when to use, when NOT to use, what each input means, what the outputs mean, what to do with each output. Long descriptions (200–800 words) are fine and recommended.
- **`input_schema`** is a stringified JSON array — the typed inputs the LLM must supply.
- **`output_schema`** is a stringified JSON array — the fields the recipe will return. The LLM consumes these.
- Datapills for the trigger inputs use:
  ```json
  "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_genie\",\"line\":\"trigger\",\"path\":[\"parameters\",\"user_email\"]}')}"
  ```

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
  "input": {
    "result": {
      "success": "true",
      "manager_email": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"py_eval\",\"line\":\"parse_employee\",\"path\":[\"output\",\"manager_email\"]}')}",
      "manager_name": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"py_eval\",\"line\":\"parse_employee\",\"path\":[\"output\",\"manager_name\"]}')}",
      "error": ""
    }
  },
  "uuid": "return-success-001"
}
```

Each key in `input.result` must match a field name in the trigger's `output_schema`. Unknown keys are dropped silently.

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
- [ ] `input_schema` and `output_schema` are stringified JSON arrays
- [ ] Each `workflow_return_result.input.result` key matches a field in `output_schema`
- [ ] Error paths use `workflow_return_result` with `success: false` (NOT `stop` with `stop_with_error: "true"`)
- [ ] Config entry for `workato_genie` includes `"account_id": null`

---

## Related Documentation

- [Recipe Structure](../fundamentals/recipe-structure.md)
- [Datapill Syntax](../fundamentals/datapill-syntax.md)
- [Python Snippets](../patterns/python-snippets.md) — preferred for any non-trivial transformation inside a genie skill
- [Data Table Trigger](./data-table.md) — for background recipes triggered by row events (typically paired with genie skills that write to those tables)
