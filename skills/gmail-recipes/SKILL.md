---
name: gmail-recipes
description: Gmail integration recipes for Workato. Enables AI agents to generate valid recipe JSON for Gmail operations including sending emails, listing/searching messages, managing labels, and message details.
license: MIT
metadata:
  author: Workato
  version: "1.0.0"
---

# Gmail Recipes Skill

> **DEPENDENCY: Run `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

You are now equipped with Gmail-specific knowledge for writing Workato recipes using the **native Gmail connector**.

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects:
1. **Read existing Gmail `.recipe.json` files** to understand local patterns

### For GREENFIELD projects:
1. **Use skill templates** - see `templates/` directory for validated examples
2. **Use descriptive UUIDs** - e.g., `list-emails-001`, `get-details-002`

### ALWAYS:
1. **Ask for connection name** - exact name of Gmail connection in Workato
2. **Confirm operation type** - send, list, search, or label management
3. **Use API endpoint trigger** for testability via curl
4. **Use descriptive UUIDs** - never copy random hex UUIDs from existing recipes
5. **Remember datapill paths** - adhoc HTTP uses `["body", ...]` wrapper

> **WARNING:** Gmail adhoc HTTP responses wrap data in `body`. Always use paths like `["body", "messages"]` for list/search results.

---

## Capabilities

With this skill loaded, you can:
- Create recipes that send emails (text/HTML) with attachments
- Create recipes that list and search emails with Gmail query syntax
- Create recipes that get full message details
- Create recipes that manage labels (create, list, apply, remove)
- Create recipes that archive or modify messages
- Create callable API endpoint recipes for Gmail operations

---

## Gmail Connector

This skill covers the **native Gmail connector** (`gmail`) which provides:
- 3 native actions for core email operations (send, get by ID, download attachment)
- 1 trigger for new email arrival
- Adhoc HTTP actions for all other Gmail REST API operations (list, search, labels, user info, modify, delete, threads, drafts)

### Connector Limitations

> **Important:** The native Gmail connector is built on the **Gmail REST API v1** with a hardcoded base URL (`https://www.googleapis.com/gmail/v1/users/`). This means:
>
> - **3 native actions + 1 trigger** — covers send, get email/draft by ID, and download attachment
> - **Adhoc HTTP required** for most operations: list/search emails, labels, user info, message modification, deletion, threads, drafts
> - **API version locked** - Cannot access newer Gmail API features not in v1
>
> If a user needs functionality not supported by the v1 API, recommend they:
> 1. Check the Workato Community Library for updated Gmail connectors
> 2. Consider building a custom SDK connector with the needed endpoints
> 3. Use the HTTP connector with custom OAuth for full API flexibility

> **Note:** Developers can build custom SDK connectors for Gmail with additional actions. See `workato-recipes/patterns/custom-connector-actions.md` for custom connector patterns. Custom connectors are not included with Workato by default.

---

## Gmail-Specific Knowledge

### Provider

Use `gmail` for the native Gmail connector:

```json
"provider": "gmail"
```

### Connection Configuration

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

### Gmail API Base URL

For adhoc HTTP actions, Gmail uses:
```
https://www.googleapis.com/gmail/v1/users/
```

Common paths:
- `me/messages` - List messages
- `me/messages/{id}` - Get message details
- `me/labels` - List labels
- `me/labels/{id}` - Get/modify label

### Datapill Paths

**Native actions** (like `send_mail`) return data without `body` wrapper:
```json
"path": ["id"]
"path": ["threadId"]
"path": ["labelIds"]
```

**Adhoc HTTP actions** wrap responses in `body`:
```json
"path": ["body", "messages"]
"path": ["body", "id"]
"path": ["body", "labelIds"]
```

### Gmail Query Syntax

The `q` parameter supports Gmail search operators:
- `from:sender@example.com` - From specific sender
- `to:recipient@example.com` - To specific recipient
- `subject:keyword` - Subject contains keyword
- `is:unread` - Unread messages
- `is:starred` - Starred messages
- `has:attachment` - Has attachments
- `after:2024/01/01` - After date
- `before:2024/12/31` - Before date
- `label:INBOX` - Has specific label

Combine with spaces: `from:boss@company.com is:unread has:attachment`

### Optional Parameters Pattern

For optional query parameters, use `.presence || skip`:

```json
"input": {
  "data": {
    "maxResults": "=_dp('{...}').presence || skip",
    "pageToken": "=_dp('{...}').presence || skip",
    "q": "=_dp('{...}').presence || skip",
    "labelIds": "=_dp('{...}').presence || skip"
  }
}
```

---

## Native Connector Guidance

The Gmail connector provides 3 native actions and 1 trigger. See `lint-rules.json` for the authoritative list of valid action and trigger names.

### Trigger

- **`new_email`** — Fires when a new email arrives in the connected account.

### Choosing the Right Approach

