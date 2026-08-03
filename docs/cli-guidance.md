# wk CLI + Recipe Lint Setup

One-time setup for the `wk` CLI and the `recipe-lint` plugin. For how to actually use them day-to-day (lint tiers, rule reference, provider names, `wk push`/`lint`/`export` commands), see the loaded skill: [`workato-recipes/fundamentals/cli-workflow.md`](../skills/workato-recipes/fundamentals/cli-workflow.md) — that content lives there, not here, so it's loaded automatically for any agent using this plugin rather than requiring a human to point them at a docs file.

---

## Setup

### Install the wk CLI

```bash
go install github.com/workato-devs/wk-cli-beta/cmd/wk@latest
```

### Install the Recipe Lint Plugin

```bash
wk plugins install github.com/workato-devs/wk-lint-beta@latest
```

### Clone Recipe Skills

```bash
git clone https://github.com/workato/recipe-skills.git
```

This registers two capabilities:
- **`wk lint`** command — run the linter on-demand
- **`pre-push` hook** — automatically lint `.recipe.json` files before `wk push`

### No Other Configuration Required

Once the plugin is installed and you have a local clone of recipe-skills, you're ready to develop. There is no per-project setup, environment variable, or config file required to get started.

---

## How the Linter Uses Recipe Skills

When you pass `--skills-path`, the linter walks the directory tree for `lint-rules.json` files. Each file declares a connector name and its valid actions:

```json
{
  "connector": "salesforce",
  "valid_action_names": ["upsert_sobject", "search_sobjects", "..."],
  "connector_internals": ["sobject_name", "limit"]
}
```

Used for three rules: `ACTION_NAME_VALID` (rejects unlisted action names), `CONFIG_PROVIDER_MATCH` (skips providers listed in `connector_internals`), `EIS_NO_CONNECTOR_INTERNAL` (flags connector-internal fields in `extended_input_schema`). The linter does not read `SKILL.md`, templates, or patterns — only `lint-rules.json`.
