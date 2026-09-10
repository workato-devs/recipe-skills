# Email Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

The following checks are specific to the native Email connector.

---

## Config & Connection

- [ ] Config includes an `email` provider entry with `account_id: null` (this connector has no external connection to authenticate)
- [ ] Action `name` matches a valid name in `lint-rules.json` or is `__adhoc_http_action`

## Datapill Paths

- [ ] `send_mail` action datapills do NOT use a `["body"]` wrapper (native action, not adhoc HTTP)

## `send_mail` Action

- [ ] `email_type` is specified (`"text"` or `"html"`)
- [ ] `to`, `subject`, and `body` are all present
