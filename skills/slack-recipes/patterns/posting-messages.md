# Posting Messages

This pattern covers posting messages to Slack channels and DMs using Workbot for Slack.

---

## Post Bot Message

Send a message to a specific channel or user DM:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "post_bot_message",
  "as": "send_notification",
  "keyword": "action",
  "toggleCfg": {
    "channel": true
  },
  "input": {
    "channel": "C1234567890",
    "text": "Plain text message content",
    "message": {
      "title": "Message Title",
      "attachment_text": "**Rich** formatted content with _markdown_"
    }
  },
  "visible_config_fields": [
    "channel",
    "text"
  ],
  "uuid": "send-notification-001"
}
```

---

## Channel Targeting

### Send to Specific Channel

Use channel ID directly:

```json
"channel": "C1234567890"
```

### Send DM to Triggering User

Reference the user from trigger context:

```json
"channel": "=_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"user\"]}').gsub('\"','')"
```

> **Note:** The `.gsub('\"','')` removes any surrounding quotes from the user ID.

### Send to Channel from Trigger

Use the channel where the command was invoked:

```json
"channel": "=_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"channel\"]}').gsub('\"','')"
```

---

## Message Formatting

### Plain Text

Simple text without formatting:

```json
"text": "This is a plain text message"
```

### Rich Message with Attachment

Use `message` object for rich formatting:

```json
"message": {
  "title": "Notification Title",
  "attachment_text": "**Bold text** and _italics_\n\nNew paragraph with details."
}
```

### Message with Multiple Sections

```json
"message": {
  "title": "Project Created Successfully",
  "attachment_text": "**Project Details:**\n• Name: #{_dp('...')}\n• Owner: #{_dp('...')}\n• Status: Active\n\n**Next Steps:**\nYour project workspace is ready."
}
```

---

## Post Bot Reply with Buttons

Send an interactive reply with buttons:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "post_bot_reply_v2",
  "as": "reply_with_options",
  "keyword": "action",
  "toggleCfg": {
    "attachment_buttons.0.bot_command": true,
    "attachment_buttons.1.bot_command": true
  },
  "input": {
    "message": {
      "title": "Approval Required",
      "attachment_text": "Please review and take action on this request."
    },
    "attachment_buttons": [
      {
        "title": "Approve",
        "bot_command": {
          "zip_name": "Recipes/handle_approval.recipe.json",
          "name": "Handle Approval",
          "folder": "Recipes"
        },
        "params": "request_id=123"
      },
      {
        "title": "Reject",
        "bot_command": {
          "zip_name": "Recipes/handle_rejection.recipe.json",
          "name": "Handle Rejection",
          "folder": "Recipes"
        },
        "params": "request_id=123"
      }
    ]
  }
}
```

### Button Configuration

| Field | Description |
|-------|-------------|
| `title` | Button label text |
| `bot_command` | Recipe to invoke when clicked |
| `bot_command.zip_name` | Path to recipe JSON file |
| `bot_command.name` | Recipe display name |
| `bot_command.folder` | Folder containing recipe |
| `params` | Parameters passed to target recipe |

### Passing Dynamic Data to Buttons

Pass trigger context or parameters to button actions:

```json
"params": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"trigger_id\"]}')}"
```

---

## Message with Fields

Display structured data in columns:

```json
"input": {
  "message": {
    "title": "Ticket #1234",
    "attachment_text": "New support ticket submitted"
  },
  "attachment_fields": [
    {
      "title": "Priority",
      "value": "High",
      "short": true
    },
    {
      "title": "Status",
      "value": "Open",
      "short": true
    },
    {
      "title": "Description",
      "value": "Full description text here...",
      "short": false
    }
  ]
}
```

---

## Error Message Pattern

Send error notifications to users:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "post_bot_message",
  "as": "error_message",
  "keyword": "action",
  "input": {
    "channel": "=_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"user\"]}').gsub('\"','')",
    "text": "An error occurred while processing your request.\n\n**Error Details:**\n#{_dp('{\"pill_type\":\"output\",\"provider\":\"catch\",\"line\":\"error_handler\",\"path\":[\"message\"]}')}\n\nPlease try again or contact support."
  }
}
```

---

## Success Confirmation Pattern

Confirm successful operations:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "post_bot_message",
  "as": "success_message",
  "keyword": "action",
  "input": {
    "channel": "=_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"user\"]}').gsub('\"','')",
    "message": {
      "title": "Success!",
      "attachment_text": "Your request has been processed.\n\n**Summary:**\n• Item: #{_dp('...')}\n• Status: Complete\n• Reference: ##{_dp('...')}"
    }
  }
}
```
