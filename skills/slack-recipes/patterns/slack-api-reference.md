# Slack API Reference

Quick reference for Slack API methods available via adhoc HTTP actions.

> **See also:** `workato-recipes/patterns/adhoc-http-actions.md` for the general adhoc HTTP pattern.

---

## Using Adhoc HTTP with Slack

Both `slack_bot` (Workbot) and `slack` (native) connectors support adhoc HTTP actions for calling Slack API endpoints directly.

```json
{
  "provider": "slack_bot",  // or "slack"
  "name": "__adhoc_http_action",
  "input": {
    "verb": "post",
    "request_type": "json",
    "response_type": "json",
    "path": "conversations.create",
    "input": { "data": { "name": "channel-name" } }
  }
}
```

Base URL: `https://slack.com/api/`

---

## Common Slack API Methods

### Conversations (Channels)

| Method | Description | Verb |
|--------|-------------|------|
| `conversations.create` | Create a channel | POST |
| `conversations.invite` | Invite users to channel | POST |
| `conversations.list` | List channels | GET |
| `conversations.info` | Get channel info | GET |
| `conversations.setTopic` | Set channel topic | POST |
| `conversations.setPurpose` | Set channel purpose | POST |
| `conversations.archive` | Archive a channel | POST |
| `conversations.unarchive` | Unarchive a channel | POST |
| `conversations.rename` | Rename a channel | POST |
| `conversations.kick` | Remove user from channel | POST |

### Users

| Method | Description | Verb |
|--------|-------------|------|
| `users.info` | Get user info by ID | GET |
| `users.lookupByEmail` | Find user by email | GET |
| `users.list` | List workspace users | GET |

### Messages

| Method | Description | Verb |
|--------|-------------|------|
| `chat.postMessage` | Post a message | POST |
| `chat.update` | Update a message | POST |
| `chat.delete` | Delete a message | POST |
| `reactions.add` | Add emoji reaction | POST |
| `reactions.remove` | Remove emoji reaction | POST |

### Files

| Method | Description | Verb |
|--------|-------------|------|
| `files.upload` | Upload a file | POST |
| `files.list` | List files | GET |
| `files.info` | Get file info | GET |
| `files.delete` | Delete a file | POST |

---

## Request Examples

### Create Channel

```json
"path": "conversations.create",
"input": {
  "schema": "[{\"name\":\"name\",\"type\":\"string\"},{\"name\":\"is_private\",\"type\":\"boolean\"}]",
  "data": {
    "name": "project-alpha",
    "is_private": "false"
  }
},
"output": "[{\"name\":\"ok\",\"type\":\"boolean\"},{\"name\":\"channel\",\"type\":\"object\",\"properties\":[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"name\",\"type\":\"string\"}]}]"
```

### Invite User to Channel

```json
"path": "conversations.invite",
"input": {
  "schema": "[{\"name\":\"channel\",\"type\":\"string\"},{\"name\":\"users\",\"type\":\"string\"}]",
  "data": {
    "channel": "C1234567890",
    "users": "U1234567890,U0987654321"
  }
}
```

### Set Channel Topic

```json
"path": "conversations.setTopic",
"input": {
  "schema": "[{\"name\":\"channel\",\"type\":\"string\"},{\"name\":\"topic\",\"type\":\"string\"}]",
  "data": {
    "channel": "C1234567890",
    "topic": "Project Alpha - Q1 Planning"
  }
}
```

### Get User Info

```json
"path": "users.info",
"verb": "get",
"input": {
  "schema": "[{\"name\":\"user\",\"type\":\"string\"}]",
  "data": {
    "user": "U1234567890"
  }
},
"output": "[{\"name\":\"ok\",\"type\":\"boolean\"},{\"name\":\"user\",\"type\":\"object\",\"properties\":[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"name\",\"type\":\"string\"},{\"name\":\"real_name\",\"type\":\"string\"},{\"name\":\"profile\",\"type\":\"object\",\"properties\":[{\"name\":\"email\",\"type\":\"string\"}]}]}]"
```

### Post Message

```json
"path": "chat.postMessage",
"input": {
  "schema": "[{\"name\":\"channel\",\"type\":\"string\"},{\"name\":\"text\",\"type\":\"string\"},{\"name\":\"thread_ts\",\"type\":\"string\"}]",
  "data": {
    "channel": "C1234567890",
    "text": "Hello from Workato!",
    "thread_ts": ""
  }
}
```

### Add Reaction

```json
"path": "reactions.add",
"input": {
  "schema": "[{\"name\":\"channel\",\"type\":\"string\"},{\"name\":\"timestamp\",\"type\":\"string\"},{\"name\":\"name\",\"type\":\"string\"}]",
  "data": {
    "channel": "C1234567890",
    "timestamp": "1234567890.123456",
    "name": "thumbsup"
  }
}
```

---

## Response Handling

### Success Response

Slack API returns `ok: true` on success:

```json
{
  "ok": true,
  "channel": {
    "id": "C1234567890",
    "name": "project-alpha"
  }
}
```

### Error Response

Slack API returns `ok: false` with error details:

```json
{
  "ok": false,
  "error": "channel_not_found"
}
```

### Common Error Codes

| Error | Description |
|-------|-------------|
| `channel_not_found` | Channel doesn't exist or bot not a member |
| `user_not_found` | User ID invalid |
| `not_in_channel` | Bot not in the channel |
| `is_archived` | Channel is archived |
| `name_taken` | Channel name already exists |
| `invalid_auth` | Authentication failed |
| `missing_scope` | OAuth scope not granted |

---

## Channel Name Rules

When creating channels via API:
- Lowercase only
- Max 80 characters
- Letters, numbers, hyphens, underscores only
- No leading/trailing hyphens

Sanitization formula:
```ruby
.downcase.gsub(/[^a-z0-9]/, '-').gsub(/-+/, '-').gsub(/^-|-$/, '')[0..79]
```

---

## Documentation

- [Slack API Methods](https://api.slack.com/methods)
- [Slack API Error Reference](https://api.slack.com/methods#errors)
- [Slack API Rate Limits](https://api.slack.com/docs/rate-limits)
