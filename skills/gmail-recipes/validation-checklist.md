# Gmail Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

The following checks are specific to Gmail connector recipes.

---

## Config & Connection

- [ ] Config includes `gmail` provider with connection reference
- [ ] Action `name` matches a valid name in `lint-rules.json` or is `__adhoc_http_action`

## Datapill Paths

- [ ] Native action datapills (e.g., `send_mail`) do NOT use `["body"]` wrapper — use `["id"]`, `["threadId"]`
- [ ] Adhoc HTTP action datapills DO use `["body"]` wrapper — use `["body", "messages"]`, `["body", "id"]`

## Adhoc HTTP Actions

- [ ] Gmail API paths are relative to base URL — use `me/messages`, `me/labels`, etc.
- [ ] Optional query parameters use `.presence || skip` pattern
- [ ] Response `output` schema is a stringified JSON array
- [ ] `verb`, `response_type` are specified

## `send_mail` Action

- [ ] `email_type` is specified (`"text"` or `"html"`)
- [ ] Attachment arrays use `____source` pattern with `file_binary_content` and `file_name`

## Gmail Query Syntax

- [ ] Search queries use Gmail query operators (`from:`, `to:`, `subject:`, `is:unread`, `has:attachment`, etc.)
- [ ] Query string passed in `q` parameter of list/search adhoc HTTP requests
