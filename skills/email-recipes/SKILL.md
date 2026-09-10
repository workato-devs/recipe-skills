---
name: email-recipes
description: Native Workato Email connector recipes. Enables AI agents to generate valid recipe JSON for sending email notifications via the built-in `email` connector.
license: MIT
metadata:
  author: Your Name
  version: "1.0.0"
---

# Email Recipes Skill

> **DEPENDENCY: Load the `workato-recipes` base skill first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

You are now equipped with knowledge for writing Workato recipes using the **native Email connector** (`email`) — a built-in, connection-free way to send an email notification from inside a recipe.

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects:
1. **Read existing recipes using the `email` provider** to confirm the exact field set already in use in this project

### For GREENFIELD projects:
1. **Use the skill template** — see `templates/send-email.json` for a validated example
2. **Use descriptive UUIDs** — e.g., `send-notification-001`

### ALWAYS:
1. **Config uses `account_id: null`** — the Email connector has no external account to connect; do not ask the user for a connection name for it
2. **Confirm `email_type`** — `"text"` or `"html"`
3. **Use descriptive UUIDs** — never copy random hex UUIDs from existing recipes

---

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Email Config Requirements](#email-config-requirements)
3. [Native Connector Guidance](#native-connector-guidance)
4. [Email Datapill Paths](#email-datapill-paths)
5. [How These Names Were Verified](#how-these-names-were-verified)
6. [Common Patterns](#common-patterns)
7. [Validation](#validation)
8. [Templates](#templates)
9. [References](#references)

---

## When to Use This Skill

Use the native Email connector when a recipe needs to send a simple, one-off email notification (an alert, a status update, an error report) and does not need to read a mailbox, manage threads/labels, or send from a specific mailbox identity. If the recipe needs to send *from* or *read* a real mailbox (Gmail, Outlook, etc.), use that connector's skill instead (e.g. `gmail-recipes`) — the native Email connector is a platform utility, not a mailbox integration.

---

## Email Config Requirements

```json
{
  "keyword": "application",
  "name": "email",
  "provider": "email",
  "skip_validation": false,
  "account_id": null
}
```

`account_id` is always `null` — there is no OAuth flow or credential to configure for this connector.

---

## Native Connector Guidance

The Email connector provides 1 verified native action and 0 verified triggers. See `lint-rules.json` for the authoritative list.

### Choosing the Right Action

- **`send_mail`** — Use whenever a recipe needs to send an email notification. It's the only verified action; there is no adhoc-HTTP fallback documented here since this connector has no underlying REST API endpoint to call directly.

```json
{
  "provider": "email",
  "name": "send_mail",
  "keyword": "action",
  "input": {
    "email_type": "html",
    "to": "recipient@example.com",
    "subject": "Notification subject",
    "body": "<p>Notification body</p>"
  }
}
```

**Email types:**
- `"text"` — Plain text email
- `"html"` — HTML formatted email

Only `to`, `subject`, `body`, and `email_type` have been observed in real usage. Fields like `cc`, `bcc`, `reply_to`, or `attachments` may or may not exist on this action — do not assume they do without verifying first (see [How These Names Were Verified](#how-these-names-were-verified)).

---

## Email Datapill Paths

No recipe in the verified source workspace ever consumed `send_mail`'s output — none of the observed usages reference an output datapill from this action. Do not invent an output schema for it. If you need to reference its output, verify the actual field names first by activating a scratch recipe (see below) and inspecting the job's output before wiring a datapill to it.

---

## How These Names Were Verified

Unlike connectors backed by a public SDK or vendor API docs, the native Email connector has no accessible schema to read ahead of time. `send_mail` was confirmed valid two ways:
1. It appears, with an identical field set, in 3 separate production recipes in a live Workato workspace.
2. A minimal test recipe using `send_mail` was imported into a scratch folder and successfully activated (`wk recipes start`); a control recipe using a fabricated action name on the same `email` provider was imported the same way and never activated (timed out), confirming Workato does validate the action name at activation time even though `wk recipes import` alone does not.

If you need to verify a candidate action or trigger name for this connector, repeat this technique in a disposable scratch recipe rather than guessing from memory or general documentation — then delete the scratch recipe once you have your answer.

---

## Common Patterns

### Notify on Failure

Wrap the risky action(s) in `try`/`catch` and send a `send_mail` notification from the `catch` block, referencing the catch's error message:

```json
{
  "provider": "email",
  "name": "send_mail",
  "keyword": "action",
  "input": {
    "email_type": "html",
    "to": "oncall@example.com",
    "subject": "Recipe failed",
    "body": "Error: #{_dp('{\"pill_type\":\"output\",\"provider\":\"catch\",\"line\":\"<catch-alias>\",\"path\":[\"message\"]}')}"
  }
}
```

See [try-catch.md](../workato-recipes/control-flow/try-catch.md) in the base skill for the full try/catch structure.

---

## Validation

See [validation-checklist.md](validation-checklist.md) for the full checklist. Always run the base checklist first.

---

## Templates

- [`templates/send-email.json`](templates/send-email.json) — A callable recipe that sends a `send_mail` notification and returns a `sent` boolean. Pushed and activation-verified against a live Workato workspace.

---

## References

- **Base Skill:** `workato-recipes` — recipe structure, triggers, control flow, formulas
- **Related:** `gmail-recipes` — for recipes that need to send from or read an actual mailbox rather than a platform notification