**Native actions (use these when possible):**
- **`send_mail`** — Send an email (text or HTML) with optional attachments. See [detail below](#send_mail-detail).
- **`get_email_or_draft_by_id`** — Get full details of a single email or draft by message ID. Returns headers, body, labels, snippet.
- **`download_attachment`** — Download an attachment by message ID and attachment ID.

**Adhoc HTTP required for everything else:**
- **List/search emails** — Use `__adhoc_http_action` with `GET me/messages` and Gmail query syntax via the `q` parameter. See [adhoc patterns below](#adhoc-http-patterns).
- **Labels** — List, create, modify, delete, apply, or remove labels via `me/labels` endpoints.
- **User info** — Get Gmail profile via `me/profile`.
- **Message operations** — Modify (add/remove labels, archive), delete, trash via `me/messages/{id}/modify`, `me/messages/{id}/trash`.
- **Threads and drafts** — Full thread and draft management via `me/threads`, `me/drafts`.

See `patterns/gmail-api-reference.md` for the full endpoint catalog.

---

### send_mail Detail

Send an email with optional attachments:

```json
{
  "provider": "gmail",
  "name": "send_mail",
  "keyword": "action",
  "input": {
    "email_type": "html",
    "to": "recipient@example.com",
    "subject": "Email Subject",
    "body": "<p>HTML content here</p>",
    "from": "sender-alias@example.com",
    "cc": "cc@example.com",
    "bcc": "bcc@example.com",
    "reply_to": "reply-to@example.com",
    "attachments": {
      "____source": "#{_dp('{...path to attachments array}')}",
      "file_binary_content": "#{_dp('{...path to file content}')}",
      "file_name": "#{_dp('{...path to file name}')}"
    }
  }
}
```

**Email types:**
- `"text"` - Plain text email
- `"html"` - HTML formatted email

**Output fields:**
- `id` - Message ID
- `threadId` - Thread ID
- `labelIds` - Array of label IDs

---

## Adhoc HTTP Patterns

### List Messages

```json
{
  "provider": "gmail",
  "name": "__adhoc_http_action",
  "keyword": "action",
  "input": {
    "mnemonic": "List Emails",
    "verb": "get",
    "response_type": "json",
    "path": "me/messages",
    "input": {
      "schema": "[...]",
      "data": {
        "maxResults": "=_dp('{...}').presence || skip",
        "q": "=_dp('{...}').presence || skip"
      }
    },
    "output": "[{\"name\":\"messages\",\"type\":\"array\",\"of\":\"object\",\"properties\":[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"threadId\",\"type\":\"string\"}]}]"
  }
}
```

### Get Message Details

```json
{
  "provider": "gmail",
  "name": "__adhoc_http_action",
  "keyword": "action",
  "input": {
    "mnemonic": "Get Message Details",
    "verb": "get",
    "response_type": "json",
    "path": "me/messages/#{_dp('{...message_id}')}",
    "output": "[{\"name\":\"id\",\"type\":\"string\"},{\"name\":\"threadId\",\"type\":\"string\"},{\"name\":\"labelIds\",\"type\":\"array\",\"of\":\"string\"},{\"name\":\"snippet\",\"type\":\"string\"},{\"name\":\"payload\",\"type\":\"object\",\"properties\":[...]}]"
  }
}
```

---

## Common Patterns

### List + Enrich Pattern

Gmail's list endpoint returns minimal data (just IDs). To get full details, use a foreach loop:

1. List messages (returns IDs only)
2. Declare a list variable
3. Foreach message ID:
   - Get message details
   - Add to list variable
4. Return enriched list

See `templates/list-emails.json` for a complete example.

### Error Handling

Wrap Gmail operations in try/catch for robust error handling:

```json
{
  "keyword": "try",
  "block": [
    // Gmail operations
  ]
},
{
  "keyword": "catch",
  "block": [
    // Return error response
  ]
}
```

---

## Validation

See [validation-checklist.md](validation-checklist.md) for Gmail-specific validation, which references the base checklist in `workato-recipes/validation-checklist.md`.

---

## Reference Files

- `skills/workato-recipes/SKILL.md` - Base platform knowledge
- `skills/gmail-recipes/patterns/native-gmail-actions.md` - Native action details
- `skills/gmail-recipes/patterns/gmail-api-reference.md` - API endpoint reference
- `skills/gmail-recipes/templates/` - Validated recipe templates

---

## Usage

### Before Generating Recipes

**Ask the user for these details:**

1. **Gmail connection name** - What is their Gmail connection called?
   - Example: "My Gmail account"

2. **Operation type** - Send, list, search, or manage labels?

3. **Trigger type** - API endpoint, scheduler, or event-driven?

### Recipe Generation Steps

1. Ask for connection name (REQUIRED)
2. Identify the operation needed
3. Determine if native action or adhoc HTTP is required
4. Generate valid JSON using base skill structure + Gmail specifics

---

## Example Prompts

- "Create a recipe that sends an HTML email with attachments via API"
- "Create a recipe that lists unread emails from a specific sender"
- "Create a recipe that searches for emails and returns full details"
- "Create a recipe that applies a label to matching emails"
