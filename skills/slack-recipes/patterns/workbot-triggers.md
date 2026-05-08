# Workbot Command Triggers

This pattern covers configuring Workbot command triggers for Slack, including slash commands and dialog parameters.

---

## Reserved Keywords

### Reserved Domain/Scope Names

Avoid common words in `domain` and `scope` fields as they may conflict with existing Workbot commands:

**Avoid:** `feedback`, `help`, `support`, `status`, `remind`, `settings`

Using reserved names like "feedback" as your domain can cause unexpected behavior - the bot may respond with default messages like "Thank you :thumbsup:" instead of triggering your dialog.

**Use unique, project-specific names:**
- `my-app-feedback` instead of `feedback`
- `project-helpdesk` instead of `help`

---

## Basic Trigger Structure

```json
{
  "number": 0,
  "provider": "slack_bot",
  "name": "bot_command_v2",
  "as": "trigger_001",
  "keyword": "trigger",
  "dynamicPickListSelection": {
    "domain": "Slack"
  },
  "toggleCfg": {
    "domain": true,
    "name": true,
    "scope": false
  },
  "input": {
    "domain": "my-app",
    "name": "create",
    "scope": "project",
    "description": "Create a new project",
    "allow_dialog": "true",
    "dialog_title": "New Project Details",
    "hide_from_help": "false",
    "slash_command": {
      "enable": "true",
      "name": "/myproject",
      "first_reply": "Let me help you create a new project..."
    },
    "parameters": "[...]"
  },
  "extended_output_schema": [...],
  "block": [...]
}
```

---

## Slash Command Configuration

Enable a slash command with immediate feedback:

```json
"slash_command": {
  "enable": "true",
  "name": "/mycommand",
  "first_reply": "Processing your request..."
}
```

| Field | Description |
|-------|-------------|
| `enable` | "true" to enable slash command |
| `name` | Command name starting with `/` (max 32 chars, lowercase, no spaces) |
| `first_reply` | Immediate response shown while recipe processes |

### Slash Command Naming Rules

- Must start with `/`
- Lowercase letters, numbers, hyphens, underscores only
- Maximum 32 characters
- Must be unique within your Slack workspace

---

## Dialog Parameters

Parameters define form fields shown in the dialog modal:

```json
"parameters": "[
  {
    \"name\": \"project_name\",
    \"label\": \"Project Name\",
    \"hint\": \"What should we call this project?\",
    \"optional\": \"false\",
    \"control_type\": \"text\"
  },
  {
    \"name\": \"description\",
    \"label\": \"Description\",
    \"hint\": \"Describe the project goals\",
    \"optional\": \"true\",
    \"control_type\": \"text-area\"
  },
  {
    \"name\": \"priority\",
    \"label\": \"Priority Level\",
    \"hint\": \"How urgent is this?\",
    \"optional\": true,
    \"control_type\": \"select\",
    \"pick_list\": [
      [\"High - Immediate attention\", \"High\"],
      [\"Medium - Normal priority\", \"Medium\"],
      [\"Low - When time permits\", \"Low\"]
    ],
    \"dialog_data_source\": \"custom\"
  }
]"
```

### Parameter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Internal field name (used in datapills) |
| `label` | Yes | Display label shown to user |
| `hint` | No | Helper text below the field |
| `optional` | Yes | "true" or "false" / true or false |
| `control_type` | Yes | Input type (see below) |
| `pick_list` | For select | Array of `[display, value]` pairs |
| `dialog_data_source` | For select | Set to "custom" for static options |

### Control Types

| Type | Description | Max Length |
|------|-------------|------------|
| `text` | Single-line text input | 150 chars |
| `text-area` | Multi-line text input | 3000 chars |
| `select` | Dropdown menu | - |

---

## Extended Output Schema

Map parameters to output schema for datapill access:

```json
"extended_output_schema": [
  {
    "label": "Parameters",
    "name": "parameters",
    "properties": [
      {
        "control_type": "text",
        "label": "Project Name",
        "name": "project_name",
        "hint": "What should we call this project?",
        "optional": "false",
        "type": "string"
      },
      {
        "control_type": "text-area",
        "label": "Description",
        "name": "description",
        "hint": "Describe the project goals",
        "optional": "true",
        "type": "string"
      },
      {
        "label": "Priority Level",
        "name": "priority",
        "hint": "How urgent is this?",
        "optional": true,
        "pick_list": [
          ["High - Immediate attention", "High"],
          ["Medium - Normal priority", "Medium"],
          ["Low - When time permits", "Low"]
        ],
        "type": "array",
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

Reference dialog parameters in datapills:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"parameters\",\"project_name\"]}')}"
```

---

## Context Fields

The trigger provides context about the Slack environment:

```json
"path": ["context", "user"]        // User ID who triggered
"path": ["context", "channel"]     // Channel where triggered
"path": ["context", "trigger_id"]  // Required for dialogs
"path": ["context", "team"]        // Workspace ID
```

---

## toggleCfg Behavior

The `toggleCfg` object controls whether fields use picklist selection vs custom/formula values:

```json
"toggleCfg": {
  "domain": true,   // true = expects picklist value
  "name": true,     // true = expects picklist value
  "scope": false    // false = allows custom/formula value
}
```

