# Gmail API Reference

Quick reference for Gmail REST API endpoints accessible via adhoc HTTP actions.

**Base URL:** `https://www.googleapis.com/gmail/v1/users/`

---

## Messages

### List Messages
```
GET me/messages
```

Query parameters:
| Parameter | Description |
|-----------|-------------|
| `maxResults` | Max messages to return (default 100, max 500) |
| `pageToken` | Token for pagination |
| `q` | Gmail search query |
| `labelIds` | Filter by label IDs |
| `includeSpamTrash` | Include spam/trash (default false) |

### Get Message
```
GET me/messages/{id}
```

Query parameters:
| Parameter | Description |
|-----------|-------------|
| `format` | `full`, `metadata`, `minimal`, or `raw` |
| `metadataHeaders` | Headers to include when format=metadata |

### Modify Message
```
POST me/messages/{id}/modify
```

Request body:
```json
{
  "addLabelIds": ["LABEL_ID"],
  "removeLabelIds": ["LABEL_ID"]
}
```

### Trash Message
```
POST me/messages/{id}/trash
```

### Untrash Message
```
POST me/messages/{id}/untrash
```

### Delete Message
```
DELETE me/messages/{id}
```

---

## Labels

### List Labels
```
GET me/labels
```

### Get Label
```
GET me/labels/{id}
```

### Create Label
```
POST me/labels
```

Request body:
```json
{
  "name": "Label Name",
  "labelListVisibility": "labelShow",
  "messageListVisibility": "show"
}
```

### Update Label
```
PATCH me/labels/{id}
```

### Delete Label
```
DELETE me/labels/{id}
```

---

## Threads

### List Threads
```
GET me/threads
```

Query parameters: Same as List Messages

### Get Thread
```
GET me/threads/{id}
```

### Modify Thread
```
POST me/threads/{id}/modify
```

### Trash Thread
```
POST me/threads/{id}/trash
```

---

## Drafts

### List Drafts
```
GET me/drafts
```

### Get Draft
```
GET me/drafts/{id}
```

### Create Draft
```
POST me/drafts
```

### Update Draft
```
PUT me/drafts/{id}
```

### Send Draft
```
POST me/drafts/send
```

### Delete Draft
```
DELETE me/drafts/{id}
```

---

## Common Response Schemas

### Message List Response
```json
{
  "messages": [
    { "id": "string", "threadId": "string" }
  ],
  "nextPageToken": "string",
  "resultSizeEstimate": 123
}
```

### Message Detail Response
```json
{
  "id": "string",
  "threadId": "string",
  "labelIds": ["string"],
  "snippet": "string",
  "historyId": "string",
  "internalDate": "string",
  "payload": {
    "partId": "string",
    "mimeType": "string",
    "filename": "string",
    "headers": [
      { "name": "string", "value": "string" }
    ],
    "body": {
      "size": 123,
      "data": "base64-encoded-string"
    },
    "parts": [/* nested parts */]
  },
  "sizeEstimate": 123
}
```

### Label Response
```json
{
  "id": "string",
  "name": "string",
  "type": "system|user",
  "messageListVisibility": "show|hide",
  "labelListVisibility": "labelShow|labelShowIfUnread|labelHide",
  "messagesTotal": 123,
  "messagesUnread": 45,
  "threadsTotal": 67,
  "threadsUnread": 12
}
```

---

## System Label IDs

| Label | ID |
|-------|----|
| Inbox | `INBOX` |
| Sent | `SENT` |
| Drafts | `DRAFT` |
| Spam | `SPAM` |
| Trash | `TRASH` |
| Starred | `STARRED` |
| Important | `IMPORTANT` |
| Unread | `UNREAD` |
| All Mail | `ALL` |

---

## Gmail Search Operators

Use in the `q` parameter:

| Operator | Example | Description |
|----------|---------|-------------|
| `from:` | `from:john@example.com` | From sender |
| `to:` | `to:jane@example.com` | To recipient |
| `cc:` | `cc:team@example.com` | CC'd recipient |
| `bcc:` | `bcc:secret@example.com` | BCC'd recipient |
| `subject:` | `subject:meeting` | Subject contains |
| `is:` | `is:unread`, `is:starred` | Message state |
| `has:` | `has:attachment` | Has attachment |
| `in:` | `in:inbox`, `in:sent` | In folder/label |
| `label:` | `label:work` | Has label |
| `after:` | `after:2024/01/01` | After date |
| `before:` | `before:2024/12/31` | Before date |
| `newer_than:` | `newer_than:7d` | Within time period |
| `older_than:` | `older_than:1m` | Older than period |
| `filename:` | `filename:report.pdf` | Attachment name |
| `size:` | `size:5m` | Larger than size |
| `larger:` | `larger:10m` | Larger than |
| `smaller:` | `smaller:1m` | Smaller than |

Combine operators: `from:boss@company.com is:unread has:attachment after:2024/01/01`
