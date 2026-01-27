# Slack Recipes Skill - Agent Instructions

> **DEPENDENCY: Load `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

This skill provides Slack-specific knowledge for generating Workato recipes. It covers **two Slack connectors**:

| Connector | Provider | Use Case |
|-----------|----------|----------|
| **Workbot for Slack** | `slack_bot` | Interactive bots, slash commands, dialogs, buttons |
| **Slack (native)** | `slack` | Programmatic actions via API-triggered recipes |

This skill extends the **workato-recipes** base skill.

---

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Choosing a Connector](#choosing-a-connector)
3. [Workbot for Slack (slack_bot)](#workbot-for-slack-slack_bot)
4. [Native Slack Connector (slack)](#native-slack-connector-slack)
5. [Datapill Paths](#datapill-paths)
6. [Templates](#templates)
7. [Pre-Push Checklist](#pre-push-checklist)

---

## When to Use This Skill

Use this skill when building Workato recipes that:
- Respond to slash commands in Slack
- Post messages to channels or DMs
- Display interactive dialogs/modals to collect user input
- Create buttons that trigger other recipes
- Manage Slack channels (create, invite users)
- Look up users by email
- Build conversational workflows in Slack

**Prerequisites:**
- `workato-recipes` base skill loaded
- Workato workspace with Slack connection(s) configured

---

## Choosing a Connector

### Use Workbot for Slack (`slack_bot`) when:
- Building interactive slash commands
- Collecting user input via dialogs/modals
- Creating button-based workflows
- Responding to user actions in real-time
- You need the trigger to be a user interaction

### Use Native Slack (`slack`) when:
- Building API-triggered recipes
- Creating callable recipes for other systems
- You need programmatic actions without user interaction
- Automating Slack operations from external triggers

---

## Workbot for Slack (slack_bot)

### Config Section

```json
{
  "keyword": "application",
  "provider": "slack_bot",
  "skip_validation": false,
  "account_id": {
    "zip_name": "my_workbot_account.connection.json",
    "name": "My Workbot for Slack account",
    "folder": "Connections"
  }
}
```

### Workbot Command Trigger

The primary trigger for Slack recipes is `bot_command_v2`:

```json
{
  "number": 0,
  "provider": "slack_bot",
  "name": "bot_command_v2",
  "as": "trigger_001",
  "keyword": "trigger",
  "input": {
    "domain": "my-app",
    "name": "create",
    "scope": "project",
    "description": "Create a new project",
    "allow_dialog": "true",
    "dialog_title": "New Project",
    "hide_from_help": "false",
    "slash_command": {
      "enable": "true",
      "name": "/mycommand",
      "first_reply": "Processing your request..."
    },
    "parameters": "[...]"
  }
}
```

### Trigger Input Fields

| Field | Required | Description |
|-------|----------|-------------|
| `domain` | Yes | App domain grouping (e.g., "my-app") |
| `name` | Yes | Command name within domain |
| `scope` | No | Command scope for organization |
| `description` | Yes | Help text shown to users |
| `allow_dialog` | No | Enable dialog/modal support ("true"/"false") |
| `dialog_title` | No | Title shown on dialog modal |
| `hide_from_help` | No | Hide from Workbot help command |
| `slash_command.enable` | No | Enable slash command ("true"/"false") |
| `slash_command.name` | No | Slash command (e.g., "/mycommand") |
| `slash_command.first_reply` | No | Immediate response before processing |
| `parameters` | No | JSON string defining dialog form fields |

### Parameters Format

Parameters define the dialog form fields as a JSON string:

```json
"parameters": "[
  {
    \"name\": \"project_name\",
    \"label\": \"Project Name\",
    \"hint\": \"Enter the project name\",
    \"optional\": \"false\",
    \"control_type\": \"text\"
  },
  {
    \"name\": \"description\",
    \"label\": \"Description\",
    \"hint\": \"Describe the project\",
    \"optional\": \"true\",
    \"control_type\": \"text-area\"
  },
  {
    \"name\": \"priority\",
    \"label\": \"Priority\",
    \"hint\": \"Select priority level\",
    \"optional\": true,
    \"control_type\": \"select\",
    \"pick_list\": [
      [\"High\", \"high\"],
      [\"Medium\", \"medium\"],
      [\"Low\", \"low\"]
    ]
  }
]"
```

#### Control Types

| Control Type | Description |
|--------------|-------------|
| `text` | Single-line text input |
| `text-area` | Multi-line text input |
| `select` | Dropdown with `pick_list` options |

---

## Slack Actions

### Post Bot Message

Send a message to a channel or DM:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "post_bot_message",
  "as": "send_message",
  "keyword": "action",
  "input": {
    "channel": "C1234567890",
    "text": "Hello from Workbot!",
    "message": {
      "title": "Notification",
      "attachment_text": "Here are the details..."
    }
  }
}
```

**Send DM to triggering user:**
```json
"channel": "=_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"user\"]}').gsub('\"','')"
```

### Post Bot Reply with Buttons

Send a reply with interactive buttons:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "post_bot_reply_v2",
  "as": "reply_with_buttons",
  "keyword": "action",
  "input": {
    "message": {
      "title": "Ready to proceed?",
      "attachment_text": "Click a button to continue"
    },
    "attachment_buttons": [
      {
        "title": "Approve",
        "bot_command": {
          "zip_name": "Recipes/handle_approval.recipe.json",
          "name": "Handle Approval",
          "folder": "Recipes"
        },
        "params": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"trigger_id\"]}')}"
      },
      {
        "title": "Reject",
        "bot_command": {
          "zip_name": "Recipes/handle_rejection.recipe.json",
          "name": "Handle Rejection",
          "folder": "Recipes"
        }
      }
    ]
  }
}
```

### Open Bot Dialog

Open a dialog/modal to collect additional input:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "open_bot_dialog",
  "as": "open_dialog",
  "keyword": "action",
  "input": {
    "trigger_id": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"trigger_id\"]}')}",
    "title": "Enter Details",
    "bot_command": {
      "zip_name": "Recipes/process_dialog.recipe.json",
      "name": "Process Dialog Submission",
      "folder": "Recipes"
    },
    "elements": "=[{\"type\":\"text\",\"name\":\"field1\",\"label\":\"Field 1\",\"optional\":false}]"
  }
}
```

