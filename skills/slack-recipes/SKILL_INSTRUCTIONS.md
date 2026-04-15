# Slack Recipes Skill - Agent Instructions

> **DEPENDENCY: Load `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects:
1. **Read existing Slack `.recipe.json` files** to understand local patterns
2. **Check for established domain/scope naming** conventions

### For GREENFIELD projects:
1. **Use skill templates** - see `templates/feedback-collection.json` as reference
2. **Use descriptive UUIDs** - e.g., `trigger-001`, `post-reply-002`

### ALWAYS:
1. **Ask for connection name** - exact name of Workbot/Slack connection in Workato
2. **Ask for slash command name** - verify it's not reserved (see list below)
3. **Ask for domain/scope** - avoid reserved words like "feedback", "help"
4. **Use descriptive UUIDs** - never copy random hex UUIDs from existing recipes

---

## CRITICAL: Environment Configuration Required

Before testing Workbot recipes, verify your Slack app is configured for your Workato environment:

1. Go to your Workbot connection in Workato
2. Open the OAuth profile settings
3. Follow the "Configuring your app manually" instructions
4. Update ALL URLs in your Slack app to match the environment-specific URLs shown
5. Ensure the `coak_id` parameter matches your OAuth profile ID

**When switching environments (e.g., trial → production), ALL Slack app URLs must be updated.**

Example URLs (trial environment):
```
Redirect URL: https://app.trial.workato.com/oauth/callback
Events URL: https://app.trial.workato.com/slack_webhooks/event?coak_id=XXX
Actions URL: https://app.trial.workato.com/slack_webhooks/actions?coak_id=XXX
Data Source URL: https://app.trial.workato.com/slack_webhooks/data_source?coak_id=XXX
```

**Required Slack Bot Token Scopes:**
- `app_mentions:read`, `channels:read`, `chat:write`, `commands`
- `files:read`, `files:write`, `groups.read`
- `im:history`, `im:write`, `mpim:read`
- `users:read`, `users:read.email`

**Required User Token Scopes:**
- `users:read`, `users:read.email`

---

This skill provides Slack-specific knowledge for generating Workato recipes. It covers **two Slack connectors**:

| Connector | Provider | Actions | Trigger | Use Case |
|-----------|----------|:---:|:---:|----------|
| **Workbot for Slack** | `slack_bot` | 3 + adhoc | `bot_command_v2` | Interactive bots, slash commands, dialogs, buttons |
| **Slack (native)** | `slack` | 9 | 2 triggers | Programmatic actions, button replies, channel management |

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

## Reserved Slack Command Names

**Always ask the user what slash command name to use.** Slack reserves certain command names that cannot be used:

`/feedback`, `/remind`, `/call`, `/dnd`, `/help`, `/invite`, `/leave`, `/me`, `/msg`, `/mute`, `/prefs`, `/search`, `/shortcuts`, `/status`, `/topic`, `/who`

Before generating a recipe with a slash command, verify the name is available in the user's workspace or explicitly ask for their preferred command name.

---

## Reserved Domain and Scope Names

**Avoid common words as `domain` or `scope` values** - they may conflict with existing Workbot functionality:

- `feedback`, `help`, `support`, `status`, `settings`, `admin`, `config`

**Use unique, project-specific names instead:**
- `shoe-request`, `myapp-feedback`, `project-onboarding`

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

### Workbot Actions Overview

The Workbot for Slack connector provides **4 built-in actions** and **1 trigger**.

#### Trigger

| Name | Description |
|------|-------------|
| `bot_command_v2` | Trigger on slash commands, button clicks, or dialog submissions |

#### Actions

| Name | Description | Notes |
|------|-------------|-------|
| `post_bot_reply_v2` | Reply to the triggering user in context | No channel ID needed |
| `post_bot_message` | Post a message to any channel or DM | Requires channel ID |
| `open_bot_dialog` | Open a dialog/modal to collect user input | Requires `trigger_id` from trigger context |

#### Raw HTTP

| Name | Description |
|------|-------------|
| `__adhoc_http_action` | Direct HTTP call to Slack API endpoints (e.g., `conversations.create`, `conversations.invite`, `users.info`) |

Use `__adhoc_http_action` for Slack API operations not covered by the 4 native Workbot actions: channel management, user lookups, file operations, etc. See [Adhoc HTTP Action](#adhoc-http-action-direct-slack-api) below.

---

### Workbot Command Trigger

The primary trigger for Slack recipes is `bot_command_v2`:

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
    "name": false,
    "scope": false
  },
  "input": {
    "allow_dialog": "true",
    "slash_command": {
      "enable": "true",
      "name": "/mycommand",
      "first_reply": "Processing your request..."
    },
    "scope": "project",
    "description": "Create a new project",
    "dialog_title": "New Project",
    "parameters": "[...]",
    "hide_from_help": "false",
    "name": "create",
    "domain": "my-app"
  }
}
```

