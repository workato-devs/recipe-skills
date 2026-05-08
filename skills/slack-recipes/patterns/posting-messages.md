# Posting Messages

This pattern covers posting messages to Slack channels and DMs using Workbot for Slack.

---

## Choosing the Right Action

| Action | Channel Required | Use Case |
|--------|------------------|----------|
| `post_bot_reply_v2` | **No** | Reply directly to the triggering user/context |
| `post_bot_message` | **Yes** | Post to a specific channel or DM |

### post_bot_reply_v2 (Recommended for Simple Responses)

Use when you want to respond directly to the user who triggered the command. No channel ID needed:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "post_bot_reply_v2",
  "as": "reply_to_user",
  "keyword": "action",
  "input": {
    "message": {
      "title": "Success!",
      "attachment_text": "Your request has been processed."
    }
  },
  "uuid": "reply-to-user-001"
}
```

### post_bot_message (For Specific Channels)

Use when you need to post to a specific channel or send a DM to someone other than the triggering user:

```json
{
  "number": 1,
  "provider": "slack_bot",
  "name": "post_bot_message",
  "as": "send_to_channel",
  "keyword": "action",
  "input": {
    "channel": "C1234567890",
    "message": {
      "title": "Notification",
      "attachment_text": "Something happened."
    }
  },
  "uuid": "send-to-channel-001"
}
```

---

## Post Bot Message (Detailed)

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
        "params": "request_id: 123"
      },
      {
        "title": "Reject",
        "bot_command": {
          "zip_name": "Recipes/handle_rejection.recipe.json",
          "name": "Handle Rejection",
          "folder": "Recipes"
        },
        "params": "request_id: 123"
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

---

## `update_blocks_by_block_id` — Mutating an Already-Posted Message

The canonical action for updating a previously-posted message in place. Most commonly used to **clean up after an interactive button click** — once a manager has clicked Approve, you want to remove the buttons so the message can't be re-clicked.

### Action Structure

```json
{
  "number": 5,
  "provider": "slack_bot",
  "name": "update_blocks_by_block_id",
  "as": "remove_buttons",
  "keyword": "action",
  "input": {
    "surface": "message",
    "message_json": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack_bot\",\"line\":\"trigger_001\",\"path\":[\"context\",\"original_message_json\"]}')}",
    "blocks_to_update": [
      {
        "block_id": "approve_deny_buttons",
        "remove_block": "true",
        "blocks": [
          {
            "type": "section",
            "block_id": "decision_summary",
            "text": {
              "type": "mrkdwn",
              "text": ":white_check_mark: *Approved* by <@#{_dp('...user_id...')}>"
            }
          }
        ]
      }
    ]
  },
  "uuid": "remove-buttons-001"
}
```

### Input Fields

| Field | Required | Description |
|-------|----------|-------------|
| `surface` | Yes | Always `"message"` for posted Slack messages |
| `message_json` | Yes | The full JSON of the original message — passed through from the Workbot trigger context (`context.original_message_json`). The action uses this to find which message to mutate |
| `blocks_to_update` | Yes | Array of update operations, one per `block_id` to mutate |
| `blocks_to_update[].block_id` | Yes | The `block_id` of the existing block to update (must match what was assigned when the message was originally posted) |
| `blocks_to_update[].remove_block` | No | `"true"` to remove the existing block entirely. If you also supply `blocks`, those are inserted in its place |
| `blocks_to_update[].blocks` | No | Replacement block(s) to insert. Standard Slack Block Kit shape (`type`, `block_id`, `text`, etc.) |

### Patterns

**Remove buttons after a click, leave a static confirmation:**

Set `remove_block: "true"` on the buttons block and supply a single `section` block in `blocks` with the new confirmation text. The button row disappears, replaced by a "✅ Approved by @manager" line.

**Remove a block without replacing it:**

Set `remove_block: "true"` and supply an empty `blocks: []`.

**Replace block content without removing the block_id:**

Omit `remove_block` and supply `blocks` with the new content. The block_id stays put; its content is overwritten.

### Setup Requirements (When Posting the Original Message)

To use `update_blocks_by_block_id` later, the *original* `post_bot_message` must have given each interactive block a stable `block_id`. The default Workato message helpers don't do this for you — you have to construct the message in raw block form:

```json
{
  "name": "post_bot_message",
  "input": {
    "channel": "...",
    "message": {
      "blocks": [
        { "type": "section", "block_id": "summary", "text": { ... } },
        {
          "type": "actions",
          "block_id": "approve_deny_buttons",
          "elements": [ ... button definitions ... ]
        }
      ]
    }
  }
}
```

The receiver recipe then references `block_id: "approve_deny_buttons"` to remove or replace that row.
