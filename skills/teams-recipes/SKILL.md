---
name: teams-recipes
description: Microsoft Teams Workbot (teams_bot) recipes for Workato. Enables AI agents to generate valid recipe JSON for bot commands, user lookup, and block message posting.
license: MIT
metadata:
  author: Your Name
  version: "1.10.0"
---

# Teams Recipes Skill

> **DEPENDENCY: Load the `workato-recipes` base skill first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

You are now equipped with knowledge for writing Workato recipes using **Workbot for Microsoft Teams** (`teams_bot`) — a connector for receiving slash-style bot commands from Teams users and posting block-based messages back.

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects:
1. **Read existing recipes using the `teams_bot` provider** to see what bot commands are already registered on the target connection
2. **Never reuse an existing `action_name`** on the same connection — each `bot_command` trigger's `action_name` must be unique across the whole Teams bot

### For GREENFIELD projects:
1. **Use the skill template** — see `templates/bot-command-notify.json` for a validated example
2. **Use descriptive UUIDs** — e.g., `lookup-caller-002`, `post-notify-003`

### ALWAYS:
1. **Ask for the connection name** — exact name of the Teams Workbot connection in Workato
2. **Confirm the desired `action_name`** — this becomes the Teams-visible command name; check it isn't already used
3. **Decide the user-lookup mode** — by `principal_name` (email/UPN) or `id` (Azure AD object ID) — see [Native Connector Guidance](#native-connector-guidance)

---

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Teams Config Requirements](#teams-config-requirements)
3. [Native Connector Guidance](#native-connector-guidance)
4. [Teams Datapill Paths](#teams-datapill-paths)
5. [Block Types Reference](#block-types-reference)
6. [Common Patterns](#common-patterns)
7. [Validation](#validation)
8. [Templates](#templates)
9. [References](#references)

---

## When to Use This Skill

Use this skill when a recipe needs to expose a command that Teams users invoke from within Microsoft Teams (via Workbot), look up the invoking (or another) Teams user's identity, and/or post a message — including one with an actionable button — into a Teams channel or DM. This is not a general Microsoft Graph/Teams API integration; it only covers what the `teams_bot` connector's own actions and trigger expose.

---

## Teams Config Requirements

```json
{
  "keyword": "application",
  "name": "teams_bot",
  "provider": "teams_bot",
  "skip_validation": false,
  "account_id": 558004
}
```

`account_id` must reference a real Teams Workbot connection — unlike the native Email connector, this one requires an actual connection.

---

## Native Connector Guidance

The Teams connector provides 9 verified native actions and 4 verified triggers — every trigger/action visible in the connector's own picker is now verified. See `lint-rules.json` for the authoritative list.

**A naming-convention warning:** Workato's internal trigger/action `name` does not reliably follow the doc's UI label. Confirmed twice: the docs' "New help message trigger" is internally `help_event`, not `new_help_message`; the docs' "New message trigger" is internally `new_message_event`, not `new_message`. Never assume a doc label maps predictably to an internal name — verify against the actual connector (the recipe editor's connector/action picker, or real recipe usage) every time.

**A trigger-family warning:** the connector's own trigger picker offers a 4th trigger, "New real-time event" (internal name `new_event`), which Workato's public documentation doesn't mention at all. It's a single generic, polymorphic trigger — not a fixed shape — whose `event_name` input picks which specific real-time event it receives, and whose output schema changes per event. See [patterns/real-time-events.md](patterns/real-time-events.md); it also explains why the doc's "Tab opened trigger" and "Show tab using Adaptive Cards" action appear to not be available at all on the bot connection this skill was verified against.

> **CRITICAL: never use `wait_for_interval` (base skill, [patterns/wait-delay.md](../workato-recipes/patterns/wait-delay.md)) inside a recipe triggered by `bot_command` — and presumably `help_event`/`new_message_event` too, since the connector's own trigger picker labels all three "Real-time."** Confirmed via an actual job failure with the exact platform error: `"Use of long actions is not allowed in WorkBot recipes"`. This isn't a soft recommendation, it's a hard platform rule for Workbot triggers. If a recipe needs to pause before a follow-up action (e.g. deleting a message a few seconds/minutes after posting it), use a `text_with_button_block` with `button_type: "action_continue_flow"` instead — see [Block Types Reference](#block-types-reference) and the [Common Patterns](#common-patterns) entry below. Waiting on user interaction this way does not trip the same restriction.

### Choosing the Right Trigger

- **`bot_command`** — Use to expose a new slash-style command to Teams users. Requires a unique `action_name` and a `parameters` field (a JSON-stringified array of parameter definitions — each needs `name`, `label`, `type`, `control_type`, `optional`). The trigger's output includes both the declared `parameters` (per your schema) and a `context` object carrying details about the invoking user and conversation (e.g. `context.from.aadObjectId`). Also carries `hide_from_help` (string `"true"`/`"false"`) — every observed production trigger sets this explicitly, even when `false`.
  - **Parameter data types observed in production:** a plain string parameter uses `"type": "string"` + `"control_type": "text"`. A date-picker parameter uses `"type": "date_time"` + `"control_type": "date"` (plus `"parse_output": "date_conversion"` / `"render_input": "date_conversion"` in the trigger's own `extended_output_schema` entry for that field) — confirmed in a live production `bot_command` trigger. No `file`-type parameter has been observed in this workspace; do not assume it works without confirming first.
- **`help_event`** — Use to reply with a fully custom message when a user sends `help` to the bot (DM or @mention). Takes no input. Like `bot_command`, its output carries a `context` object, and `context.from.aadObjectId` resolves the same way — feed it straight into `get_user_by_principal_name`'s `id` input to look up and reply to whoever asked for help. Only one `help_event` recipe can be active per bot at a time (per Workato's own documentation) — this is a bot-wide singleton, not a per-command trigger, so treat activating/deactivating it with more care than an ordinary `bot_command`. Activation-tested end-to-end: sending `help` to a live bot with this trigger active returns the configured reply.
- **`new_message_event`** — Use to respond when a user DMs or @mentions the bot with text that doesn't match any registered `bot_command`. Confirmed via the connector's trigger picker; supports an optional trigger condition (a `filter` block) to scope it to specific channels, per the doc's "New message trigger" feature. Full output schema confirmed live (see [Teams Datapill Paths](#teams-datapill-paths)) — all fields are **camelCase**, not the snake_case the doc's field labels would suggest (`messageText`, not `message_text`).
- **`new_event`** — A single generic trigger for real-time Bot Framework invoke events, selected via its `event_name` input (a live-search field, not a static list). Only the `application/search` ("Typeahead search") event has been confirmed available on the bot connection this skill was verified against, with a fully captured live output schema. See [patterns/real-time-events.md](patterns/real-time-events.md) for the schema, the top-level (not `context`-nested) `from.aadObjectId` path, and why tab/task-module-related events appear unavailable here.

### Choosing the Right Action

- **`get_user_by_principal_name`** — Looks up a Teams user. Despite the name, this action has been observed in live recipes with **two different input fields**: `principal_name` (an email/UPN string) in one recipe, and `id` (an Azure AD object ID — typically taken straight from a `bot_command` trigger's `context.from.aadObjectId`) in three others. Use `id` when you already have the caller's AAD object ID from a `bot_command` trigger context; use `principal_name` when you only have an email address (e.g. sourced from another system, as in the [shared Teams ID resolver pattern](patterns/shared-teams-id-resolver.md)). Do not set both fields on the same action.
- **`post_blocks_message`** — Posts a message built from one or more `blocks` **to a specific channel or user** (this is the UI's "Post message" action — confirmed by direct picker selection, its auto-generated description matches exactly). Requires `channel`, which accepts either a datapill (from `get_user_by_principal_name`'s `id` output, or from a `call_recipe`'d resolver — see [Common Patterns](#common-patterns)) or a static, hardcoded Teams user ID string — both are confirmed in production recipes. Use this when posting somewhere other than where a command was invoked, or from a recipe that isn't itself a `bot_command`/`help_event` (e.g. a scheduled notification). Its output is a single field, `id` (the new message's ID) — confirmed via a live job run. See [Block Types Reference](#block-types-reference) for what each block type supports.
- **`post_blocks_reply_message`** — The UI's "Post reply" action — a **distinct action from `post_blocks_message`**, confirmed by direct picker selection (auto-generated description: "Post reply to user as Workbot"). Unlike `post_blocks_message`, it has **no `channel`/recipient field** — it implicitly replies to wherever the invoking command came from. Per Workato's own docs, "Post reply must always be paired with a Workbot command" — use it only from a `bot_command` or `help_event` recipe, not a recipe with no live Teams invocation context. Its `blocks` field is presumed (not yet confirmed) to accept the same block types as `post_blocks_message`.
- **`delete_message`** — Deletes a previously posted message. Fully activation-tested end-to-end in a live `bot_command` recipe: the posted message visibly appeared in Teams and was then deleted. Takes `conversation_id` and `message_id`. `message_id` comes from a `post_blocks_message`/`post_blocks_reply_message`'s `id` output. `conversation_id` comes from **`context.conversation.id`** on the triggering `bot_command`/`help_event` — the same `context` object that carries `from.aadObjectId`, just a different branch of it. **`conversation_id` is NOT the same as a Teams user ID** — do not source it from `get_user_by_principal_name`'s `id` output (confirmed wrong via an earlier live job failure).
- **`post_simple_message` / `post_simple_reply`** — Reduced-feature siblings of `post_blocks_message`/`post_blocks_reply_message`: plain Markdown text, no rich blocks or buttons. Same recipient rules as their `_blocks_` counterparts (`post_simple_message` needs a recipient; `post_simple_reply`, like `post_blocks_reply_message`, does not). Confirmed via direct picker selection; use these only when a recipe genuinely doesn't need blocks/buttons — otherwise prefer the `_blocks_` actions, which are far better documented in this skill.
- **`post_bot_message` / `post_bot_reply`** — The doc's "Post message (old version)" / "Post reply (old version)." Confirmed via direct picker selection; both carry a `use_json` field not present on the newer actions, which is very likely where the doc's "Post as raw JSON" (fully custom Adaptive Card JSON) feature actually lives — not on `post_blocks_message`/`post_blocks_reply_message`. Presumed deprecated; prefer `post_blocks_message`/`post_blocks_reply_message` for new recipes unless raw JSON control is specifically needed and confirmed to only exist here.
- **`invoke_response`** — The picker's "Response to real-time event," not documented anywhere in Workato's own Workbot-for-Teams docs (same as `new_event`, which it pairs with). Use it to respond to a `new_event` firing. For the `application/search` event: full schema confirmed live — `type` is fixed (`application/vnd.microsoft.search.searchResponse`, read-only), `value.results` is an array of `{title, value}` (typically from a dynamic list datapill). Matches Microsoft Bot Framework's public dynamic-search response format exactly. Schema confirmed; a full live round trip through a real Adaptive Card has not — see [patterns/real-time-events.md](patterns/real-time-events.md).
- **Anything else (the picker's "Custom action")** — this is NOT a connector-specific action. Confirmed via direct picker selection: it resolves to the standard `__adhoc_http_action`, exactly like every other connector skill in this repo. Use the base `workato-recipes` skill's adhoc HTTP patterns, not connector-specific guidance, when a recipe needs a Microsoft Graph API call this connector's native actions don't cover.

---

## Teams Datapill Paths

Native action/trigger datapills do NOT use a `["body"]` wrapper. Notable paths:

- Trigger declared parameters: `["parameters", "<param_name>"]`
- Trigger caller context (`bot_command`, `help_event`): `["context", "from", "aadObjectId"]`
- Trigger conversation ID (`bot_command`, `help_event`): `["context", "conversation", "id"]` — activation-confirmed as `delete_message`'s `conversation_id` input. Same `context` object as the path above, different branch — found via the live datapill tree, not `extended_output_schema` (which never declares `context` at all for these triggers).
- Trigger caller context (`new_event`): `["from", "aadObjectId"]` — **top-level, not nested under `context`.** Confirmed different from `bot_command`/`help_event`'s shape; see [patterns/real-time-events.md](patterns/real-time-events.md).
- `new_message_event`'s full output — ALL top-level, ALL camelCase (confirmed live by dragging every field the editor's datapill tree showed and reading back the real paths): `["messageId"]`, `["messageText"]`, `["timestamp"]`, `["serviceUrl"]`, `["conversationId"]`, `["conversationType"]`, `["sentFromId"]`, `["sentFromName"]`, `["userId"]`, `["recipientId"]`, `["recipientName"]`, and `["attachments"]` (an array — each item has `contentType`/`contentUrl`/`name` directly, plus a nested `content` object with `downloadUrl`/`uniqueId`/`fileType`).
- `get_user_by_principal_name` output: `["id"]` (the Teams user ID — feed this into `post_blocks_message`'s `channel` field to message that user directly)
- `post_blocks_message` output: `["id"]` (the posted message's ID — confirmed via a live job run; feed this into `delete_message`'s `message_id` field, or a follow-up post's "message to update" field). When the message includes an `action_continue_flow` button, this same step's output ALSO gains `["conversation_id"]` and `["user_selection", ...]` once the job resumes — see [Block Types Reference](#block-types-reference).

---

## Block Types Reference

`post_blocks_message`'s `blocks` array has been observed with two `block_type`s in live recipes:

**`text_block`** — plain or markdown-ish text. Two `text_type` variants are confirmed in production:

- `"text_type": "body_text"` — standard message text:
  ```json
  {
    "block_type": "text_block",
    "text_block": {
      "text": "Some message text, markdown-flavored links/bold supported",
      "text_type": "body_text"
    }
  }
  ```
- `"text_type": "custom"` with `separator` and `style.isSubtle` — used for a visually de-emphasized trailing note (e.g. a footer/disclaimer line below the main message and its buttons):
  ```json
  {
    "block_type": "text_block",
    "text_block": {
      "text": "No action needed if this was already handled elsewhere.",
      "text_type": "custom",
      "separator": "true",
      "style": {
        "isSubtle": "true"
      }
    }
  }
  ```

**`text_with_button_block`** — text with an actionable button. Two `button_type` values are confirmed, matching two different doc-described UI behaviors, and they are NOT interchangeable:

### `button_type: "submit"` (doc's "Run bot command") — invokes a *different* command

Use when the button should kick off a separate flow (a different `bot_command`), in a new job. The button can only carry values that already existed before this message was posted — it cannot reference the message's own future ID (see the `action_continue_flow` case below for that).

```json
{
  "block_type": "text_with_button_block",
  "text_with_button_block": {
    "text": "Snooze this for 30 days?",
    "button_title": "Snooze",
    "button_type": "submit",
    "bot_command": "rm_snoozerp",
    "params": "=\"{\\\"rpid\\\": \\\"\" + _dp('{\"pill_type\":\"output\",...,\"path\":[\"parameters\",\"rpid\"]}').to_s + \"\\\", \\\"date\\\": \\\"\" + (today + 30).strftime('%d.%m.%Y') + \"\\\"}\"",
    "open_task_module": "false"
  }
}
```

`params` is a JSON-encoded string matching the target command's `bot_command` trigger's own `parameters` schema. Two building styles are both confirmed in production:
- **Static/passthrough values** — a plain string with an embedded datapill: `"{\"rpid\": \"#{_dp('...')}\" }"`.
- **Computed values** (e.g. a date offset) — full formula mode (string starts with `=`), concatenating literal JSON fragments with `.to_s`-cast datapill values and formula methods like `(today + 30).strftime('%d.%m.%Y')`. See the base skill's [variables-and-lists.md](../workato-recipes/patterns/variables-and-lists.md) for formula-mode string building, and `templates/bot-command-buttons-reply.json` for a full worked example of both styles in the same recipe.

### `button_type: "action_continue_flow"` (doc's "Continue recipe") — suspends the *same* job until clicked

Use when the button needs to act on something that only exists once this SAME message has been posted (classically: deleting the very message the button is attached to) — or any case where you want the current job to pause and resume with the user's response, rather than kicking off a separate job. Confirmed live via direct field selection + save, then a full activation test.

```json
{
  "block_type": "text_with_button_block",
  "text_with_button_block": {
    "button_type": "action_continue_flow",
    "text": "Hello! 👋",
    "button_title": "Dismiss"
  }
}
```

Optional fields also confirmed: `header_text`, `button_id` (distinguishes which button was clicked when a message has more than one — pairs with the `selected_block_id` output below), `separator` (string boolean).

A sibling **top-level** input field, `timeout`, appears on the `post_blocks_message`/`post_blocks_reply_message` action itself (not inside the block) once any `action_continue_flow` button exists in its `blocks`:
```json
{
  "channel": "...",
  "blocks": [ /* ... including an action_continue_flow block ... */ ],
  "timeout": "22"
}
```
`timeout` is an integer in **minutes** — confirmed via the field's own UI hint ("Default value is 43200 minutes") — do not assume seconds despite the bare numeric string. If the timeout elapses with no click, the job continues automatically.

Once the button is clicked (or the timeout elapses), the job resumes, and this same `post_blocks_message`/`post_blocks_reply_message` step's output gains new fields not present without a continue-flow button: a top-level `conversation_id`, and a `user_selection` object (`selected_button`, `selected_block_id`, and a `user` object with `id`/`username`/`team_id`). The message's own `id` output (needed for `delete_message`) does not appear in this expanded schema but was confirmed to still resolve as a valid datapill — this connector's `extended_output_schema` is not exhaustive.

**`button_type` values NOT yet verified:** the doc also describes an "Open URL" button behavior — no internal `button_type` value for it has been captured yet.

No other block types have been verified — do not assume additional block types (e.g. images, adaptive-card JSON blocks) exist without confirming first (see the verification note in `lint-rules.json`).

---

## Common Patterns

### Command → Lookup → Reply

The standard shape for a Teams bot command: receive the command, resolve the caller's Teams user record, then reply to them directly.

1. `bot_command` trigger declares the command's parameters
2. `get_user_by_principal_name` resolves the caller using `context.from.aadObjectId` from the trigger
3. `post_blocks_message` sends the reply, using the lookup action's `id` output as the `channel`

See `templates/bot-command-notify.json` for the full working example.

### Custom Help Message

The same lookup-then-reply shape works for `help_event` as for `bot_command` — the only difference is there are no declared `parameters` to read, since the trigger fires on the literal word `help`, not a registered command. See `templates/custom-help-message.json`.

### Button That Invokes Another Command

A `text_with_button_block` can chain into a second bot command: set `bot_command` to that command's `action_name`, and `params` to a JSON string of the values that command's own trigger `parameters` expect. See `templates/bot-command-buttons-reply.json` for a working example with two buttons chaining into two different commands.

### Auto-Expiring / Self-Deleting Message

A common need: post a message, then delete it a short while later, or once the user acknowledges it. Two hard constraints shape how this has to be built, both discovered building this exact pattern:

1. **`wait_for_interval` cannot be used** — a recipe triggered by `bot_command` (or `help_event`/`new_message_event`) fails outright with `"Use of long actions is not allowed in WorkBot recipes"` if it contains one. A fixed, unconditional delay inside a Workbot-triggered recipe is not possible.
2. **A `submit`-type button can't reference the message's own future ID** — its `params` can only carry values that existed before the message was posted.

The working shape instead uses an `action_continue_flow` button on the message itself:

1. `bot_command`/`help_event` trigger fires
2. `get_user_by_principal_name` resolves the caller
3. `post_blocks_message` posts the message with a `text_with_button_block` (`button_type: "action_continue_flow"`, e.g. `button_title: "Dismiss"`) and a `timeout` (minutes) — the job suspends here
4. On click (or timeout), the job resumes; `delete_message` deletes the same message, using this step's own earlier `id` output for `message_id`, and the *trigger's* `context.conversation.id` for `conversation_id`

**Fully activation-tested end-to-end**, including the click: a human tester started the recipe, sent `hossa` in Teams, saw the message with its "Dismiss" button, clicked it, and confirmed the message was deleted. This is the strongest verification level of any multi-step pattern in this skill — every piece (`bot_command`, the lookup, `post_blocks_message` with an `action_continue_flow` button, and `delete_message` with `context.conversation.id`) proven together in one real, observed run.

### Notifying Someone Who Isn't the Caller

Not every recipe that posts a Teams message is itself a `bot_command` — for example, a scheduled or record-driven recipe that notifies a record's owner. In that case there's no `context.from.aadObjectId` to resolve. Production usage centralizes this into a shared callable recipe that turns an external-system identifier into a Teams user ID via `get_user_by_principal_name`'s `principal_name` input, called with `call_recipe`. See [patterns/shared-teams-id-resolver.md](patterns/shared-teams-id-resolver.md).

---

## Validation

See [validation-checklist.md](validation-checklist.md) for the full checklist. Always run the base checklist first.

---

## Templates

- [`templates/bot-command-notify.json`](templates/bot-command-notify.json) — A `bot_command` trigger that looks up the calling user and posts a text-block reply. Structurally validated by import against a live Workato workspace; the two actions it uses (`get_user_by_principal_name`, `post_blocks_message`) were additionally activation-verified in a scratch recipe. The trigger itself was intentionally not activation-tested to avoid registering a live, Teams-visible bot command as a side effect — its shape is instead backed by two identical real production recipes.
- [`templates/bot-command-buttons-reply.json`](templates/bot-command-buttons-reply.json) — A richer `bot_command` example: a `date_time`/`date` parameter alongside a `string` one, a lookup, and a reply with a markdown `text_block`, two `text_with_button_block`s (one static-params, one formula-built dynamic-params) each chaining into a different follow-up command, and a trailing `text_type: "custom"` subtle footer block. Field values are genericized from real production recipes (see `lint-rules.json`'s `_notes` for the verification trail); structurally import-validated against a live Workato workspace. Not activation-tested, for the same reason as above.
- [`templates/custom-help-message.json`](templates/custom-help-message.json) — A `help_event` trigger that looks up the user who asked for help and posts a custom reply. Fully activation-tested end-to-end by a human tester: started the recipe, sent `help` to a live bot in Teams, confirmed the reply, then stopped it. The strongest verification level of any template in this skill.
- [`templates/self-deleting-message.json`](templates/self-deleting-message.json) — A `bot_command` that posts a message with a "Dismiss" `action_continue_flow` button and a 22-minute timeout, then deletes it via `delete_message` once clicked (or once the timeout elapses). Fully activation-tested end-to-end, click included — see [Auto-Expiring / Self-Deleting Message](#common-patterns).

---

## References

- **Base Skill:** `workato-recipes` — recipe structure, triggers, control flow, formulas
- **Related:** `slack-recipes`' `slack_bot` variant — the closest structural precedent (a chat-platform Workbot), useful for comparison if extending this skill further
- **Pattern:** [patterns/shared-teams-id-resolver.md](patterns/shared-teams-id-resolver.md) — centralizing external-ID-to-Teams-ID resolution in a callable recipe
- **Pattern:** [patterns/real-time-events.md](patterns/real-time-events.md) — the generic `new_event` trigger, its `event_name` picklist, and the Typeahead search event's full schema