### toggleCfg for Custom Values (CRITICAL)

The `toggleCfg` object controls whether fields use picklist selections or custom values:

| Field | `true` | `false` |
|-------|--------|---------|
| `domain` | Use picklist domain | Use custom domain value |
| `name` | Use picklist action name | Use custom action name |
| `scope` | Use picklist scope | Use custom scope value |

**For most custom Workbot commands, use:**
```json
"toggleCfg": {
  "domain": true,
  "name": false,
  "scope": false
}
```

### Input Attribute Ordering (CRITICAL)

**Attribute order matters for Workbot triggers.** Use this exact order:

1. `allow_dialog`
2. `slash_command`
3. `scope`
4. `description`
5. `dialog_title`
6. `parameters`
7. `hide_from_help`
8. `name`
9. `domain`

Incorrect ordering can cause the recipe to fail validation or behave unexpectedly
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

Parameters define the dialog form fields as a JSON string.

#### Text Parameters (Simple)

```json
{
  "name": "project_name",
  "label": "Project Name",
  "hint": "Enter the project name",
  "optional": "false",
  "control_type": "text"
}
```

#### Text-Area Parameters

```json
{
  "name": "comments",
  "label": "Comments",
  "hint": "Provide detailed feedback",
  "optional": "false",
  "control_type": "text-area"
}
```

#### Select Parameters (CRITICAL - Complete Structure Required)

**Select parameters require ALL these fields or the dialog won't display correctly:**

```json
{
  "name": "rating",
  "label": "Rating",
  "hint": "Rate from 1 to 5",
  "optional": true,
  "control_type": "select",
  "pick_list": [
    ["1 - Poor", "1"],
    ["2 - Fair", "2"],
    ["3 - Good", "3"],
    ["4 - Very Good", "4"],
    ["5 - Excellent", "5"]
  ],
  "type": "array",
  "prompt": "true",
  "dialog_data_source": "custom",
  "options": "1 - Poor,2 - Fair,3 - Good,4 - Very Good,5 - Excellent",
  "properties": []
}
```

**Required fields for select parameters:**

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Field identifier |
| `label` | Yes | Display label |
| `control_type` | Yes | Must be `"select"` |
| `pick_list` | Yes | Array of `[display, value]` pairs |
| `type` | **Yes** | Must be `"array"` |
| `prompt` | **Yes** | Must be `"true"` (as string) |
| `dialog_data_source` | Yes | Must be `"custom"` |
| `options` | **Yes** | Comma-separated display values |
| `properties` | **Yes** | Must be `[]` (empty array) |

**Missing any of these fields will cause the dialog to fail silently.**

#### Complete Parameters Example

```json
"parameters": "[
  {
    \"name\": \"rating\",
    \"label\": \"Rating\",
    \"hint\": \"Rate from 1 to 5\",
    \"optional\": true,
    \"control_type\": \"select\",
    \"pick_list\": [[\"1 - Poor\",\"1\"],[\"2 - Fair\",\"2\"],[\"3 - Good\",\"3\"]],
    \"type\": \"array\",
    \"prompt\": \"true\",
    \"dialog_data_source\": \"custom\",
    \"options\": \"1 - Poor,2 - Fair,3 - Good\",
    \"properties\": []
  },
  {
    \"name\": \"comments\",
    \"label\": \"Comments\",
    \"hint\": \"Provide details\",
    \"optional\": \"false\",
    \"control_type\": \"text-area\"
  }
]"
```

