# Slack Recipes Skill

> **DEPENDENCY: Run `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

You are now equipped with Slack-specific knowledge for writing Workato recipes. This skill covers **two Slack connectors**:

| Connector | Provider | Use Case |
|-----------|----------|----------|
| **Workbot for Slack** | `slack_bot` | Interactive bots, slash commands, dialogs, buttons |
| **Slack (native)** | `slack` | Programmatic actions via API-triggered recipes |

## Capabilities

With this skill loaded, you can:
- Create recipes with Workbot command triggers and slash commands
- Create recipes that post messages to channels and DMs
- Create recipes with interactive dialogs/modals
- Create recipes with button interactions
- Create recipes that chain to other Workbot recipes
- Create callable recipes using native Slack actions
- Look up users by email, create channels, manage membership

## Choosing a Connector

**Use Workbot (`slack_bot`)** when the trigger is a user interaction (slash command, button click).

**Use Native Slack (`slack`)** when the trigger is an API call, scheduler, or another system.

## Slack-Specific Knowledge

### Provider

Always use `slack_bot` (Workbot for Slack), not `slack`:

```json
"provider": "slack_bot"
```

### Datapill Paths (CRITICAL)

**Slack does NOT use the `["body"]` wrapper** for trigger context:

```json
// CORRECT for Slack trigger context
"path": ["context", "user"]
"path": ["context", "channel"]
"path": ["context", "trigger_id"]
"path": ["parameters", "project_name"]

// For adhoc HTTP responses, body IS used
"path": ["body", "channel", "id"]
```

### Dialog Parameters

Parameters are defined as a JSON string with control types:
- `text` - Single-line input (150 char max)
- `text-area` - Multi-line input (3000 char max)
- `select` - Dropdown with `pick_list` options

### Sending DMs

Target the triggering user's DM:
```json
"channel": "=_dp('{...path:[\"context\",\"user\"]}').gsub('\"','')"
```

### Channel Name Sanitization

Slack channel names must be lowercase, alphanumeric with hyphens:
```json
".downcase.gsub(/[^a-z0-9]/, '-').gsub(/-+/, '-').gsub(/^-|-$/, '')[0..79]"
```

## Reference Files

- `skills/workato-recipes/SKILL_INSTRUCTIONS.md` - Base platform knowledge
- `skills/slack-recipes/SKILL_INSTRUCTIONS.md` - Slack-specific knowledge
- `skills/slack-recipes/patterns/` - Pattern documentation
- `skills/slack-recipes/templates/` - Validated recipe templates

## Usage

### Before Generating Recipes

**CRITICAL: Always ask the user for these details first:**

1. **Workbot connection name** - What is the exact name of their Workbot for Slack connection?
   - Example: "My Workbot for Slack account", "Production Workbot"
   - This will be used in the `account_id.name` field

2. **Slash command name** - What slash command should trigger this? (e.g., `/helpdesk`)

3. **Dialog requirements** - What information needs to be collected from users?

### Recipe Generation Steps

1. **Ask for connection name** (REQUIRED)
2. **Ask about slash command** - Name and initial reply message
3. **Identify dialog parameters** - What fields to collect?
4. **Determine actions** - Post messages, create channels, chain recipes?
5. **Generate valid JSON** using base skill structure + Slack specifics

## Example Prompts

- "Create a slash command recipe that collects a support ticket and posts to #support"
- "Create a recipe that creates a project channel and invites the user"
- "Create a recipe with buttons to approve or reject a request"
