# Gmail Recipes Skill

> **DEPENDENCY: Run `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

You are now equipped with Gmail-specific knowledge for writing Workato recipes using the **native Gmail connector** (`gmail`).

## Capabilities

With this skill loaded, you can:
- Create recipes that send emails (text/HTML) with attachments
- Create recipes that list and search emails with Gmail query syntax
- Create recipes that get full message details
- Create recipes that manage labels (create, list, apply, remove)
- Create callable API endpoint recipes for Gmail operations

## Gmail Connector

The native Gmail connector provides:
- Built-in `send_mail` action for sending emails
- Adhoc HTTP actions for direct Gmail REST API calls

### Connector Limitations

The native connector is built on **Gmail REST API v1** with a hardcoded base URL. This means:
- Limited built-in actions (only `send_mail`)
- Most operations require adhoc HTTP calls
- Cannot access newer API features not in v1

**If users need unsupported functionality**, recommend they:
1. Check the Workato Community Library for updated connectors
2. Consider a custom SDK connector
3. Use the HTTP connector with custom OAuth

## Gmail-Specific Knowledge

### Provider

Always use `gmail` for the native connector:

```json
"provider": "gmail"
```

### Gmail API Base URL

For adhoc HTTP actions:
```
https://www.googleapis.com/gmail/v1/users/
```

### Datapill Paths (CRITICAL)

**Native actions** return data without `body` wrapper:
```json
"path": ["id"]
"path": ["threadId"]
```

**Adhoc HTTP actions** wrap responses in `body`:
```json
"path": ["body", "messages"]
"path": ["body", "id"]
```

### Optional Parameters Pattern

For optional query parameters, use `.presence || skip`:

```json
"data": {
  "maxResults": "=_dp('{...}').presence || skip",
  "q": "=_dp('{...}').presence || skip"
}
```

## Reference Files

- `skills/workato-recipes/SKILL_INSTRUCTIONS.md` - Base platform knowledge
- `skills/gmail-recipes/SKILL_INSTRUCTIONS.md` - Gmail-specific knowledge
- `skills/gmail-recipes/patterns/` - Pattern documentation
- `skills/gmail-recipes/templates/` - Validated recipe templates
- `skills/gmail-recipes/validation-checklist.md` - Gmail validation checklist
- `skills/workato-recipes/validation-checklist.md` - Base validation checklist

## Usage

### Before Generating Recipes

**CRITICAL: Always ask the user for these details first:**

1. **Gmail connection name** - What is the exact name of their Gmail connection?
   - Example: "My Gmail account"
   - This will be used in the `account_id.name` field

2. **Operation type** - What do they need to do? (send, list, search, labels)

3. **Trigger type** - API endpoint, scheduler, or event-driven?

### Recipe Generation Steps

1. **Ask for connection name** (REQUIRED)
2. **Identify the operation** - Send email, list/search, manage labels?
3. **Determine if native action or adhoc HTTP** - send_mail vs API calls
4. **Generate valid JSON** using base skill structure + Gmail specifics

## Example Prompts

- "Create a recipe that sends an HTML email with attachments via API"
- "Create a recipe that lists unread emails from a specific sender"
- "Create a recipe that searches for emails and returns full details"
- "Create a recipe that applies a label to matching emails"
