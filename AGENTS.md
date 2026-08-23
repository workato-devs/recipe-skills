# AGENTS.md — Recipe Skills

This repository is an **open knowledge library for agent-assisted Workato recipe development**, part of [Workato Labs](https://workato-devs.github.io/labs/). It does not contain an application to run. It contains **skills**: bundles of documentation, validated templates, audited lint rules, and patterns that teach an AI agent how to generate valid Workato recipe JSON for a specific connector.

If you are an agent reading this file, your job is to **load the right skills before generating recipes** — not to run a build.

## How to use this library

Skills live under `skills/<connector>-recipes/`. Each skill's entry point is its `SKILL.md`.

**Load order is mandatory:**

1. **Always load the base skill first:** `skills/workato-recipes/SKILL.md`
   It covers recipe JSON structure, trigger types, control flow, datapill syntax, and formulas. Every connector skill `extends` it (see each `skill.yaml`), so connector instructions assume this base is already in context.
2. **Then load the connector skill(s)** relevant to the user's request, from the table below.
3. Within a skill, follow its references to `templates/`, `patterns/`, `lint-rules.json`, and `validation-checklist.md` as needed.

Do **not** enumerate or guess action/trigger names from this file. Each skill's `lint-rules.json` is the audited source of truth for valid action and trigger names; the `SKILL.md` covers when and how to use them.

## Routing table

Match the user's request to a connector and load that skill (after the base skill).

| If the user wants to work with… | Load this skill |
|---|---|
| Recipe fundamentals only (triggers, control flow, datapills, formulas, API endpoints) | `skills/workato-recipes/SKILL.md` (base — always) |
| Salesforce (records, SObjects, upsert, SOQL) | `skills/salesforce-recipes/SKILL.md` |
| Slack or Workbot (slash commands, dialogs, messages) | `skills/slack-recipes/SKILL.md` |
| Stripe (customers, payments, refunds) | `skills/stripe-recipes/SKILL.md` |
| Gmail (send, search, labels, messages) | `skills/gmail-recipes/SKILL.md` |
| Jira (issues, JQL, sprints) | `skills/jira-recipes/SKILL.md` |
| Asana (tasks, projects, portfolios, goals) | `skills/asana-recipes/SKILL.md` |
| Workato Data Tables (CRUD, search, batch, the `workato_db_table` connector) | `skills/datatable-recipes/SKILL.md` |
| Generic connection-bound REST requests (the `rest` connector) | `skills/rest-recipes/SKILL.md` |

For an API operation a native SaaS connector does not cover, many connectors support `__adhoc_http_action` — see the base skill's `patterns/adhoc-http-actions.md`. The generic `rest` provider uses its own audited request action; follow `rest-recipes` instead of substituting the native-connector action name.

## After generating a recipe

Generated recipes are standard Workato recipe JSON. Before handing them off, work through the skill's `validation-checklist.md`. Recipes are pushed to a workspace with `wk push` (the `wk` CLI; see `docs/cli-guidance.md`), but **only run push commands when the user explicitly asks** — generating valid JSON is the default deliverable.

## Contributing to this library

If the user's goal is to **add or improve a skill** (rather than generate a recipe), start with [`CONTRIBUTING.md`](CONTRIBUTING.md). The essentials:

- A connector skill is a directory under `skills/` with `skill.yaml`, `SKILL.md`, `lint-rules.json`, `validation-checklist.md`, plus `templates/` and `patterns/`. `CONTRIBUTING.md` → "Creating a New Connector Skill" walks the full file set.
- The core architecture rule: **`lint-rules.json` owns the "what" (valid action/trigger names, audited against the real connector); `SKILL.md` owns the "how" (decision logic).** Don't duplicate names across them.
- Improving an existing skill, the boundary between base and connector skills, and the anti-patterns are covered under `CONTRIBUTING.md` → "Skill Architecture" and "Contributing to Existing Skills".

## Notes for tool-specific integrations

This file is the portable, tool-neutral entrypoint — any `AGENTS.md`-aware agent (Codex, Cursor, Windsurf, and others) can open the folder and route from here. Tool-specific conveniences layer **on top** of it and are optional:

- **Claude Code** users get bundled slash commands (`/workato-recipes`, `/salesforce-recipes`, …) in `.claude/commands/`. These are a convenience wrapper over the same skills described above — not a separate or required path.

---

_Workato Labs — experimental, community feedback welcome, no SLA. See the [guiding principles](https://workato-devs.github.io/labs/principles.html)._
