# Native Gmail Actions

The native Gmail connector (`gmail`) provides built-in actions for common email operations.

---

## send_mail

Send an email with optional attachments.

### Basic Structure

```json
{
  "number": 1,
  "provider": "gmail",
  "name": "send_mail",
  "as": "unique_id",
  "keyword": "action",
  "input": {
    "email_type": "html",
    "to": "recipient@example.com",
    "subject": "Subject Line",
    "body": "<p>Email body content</p>",
    "from": "optional-alias@example.com",
    "cc": "cc@example.com",
    "bcc": "bcc@example.com",
    "reply_to": "reply-to@example.com"
  },
  "uuid": "action-uuid-here"
}
```

### Input Fields

| Field | Required | Description |
|-------|----------|-------------|
| `email_type` | Yes | `"text"` or `"html"` |
| `to` | Yes | Recipient email address |
| `subject` | Yes | Email subject line |
| `body` | Yes | Email body (plain text or HTML based on type) |
| `from` | No | Sender alias (must be configured in Gmail settings) |
| `cc` | No | CC recipients (comma-separated) |
| `bcc` | No | BCC recipients (comma-separated) |
| `reply_to` | No | Reply-to email address |
| `attachments` | No | Array of file attachments |

### With Attachments

```json
{
  "provider": "gmail",
  "name": "send_mail",
  "keyword": "action",
  "input": {
    "email_type": "html",
    "to": "#{_dp('{...}')}",
    "subject": "#{_dp('{...}')}",
    "body": "#{_dp('{...}')}",
    "attachments": {
      "____source": "#{_dp('{\"pill_type\":\"output\",...,\"path\":[\"request\",\"attachments\"]}')}",
      "file_binary_content": "#{_dp('{...path to file content}')}",
      "file_name": "#{_dp('{...path to file name}')}"
    }
  }
}
```

The `____source` field maps the source array for iteration. Each item provides `file_binary_content` and `file_name`.

### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message ID |
| `threadId` | string | Thread ID this message belongs to |
| `labelIds` | array | Labels applied to the message |

### Accessing Output

Native actions return data **without** the `body` wrapper:

```json
// Message ID
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"gmail\",\"line\":\"action_id\",\"path\":[\"id\"]}')}

// Thread ID
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"gmail\",\"line\":\"action_id\",\"path\":[\"threadId\"]}')}

// Label IDs (as array)
"=_dp('{\"pill_type\":\"output\",\"provider\":\"gmail\",\"line\":\"action_id\",\"path\":[\"labelIds\"]}')"
```

---

## Conditional Email Type

Handle both text and HTML email types:

```json
{
  "keyword": "if",
  "input": {
    "type": "compound",
    "operand": "and",
    "conditions": [
      {
        "operand": "equals_to",
        "lhs": "=_dp('{...path to type field}')",
        "rhs": "HTML"
      }
    ]
  },
  "block": [
    {
      "provider": "gmail",
      "name": "send_mail",
      "input": {
        "email_type": "html",
        // ... other fields
      }
    }
  ]
},
{
  "keyword": "else",
  "block": [
    {
      "provider": "gmail",
      "name": "send_mail",
      "input": {
        "email_type": "text",
        // ... other fields
      }
    }
  ]
}
```

---

## Error Handling Pattern

```json
{
  "keyword": "try",
  "block": [
    {
      "provider": "gmail",
      "name": "send_mail",
      "as": "send_action",
      "input": { /* ... */ }
    },
    {
      "provider": "workato_api_platform",
      "name": "return_response",
      "input": {
        "http_status_code": "200",
        "response": {
          "id": "#{_dp('{...path to id}')}",
          "thread_id": "#{_dp('{...path to threadId}')}"
        }
      }
    }
  ]
},
{
  "as": "error_handler",
  "keyword": "catch",
  "input": {
    "max_retry_count": "0",
    "retry_interval": "2"
  },
  "block": [
    {
      "provider": "workato_api_platform",
      "name": "return_response",
      "input": {
        "http_status_code": "500",
        "response": {
          "error_message": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"catch\",\"line\":\"error_handler\",\"path\":[\"message\"]}')}"
        }
      }
    }
  ]
}
```

---

## Connection Configuration

```json
{
  "keyword": "application",
  "provider": "gmail",
  "skip_validation": false,
  "account_id": {
    "zip_name": "my_gmail_account.connection.json",
    "name": "My Gmail account",
    "folder": ""
  }
}
```

The `name` field should match the user's Gmail connection name in Workato.
