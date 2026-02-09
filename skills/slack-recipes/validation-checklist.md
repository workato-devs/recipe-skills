# Slack Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

The following checks are specific to Slack connector recipes.

---

## Workbot for Slack (`slack_bot`)

### Config & Connection

- [ ] `slack_bot` provider in config section
- [ ] Connection name matches your Workbot connection

### Trigger Configuration

- [ ] Slash command name is unique in workspace (not a reserved name like `/feedback`, `/remind`, `/help`)
- [ ] Domain/scope names are unique (not reserved words like `feedback`, `help`, `support`)
- [ ] `toggleCfg` included with appropriate true/false values
- [ ] Input attributes in correct order: `allow_dialog`, `slash_command`, `scope`, `description`, `dialog_title`, `parameters`, `hide_from_help`, `name`, `domain`
- [ ] `dynamicPickListSelection` present with `{ "domain": "Slack" }`

### Dialog Parameters

- [ ] Dialog select parameters have ALL required fields: `type` (`"array"`), `prompt` (`"true"`), `dialog_data_source` (`"custom"`), `options`, `properties` (`[]`), `pick_list`
- [ ] `trigger_id` passed when opening dialogs via `open_bot_dialog`

### Actions & Datapills

- [ ] Button `bot_command` references point to valid recipes with `zip_name`
- [ ] Channel names sanitized for Slack requirements (lowercase, alphanumeric, hyphens, max 80 chars)
- [ ] Datapill paths for trigger context use `["context", ...]` or `["parameters", ...]` — no `["body"]` wrapper
- [ ] Select parameter datapills use simple paths like `["parameters", "field"]` — no `current_index` or array iteration
- [ ] Correct message action chosen: `post_bot_reply_v2` for replies to triggering user, `post_bot_message` for specific channels/DMs

---

## Native Slack (`slack`)

### Config & Connection

- [ ] `slack` provider in config section
- [ ] Connection name matches your Slack connection

### Datapills & IDs

- [ ] Native action datapill paths don't include `["body"]` wrapper
- [ ] Adhoc HTTP datapill paths DO include `["body"]` wrapper
- [ ] Channel IDs use correct format (C... for public, G... for private)
- [ ] User IDs use correct format (U...)
