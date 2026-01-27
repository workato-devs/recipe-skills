# Dialog Parameters

This pattern covers configuring dialog/modal form fields for Workbot commands.

---

## Parameter Structure

Parameters are defined as a JSON string in the trigger input:

```json
"parameters": "[
  {
    \"name\": \"field_name\",
    \"label\": \"Display Label\",
    \"hint\": \"Help text for the user\",
    \"optional\": \"false\",
    \"control_type\": \"text\"
  }
]"
```

---

## Control Types

### Text Input

Single-line text field (max 150 characters):

```json
{
  "name": "title",
  "label": "Title",
  "hint": "Enter a brief title",
  "optional": "false",
  "control_type": "text"
}
```

### Text Area

Multi-line text field (max 3000 characters):

```json
{
  "name": "description",
  "label": "Description",
  "hint": "Provide detailed information",
  "optional": "true",
  "control_type": "text-area"
}
```

### Select Dropdown

Dropdown with predefined options:

```json
{
  "name": "priority",
  "label": "Priority",
  "hint": "Select priority level",
  "optional": true,
  "control_type": "select",
  "pick_list": [
    ["High - Urgent", "high"],
    ["Medium - Normal", "medium"],
    ["Low - When possible", "low"]
  ],
  "dialog_data_source": "custom"
}
```

#### Pick List Format

Each option is an array: `[display_text, value]`

```json
"pick_list": [
  ["Display Text 1", "value1"],
  ["Display Text 2", "value2"],
  ["Display Text 3", "value3"]
]
```

---

## Parameter Fields Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Internal field name for datapills |
| `label` | Yes | string | Label shown above the field |
| `hint` | No | string | Helper text below the field |
| `optional` | Yes | string/bool | "true", "false", true, or false |
| `control_type` | Yes | string | "text", "text-area", or "select" |
| `pick_list` | For select | array | Array of [display, value] pairs |
| `dialog_data_source` | For select | string | Set to "custom" for static options |
| `type` | No | string | Data type hint ("array" for select) |
| `prompt` | No | string | "true" to emphasize field |
| `options` | No | string | Comma-separated option summary |

---

## Extended Output Schema Mapping

Parameters must be mapped in `extended_output_schema` for datapill access:

```json
"extended_output_schema": [
  {
    "label": "Parameters",
    "name": "parameters",
    "properties": [
      {
        "control_type": "text",
        "label": "Title",
        "name": "title",
        "hint": "Enter a brief title",
        "optional": "false",
        "type": "string"
      },
      {
        "control_type": "text-area",
        "label": "Description",
        "name": "description",
        "hint": "Provide detailed information",
        "optional": "true",
        "type": "string"
      },
      {
        "label": "Priority",
        "name": "priority",
        "hint": "Select priority level",
        "optional": true,
        "pick_list": [
          ["High - Urgent", "high"],
          ["Medium - Normal", "medium"],
          ["Low - When possible", "low"]
        ],
        "type": "array",
        "dialog_data_source": "custom",
        "of": "object",
        "properties": []
      }
    ],
    "type": "object"
  }
]
```

---

## Accessing Parameter Values

Reference parameters in actions using datapills:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"parameters\",\"title\"]}')}"
```

For select fields (returns the value, not display text):

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"parameters\",\"priority\"]}')}"
```

---

## Complete Example

```json
{
  "input": {
    "parameters": "[{\"name\":\"ticket_subject\",\"label\":\"Subject\",\"hint\":\"Brief summary of the issue\",\"optional\":\"false\",\"control_type\":\"text\"},{\"name\":\"ticket_description\",\"label\":\"Description\",\"hint\":\"Provide full details including steps to reproduce\",\"optional\":\"false\",\"control_type\":\"text-area\"},{\"name\":\"ticket_category\",\"label\":\"Category\",\"hint\":\"What type of issue is this?\",\"optional\":true,\"control_type\":\"select\",\"pick_list\":[[\"Bug Report\",\"bug\"],[\"Feature Request\",\"feature\"],[\"Question\",\"question\"],[\"Other\",\"other\"]],\"dialog_data_source\":\"custom\"},{\"name\":\"ticket_urgency\",\"label\":\"Urgency\",\"hint\":\"How urgent is this issue?\",\"optional\":true,\"control_type\":\"select\",\"pick_list\":[[\"Critical - System down\",\"critical\"],[\"High - Major impact\",\"high\"],[\"Medium - Some impact\",\"medium\"],[\"Low - Minor issue\",\"low\"]],\"dialog_data_source\":\"custom\"}]"
  },
  "extended_output_schema": [
    {
      "label": "Parameters",
      "name": "parameters",
      "properties": [
        {
          "control_type": "text",
          "label": "Subject",
          "name": "ticket_subject",
          "type": "string",
          "optional": "false"
        },
        {
          "control_type": "text-area",
          "label": "Description",
          "name": "ticket_description",
          "type": "string",
          "optional": "false"
        },
        {
          "label": "Category",
          "name": "ticket_category",
          "optional": true,
          "type": "array",
          "of": "object",
          "properties": []
        },
        {
          "label": "Urgency",
          "name": "ticket_urgency",
          "optional": true,
          "type": "array",
          "of": "object",
          "properties": []
        }
      ],
      "type": "object"
    }
  ]
}
```

---

## Dialog Limits

Slack dialogs have the following limits:

| Limit | Value |
|-------|-------|
| Maximum fields | 10 |
| Text field max length | 150 characters |
| Text area max length | 3000 characters |
| Dialog title max length | 24 characters |
| Label max length | 24 characters |
| Hint max length | 150 characters |

---

## Opening Dialogs from Other Recipes

Use `open_bot_dialog` action with `trigger_id`:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "open_bot_dialog",
  "as": "open_dialog",
  "keyword": "action",
  "input": {
    "trigger_id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"trigger_id\"]}')}",
    "title": "Additional Details",
    "bot_command": {
      "zip_name": "Recipes/process_form.recipe.json",
      "name": "Process Form Submission",
      "folder": "Recipes"
    },
    "elements": "=[{\"type\":\"text\",\"name\":\"extra_field\",\"label\":\"Extra Field\",\"optional\":false}]"
  }
}
```

> **Important:** `trigger_id` expires after 3 seconds. Dialogs must be opened immediately after user interaction.