#### Control Types Summary

| Control Type | Description | Extra Fields Required |
|--------------|-------------|----------------------|
| `text` | Single-line text input | None |
| `text-area` | Multi-line text input | None |
| `select` | Dropdown | `type`, `prompt`, `options`, `properties`, `pick_list` |

---

## Slack Actions

### Choosing Between Message Actions

| Action | Use When | Channel Required? |
|--------|----------|-------------------|
| `post_bot_reply_v2` | Simple response to triggering user | **No** - replies to trigger context |
| `post_bot_message` | Post anywhere, including DMs | **Yes** - requires channel ID |

**Use `post_bot_reply_v2` for:**
- Confirming a slash command was received
- Showing results after dialog submission
- Any response back to the user who triggered the command

**Use `post_bot_message` for:**
- Posting to a specific channel
- Sending DMs (using user ID as channel)
- Notifications to channels other than where command was invoked

### Post Bot Message

Send a message to a channel or DM (requires channel ID):

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

### Native Slack Connector Guidance

The native Slack connector provides 9 actions and 2 triggers. See `lint-rules.json` for the authoritative list of valid action and trigger names.

#### Choosing the Right Trigger

- **`new_event`** — Subscribe to Slack events (new messages, reactions, channel changes, etc.).
- **`button_action`** — Trigger when a user clicks a button posted via the native Slack connector.

#### Choosing the Right Action

**Messaging:**
- **`post_message_to_channel`** — Post a message to a channel. Supports threading via `thread_ts`.
- **`post_button_action_reply`** — Reply to a button action interaction.

**Channel management:**
- **`create_conversation`** — Create a new channel. Set `private: "false"` for public channels.
- **`archive_conversation`** / **`unarchive_conversation`** — Archive or unarchive a channel.
- **`set_conversation_purpose`** / **`set_conversation_topic`** — Set a channel's purpose or topic text.
- **`invite_user_to_conversation`** — Invite a user to a channel. Requires channel ID + user ID.

**Users:**
- **`get_user_by_email`** — Look up a Slack user by email address. Returns user ID, name, profile, role flags.

See `patterns/native-slack-actions.md` for detailed examples and output fields.

---

## Datapill Paths

### Workbot Trigger Context (no body wrapper)

```json
"path": ["context", "user"]
"path": ["context", "trigger_id"]
"path": ["context", "channel"]
"path": ["parameters", "project_name"]
```

### Select Parameter Datapills (CRITICAL)

**Although select parameters are defined with `type: array`, the runtime output is a STRING.**

**CORRECT - simple path:**
```json
"path": ["parameters", "rating"]
```

**WRONG - causes "non array value" error:**
```json
"path": ["parameters", "rating", {"path_element_type": "current_index"}]
```

Do NOT use `current_index` or array iteration patterns with select parameter values. They return the selected value directly as a string

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

## Validation

See [validation-checklist.md](validation-checklist.md) for Slack-specific validation, which references the base checklist in `workato-recipes/validation-checklist.md`.

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Missing `toggleCfg` | Custom action names ignored | Add `toggleCfg` with `name: false` |
| Wrong input attribute order | Validation/runtime errors | Follow exact order documented above |
| Incomplete select params | Dialog doesn't display | Add ALL required fields: `type`, `prompt`, `options`, `properties` |
| `current_index` on select | "non array value" error | Use simple path: `["parameters", "field"]` |
| Reserved domain name | Conflicts with Workbot | Use unique names like `myapp-feedback` |
| Using `post_bot_message` for replies | Requires channel lookup | Use `post_bot_reply_v2` instead |
| Missing `dynamicPickListSelection` | Provider lookup fails | Add `{ "domain": "Slack" }` |