### Adhoc HTTP Action (Direct Slack API)

Call Slack API endpoints directly:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "__adhoc_http_action",
  "as": "create_channel",
  "keyword": "action",
  "input": {
    "mnemonic": "Create channel",
    "verb": "post",
    "request_type": "json",
    "response_type": "json",
    "path": "conversations.create",
    "input": {
      "schema": "[{\"control_type\":\"text\",\"label\":\"Name\",\"type\":\"string\",\"name\":\"name\"}]",
      "data": {
        "name": "my-new-channel"
      }
    },
    "output": "[{\"control_type\":\"text\",\"label\":\"Ok\",\"type\":\"boolean\",\"name\":\"ok\"},{\"properties\":[{\"control_type\":\"text\",\"label\":\"ID\",\"type\":\"string\",\"name\":\"id\"}],\"label\":\"Channel\",\"type\":\"object\",\"name\":\"channel\"}]"
  }
}
```

**Common Slack API paths:**
- `conversations.create` - Create a channel
- `conversations.invite` - Invite users to a channel
- `conversations.list` - List channels
- `users.info` - Get user information

---

## Native Slack Connector (slack)

### Config Section

```json
{
  "keyword": "application",
  "provider": "slack",
  "skip_validation": false,
  "account_id": {
    "zip_name": "my_slack_account.connection.json",
    "name": "My Slack account",
    "folder": ""
  }
}
```

### Available Actions

| Action | Description |
|--------|-------------|
| `post_message_to_channel` | Post message to channel |
| `create_conversation` | Create a channel |
| `get_user_by_email` | Look up user by email |
| `invite_user_to_channel` | Invite user to channel |
| `archive_conversation` | Archive a channel |
| `unarchive_conversation` | Unarchive a channel |
| `set_conversation_purpose` | Set channel purpose |

See `patterns/native-slack-actions.md` for complete documentation.

---

## Datapill Paths

### Workbot Trigger Context (no body wrapper)

```json
"path": ["context", "user"]
"path": ["context", "trigger_id"]
"path": ["context", "channel"]
"path": ["parameters", "project_name"]
```

### Native Slack Actions (no body wrapper)

```json
"path": ["id"]
"path": ["name"]
"path": ["profile", "email"]
"path": ["ts"]
```

### Adhoc HTTP Responses (has body wrapper)

```json
"path": ["body", "channel", "id"]
"path": ["body", "ok"]
```

### Common Workbot Context Fields

| Path | Description |
|------|-------------|
| `["context", "user"]` | User ID who triggered the command |
| `["context", "channel"]` | Channel where command was invoked |
| `["context", "trigger_id"]` | Required for opening dialogs |
| `["context", "team"]` | Slack workspace ID |
| `["parameters", "<name>"]` | Dialog parameter values |

---

## Templates

Minimal, validated recipe examples:

| Template | Description |
|----------|-------------|
| `templates/slash-command-with-dialog.json` | Slash command that collects input via dialog |
| `templates/button-interaction.json` | Message with buttons that chain to other recipes |
| `templates/create-channel-invite-user.json` | Create channel via API and invite user |

---

## Slack Patterns

### Pattern: Slash Command with Dialog

See `patterns/workbot-triggers.md` for complete trigger configuration.

### Pattern: Recipe Chaining via Buttons

Buttons can invoke other Workbot command recipes:

```json
"bot_command": {
  "zip_name": "Recipes/next_step.recipe.json",
  "name": "Next Step Recipe",
  "folder": "Recipes"
}
```

### Pattern: Channel Name Sanitization

Slack channel names have restrictions. Sanitize user input:

```json
"name": "=_dp('{...}').downcase.gsub(/[^a-z0-9]/, '-').gsub(/-+/, '-').gsub(/^-|-$/, '')[0..79]"
```

### Pattern: Send DM to Triggering User

Use the user context as the channel:

```json
"channel": "=_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"user\"]}').gsub('\"','')"
```

---

## Pre-Push Checklist

### For Workbot (`slack_bot`) recipes:

- [ ] `slack_bot` provider in config section
- [ ] Connection name matches your Workbot connection
- [ ] Slash command name is unique in your workspace
- [ ] Dialog parameters have valid `control_type` values
- [ ] `trigger_id` passed when opening dialogs
- [ ] Button `bot_command` references point to valid recipes
- [ ] Channel names sanitized for Slack requirements
- [ ] Datapill paths for context don't include `["body"]` wrapper

### For Native Slack (`slack`) recipes:

- [ ] `slack` provider in config section
- [ ] Connection name matches your Slack connection
- [ ] Datapill paths don't include `["body"]` wrapper
- [ ] Channel IDs use correct format (C... for public, G... for private)
- [ ] User IDs use correct format (U...)
