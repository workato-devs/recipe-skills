# Teams Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

The following checks are specific to the Workbot for Microsoft Teams (`teams_bot`) connector.

---

## Config & Connection

- [ ] Config includes a `teams_bot` provider entry with a real connection `account_id`
- [ ] Action/trigger `name` matches a valid name in `lint-rules.json` or is `__adhoc_http_action`

## Datapill Paths

- [ ] `bot_command` trigger datapills do NOT use a `["body"]` wrapper (native trigger, not adhoc HTTP)
- [ ] Trigger parameters are read from `["parameters", "<param_name>"]`; caller context (e.g. the invoking user's Azure AD object ID) is read from `["context", "from", "aadObjectId"]`; the invoking conversation's ID is read from `["context", "conversation", "id"]` (activation-confirmed as `delete_message`'s `conversation_id` source)

## `bot_command` Trigger

- [ ] `action_name` is a unique command name across this Teams bot connection — do not reuse a command name already registered by another recipe
- [ ] `parameters` is a JSON-stringified array of parameter definitions (`name`, `label`, `type`, `control_type`, `optional`), matching `extended_output_schema`'s `parameters` object
- [ ] A date parameter uses `"type": "date_time"` with `"control_type": "date"` (not `"type": "date"`) — and its `extended_output_schema` entry includes `"parse_output": "date_conversion"` / `"render_input": "date_conversion"`
- [ ] `input.hide_from_help` is present as a string (`"true"` or `"false"`), matching production usage
- [ ] The recipe does NOT contain a `clock`/`wait_for_interval` step anywhere — confirmed to fail outright with `"Use of long actions is not allowed in WorkBot recipes"` inside a `bot_command`-triggered recipe. Use an `action_continue_flow` button instead if a pause-before-continuing is needed.

## `help_event` Trigger

- [ ] `input` is empty (`{}`) — this trigger takes no input
- [ ] Only one `help_event` recipe is intended to be active per bot at a time — flag to the user if this looks like it would create a second one
- [ ] Caller context is read from `["context", "from", "aadObjectId"]`, same path as `bot_command` — do not assume a different structure without confirming first

## `new_message_event` Trigger

- [ ] Output field paths use the confirmed real camelCase names (`messageText`, `conversationId`, `sentFromId`, etc. — see SKILL.md's Teams Datapill Paths) — NOT snake_case guesses modeled on the doc's field labels
- [ ] `attachments` is treated as an array; per-item fields are `contentType`/`contentUrl`/`name` directly, with `downloadUrl`/`uniqueId`/`fileType` nested one level deeper under `content` — do not flatten these

## `new_event` Trigger

- [ ] `input.event_name` is a real, live-search-confirmed value (currently only `application/search` is confirmed available) — never invent an `event_name` value from the doc's feature list (e.g. anything tab/task-related) without checking the picker first
- [ ] Caller identity is read from `["from", "aadObjectId"]` (top-level), NOT `["context", "from", "aadObjectId"]` — this trigger's shape differs from `bot_command`/`help_event`

## `get_user_by_principal_name` Action

- [ ] Input uses exactly one of `principal_name` (email/UPN) or `id` (Azure AD object ID) — do not include both

## `post_blocks_message` Action

- [ ] `channel` is set — this action always targets a specific channel/user, unlike `post_blocks_reply_message`
- [ ] `blocks` is an array where each entry has a `block_type` (`text_block` or `text_with_button_block`) and a matching nested object with that same key
- [ ] `text_block` entries use `"text_type": "body_text"` for standard message text, or `"text_type": "custom"` (with `"separator": "true"` and `"style": {"isSubtle": "true"}`) for a de-emphasized footer line — not a made-up `text_type` value
- [ ] `text_with_button_block` entries with `button_type: "submit"` include `bot_command` (the command this button should invoke), `open_task_module` (string `"true"`/`"false"`), and `params` (a JSON string of the parameters that command's `bot_command` trigger expects) — do NOT use `bot_command`/`params` on an `action_continue_flow` button, they don't apply
- [ ] When a `submit` button's `params` value must be computed (not a straight datapill passthrough), the field is built in full formula mode (leading `=`), not as a template string with an embedded formula expression
- [ ] `text_with_button_block` entries with `button_type: "action_continue_flow"` do NOT set `bot_command`/`params`/`open_task_module` — instead use `button_title` (mandatory), and optionally `header_text`, `button_id`, `separator`
- [ ] When any block in `blocks` uses `action_continue_flow`, the action's own top-level input also needs a `timeout` field (an integer, in MINUTES despite being a bare numeric string — confirmed via the field's own UI hint) — do not assume seconds
- [ ] Do not assume the message's own `id` output is missing just because it's absent from `extended_output_schema` once an `action_continue_flow` block is present — it was confirmed to still resolve as a valid datapill

## `post_blocks_reply_message` Action

- [ ] Do NOT set a `channel` field — this action has none; it replies to the invoking context implicitly
- [ ] Only used from a recipe with a real Workbot-command invocation context (`bot_command` or `help_event`), never from a recipe with no live Teams invocation (e.g. a clock-triggered recipe)
- [ ] Not `post_blocks_message` — verify the recipe actually needs "reply where invoked" semantics, not "post to a specific channel/user"

## `delete_message` Action

- [ ] `message_id` is sourced from a `post_blocks_message`/`post_blocks_reply_message` step's `id` output
- [ ] `conversation_id` is sourced from the triggering `bot_command`/`help_event`'s `["context", "conversation", "id"]` — activation-confirmed. Do NOT source it from `get_user_by_principal_name`'s `id` output (confirmed wrong via a live job failure — a Teams user ID is not a conversation ID)

## `post_simple_message` / `post_simple_reply` Actions

- [ ] Only used when a recipe genuinely doesn't need rich blocks/buttons — prefer `post_blocks_message`/`post_blocks_reply_message` otherwise, since they're better documented and support buttons
- [ ] `post_simple_message` requires a recipient field (same asymmetry as `post_blocks_message`); `post_simple_reply` does not (same as `post_blocks_reply_message`) — field names for these have not been fully captured yet, flag as unconfirmed if generating one

## `post_bot_message` / `post_bot_reply` Actions

- [ ] Treat these as deprecated/legacy — prefer `post_blocks_message`/`post_blocks_reply_message` unless the recipe specifically needs the `use_json` raw-JSON mode these carry and `post_blocks_message`/`post_blocks_reply_message` are confirmed not to support it

## `invoke_response` Action

- [ ] Only used to respond to a `new_event` firing in the same recipe
- [ ] `input.event_name` matches the same confirmed-available value used on the paired `new_event` trigger (currently only `application/search`)
- [ ] For `application/search`: the nested `"application/search"` object's `type` field is always the literal string `application/vnd.microsoft.search.searchResponse` (fixed/read-only in the connector's own schema) — never a different or computed value
- [ ] `value.results` is an array of `{title, value}` objects — typically sourced from a dynamic list datapill, not typed as literal values
- [ ] Flag to the user that the full live round trip (a real Adaptive Card with a dynamic search field, a real typed query, real results appearing in Teams) has not been activation-tested — only the schema is confirmed
