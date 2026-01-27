# Native Slack Connector Actions

The **Slack connector** (`provider: "slack"`) provides built-in actions for programmatic Slack operations. This is distinct from **Workbot for Slack** (`provider: "slack_bot"`) which handles interactive bot experiences.

---

## When to Use Native Slack Connector

Use the native Slack connector when:
- Building API-triggered recipes that interact with Slack
- You need programmatic actions without user interaction
- Creating callable recipes for other systems to invoke
- You don't need slash commands, dialogs, or buttons

Use Workbot for Slack when:
- Building interactive slash commands
- Collecting user input via dialogs/modals
- Creating button-based workflows
- Responding to user actions in real-time

---

## Config Section

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

---

## Available Actions

### Post Message to Channel

```json
{
  "number": 1,
  "provider": "slack",
  "name": "post_message_to_channel",
  "as": "post_message",
  "keyword": "action",
  "toggleCfg": {
    "channel": false
  },
  "input": {
    "channel": "C1234567890",
    "text": "Hello from Workato!",
    "parse": "false"
  },
  "uuid": "post-message-001"
}
```

**Output fields:**
- `ts` - Message timestamp (used for threading/updates)
- `thread_ts` - Thread timestamp
- `channel` - Channel ID
- `type` - Message type

### Create Conversation (Channel)

```json
{
  "number": 1,
  "provider": "slack",
  "name": "create_conversation",
  "as": "create_channel",
  "keyword": "action",
  "toggleCfg": {
    "private": true
  },
  "input": {
    "conversation_name": "project-channel",
    "private": "false"
  },
  "uuid": "create-channel-001"
}
```

**Output fields:**
- `id` - Channel ID
- `name` - Channel name

### Get User by Email

```json
{
  "number": 1,
  "provider": "slack",
  "name": "get_user_by_email",
  "as": "lookup_user",
  "keyword": "action",
  "input": {
    "email": "user@example.com"
  },
  "uuid": "lookup-user-001"
}
```

**Output fields:**
- `id` - User ID
- `name` - Username
- `real_name` - Display name
- `team_id` - Workspace ID
- `profile.email` - Email address
- `profile.display_name` - Display name
- `is_admin`, `is_owner`, `is_bot` - Role flags

### Invite User to Channel

```json
{
  "number": 1,
  "provider": "slack",
  "name": "invite_user_to_channel",
  "as": "invite_user",
  "keyword": "action",
  "input": {
    "channel": "C1234567890",
    "user": "U1234567890"
  },
  "uuid": "invite-user-001"
}
```

### Archive Conversation

```json
{
  "number": 1,
  "provider": "slack",
  "name": "archive_conversation",
  "as": "archive_channel",
  "keyword": "action",
  "input": {
    "channel": "C1234567890"
  },
  "uuid": "archive-001"
}
```

### Unarchive Conversation

```json
{
  "number": 1,
  "provider": "slack",
  "name": "unarchive_conversation",
  "as": "unarchive_channel",
  "keyword": "action",
  "input": {
    "channel": "C1234567890"
  },
  "uuid": "unarchive-001"
}
```

### Set Conversation Purpose

```json
{
  "number": 1,
  "provider": "slack",
  "name": "set_conversation_purpose",
  "as": "set_purpose",
  "keyword": "action",
  "input": {
    "channel": "C1234567890",
    "purpose": "This channel is for project discussions"
  },
  "uuid": "set-purpose-001"
}
```

---

## Datapill Paths

Native Slack connector outputs **do not use a `body` wrapper**:

```json
// CORRECT - direct path
"path": ["id"]
"path": ["name"]
"path": ["profile", "email"]
"path": ["ts"]

// WRONG - no body wrapper
"path": ["body", "id"]  // Incorrect for native Slack
```

### Example Datapill References

```json
// Channel ID from create_conversation
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack\",\"line\":\"create_channel\",\"path\":[\"id\"]}')}"

// User email from get_user_by_email
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack\",\"line\":\"lookup_user\",\"path\":[\"profile\",\"email\"]}')}"

// Message timestamp from post_message_to_channel
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"slack\",\"line\":\"post_message\",\"path\":[\"ts\"]}')}"
```

---

## Callable Recipe Pattern

Native Slack actions are commonly used in **callable recipes** exposed via API endpoint:

```json
{
  "name": "Create Channel API",
  "code": {
    "provider": "workato_api_platform",
    "name": "receive_request",
    "keyword": "trigger",
    "input": {
      "request": {
        "content_type": "json",
        "schema": "[{\"name\":\"channel_name\",\"type\":\"string\"}]"
      },
      "response": {
        "content_type": "json",
        "responses": [
          {
            "http_status_code": "200",
            "name": "Success",
            "body_schema": "[{\"name\":\"channel_id\",\"type\":\"string\"}]"
          }
        ]
      }
    },
    "block": [
      {
        "provider": "slack",
        "name": "create_conversation",
        "input": {
          "conversation_name": "#{_dp('...[\"request\",\"channel_name\"]')}"
        }
      },
      {
        "provider": "workato_api_platform",
        "name": "return_response",
        "input": {
          "http_status_code": "200",
          "response": {
            "channel_id": "#{_dp('...[\"id\"]')}"
          }
        }
      }
    ]
  },
  "config": [
    {
      "keyword": "application",
      "provider": "workato_api_platform",
      "account_id": null
    },
    {
      "keyword": "application",
      "provider": "slack",
      "account_id": {
        "zip_name": "my_slack_account.connection.json",
        "name": "My Slack account"
      }
    }
  ]
}
```

---

## Comparison: Native Slack vs Workbot

| Feature | Native Slack (`slack`) | Workbot (`slack_bot`) |
|---------|------------------------|----------------------|
| Slash commands | No | Yes |
| Dialogs/modals | No | Yes |
| Buttons | No | Yes |
| Post messages | Yes | Yes |
| Create channels | Yes | Via adhoc HTTP |
| User lookup | Yes (`get_user_by_email`) | Via adhoc HTTP |
| Triggered by | API, scheduler, other triggers | User interaction |
| Best for | Programmatic automation | Interactive workflows |

---

## Pre-Push Checklist

- [ ] `slack` provider in config (not `slack_bot`)
- [ ] Connection name matches your Slack connection
- [ ] Datapill paths don't include `body` wrapper
- [ ] Channel IDs use correct format (C... for public, G... for private)
- [ ] User IDs use correct format (U...)