| Value | Behavior |
|-------|----------|
| `true` | Field expects a value from a predefined picklist |
| `false` | Field allows custom text or formula values |

**Example:** When using a custom action name like "submit" (not from a picklist), set:
```json
"toggleCfg": {
  "name": false
}
```

---

## Button-to-Recipe Parameter Routing

When a Workbot message uses `attachment_buttons` with `bot_command` pointing at another recipe, each button's `params` field passes data to the receiver's `bot_command_v2` trigger parameters.

**Use the space-separated, colon-prefixed format:**

```json
"params": "approval_id: <UUID>"
```

| Field | Behavior |
|-------|----------|
| `key: value` (with space after the colon, optional) | Routed to the receiver's matching parameter on click — verified for single-parameter receivers |
| `key=value&key=value` (URL-encoded) | **Does not work** — Workbot drops the params and falls back to interactive parameter-collection mode, prompting the user to enter each value manually |

> *Multi-parameter syntax is untested.* In our testing, multi-parameter button receivers fell into Workbot's interactive collection flow regardless of params formatting (see the [Multi-Parameter Receivers](#multi-parameter-receivers-dont-reliably-work-via-buttons) section below). We extrapolated `"key1: value1 key2: value2"` from the single-parameter shape but never confirmed it routes correctly when the receiver declares multiple parameters. If multi-param is needed, validate the exact delimiter behavior first or take the recommended split-handler approach.

### Multi-Parameter Receivers Don't Reliably Work via Buttons

Even with the correct `key: value` format and `allow_dialog: "false"`, a receiver recipe with **multiple parameters** triggered by a button click will, in practice, fall into Workbot's interactive collection flow on the first click and produce malformed input on subsequent clicks.

**Recommended pattern:** Split per-action handlers. Instead of one `handle_response` recipe with `(approval_id, action)` parameters, create separate `handle_approve` and `handle_deny` recipes, each with a single parameter (`approval_id`). The button's `bot_command` then points at the appropriate single-action recipe and the `params` field carries only one key:

```json
"attachment_buttons": [
  {
    "title": "Approve",
    "bot_command": { "zip_name": "Recipes/handle_approve.recipe.json", ... },
    "params": "approval_id: 1f2c40ee-..."
  },
  {
    "title": "Deny",
    "bot_command": { "zip_name": "Recipes/handle_deny.recipe.json", ... },
    "params": "approval_id: 1f2c40ee-..."
  }
]
```

### Defensive Parameter Normalization

If you encounter a case where the button click delivers a single concatenated string (e.g., `it_approvals approve request <UUID>`) into the receiver's first parameter, add a `py_eval` step at the top of the receiver to extract the canonical value with a regex (e.g., a UUID regex against the raw input). This is a belt-and-suspenders defense against the Workbot fallback delivering malformed input.

---

## Visibility Configuration

Control which fields appear in Workato UI:

```json
"visible_config_fields": [
  "domain",
  "name",
  "scope",
  "parameters",
  "slash_command",
  "slash_command.enable",
  "slash_command.name",
  "allow_dialog",
  "description",
  "slash_command.first_reply",
  "dialog_title",
  "hide_from_help"
]
```

---

## Complete Example

```json
{
  "number": 0,
  "provider": "slack_bot",
  "name": "bot_command_v2",
  "as": "trigger_001",
  "keyword": "trigger",
  "dynamicPickListSelection": {
    "domain": "Slack"
  },
  "toggleCfg": {
    "domain": true,
    "name": true,
    "scope": false
  },
  "input": {
    "allow_dialog": "true",
    "slash_command": {
      "enable": "true",
      "name": "/helpdesk",
      "first_reply": "Opening ticket form..."
    },
    "scope": "ticket",
    "description": "Submit a helpdesk ticket",
    "dialog_title": "New Helpdesk Ticket",
    "parameters": "[{\"name\":\"subject\",\"label\":\"Subject\",\"hint\":\"Brief description of the issue\",\"optional\":\"false\",\"control_type\":\"text\"},{\"name\":\"details\",\"label\":\"Details\",\"hint\":\"Provide full details\",\"optional\":\"false\",\"control_type\":\"text-area\"},{\"name\":\"urgency\",\"label\":\"Urgency\",\"optional\":true,\"control_type\":\"select\",\"pick_list\":[[\"Critical\",\"critical\"],[\"High\",\"high\"],[\"Normal\",\"normal\"],[\"Low\",\"low\"]],\"dialog_data_source\":\"custom\"}]",
    "hide_from_help": "false",
    "name": "create",
    "domain": "helpdesk"
  },
  "extended_output_schema": [
    {
      "label": "Parameters",
      "name": "parameters",
      "properties": [
        {
          "control_type": "text",
          "label": "Subject",
          "name": "subject",
          "type": "string",
          "optional": "false"
        },
        {
          "control_type": "text-area",
          "label": "Details",
          "name": "details",
          "type": "string",
          "optional": "false"
        },
        {
          "label": "Urgency",
          "name": "urgency",
          "optional": true,
          "type": "array",
          "of": "object",
          "properties": []
        }
      ],
      "type": "object"
    }
  ],
  "block": [...]
}
```
