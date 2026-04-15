# Asana Recipes Skill - Agent Instructions

> **DEPENDENCY: Load `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, formulas, and recipe structure.

This skill provides Asana-specific knowledge for generating Workato recipes. It extends the **workato-recipes** base skill and focuses on Asana-specific patterns, including:

- **Native Asana connector** (`provider: "asana"`) — 16 native actions for common operations
- **Adhoc HTTP** for Asana REST API endpoints not covered by native actions

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects:
1. **Read existing Asana `.recipe.json` files** to understand local patterns
2. **Check the config section** for the connection name already in use

### For GREENFIELD projects:
1. **Use skill templates** — see `templates/create-task.json`, `templates/get-task.json`, `templates/search-tasks.json`
2. **Use descriptive UUIDs** — e.g., `create-task-001`, `search-tasks-002`

### ALWAYS:
1. **Ask for connection name** — exact name of Asana connection in Workato
2. **Confirm workspace/project** — which Asana workspace and project GIDs?
3. **Use API endpoint trigger** for testability via curl
4. **Use descriptive UUIDs** — never copy random hex UUIDs from existing recipes
5. **Include opt_fields parameter** — most Asana GET endpoints accept `opt_fields` to select returned fields

---

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Asana Config Requirements](#asana-config-requirements)
3. [Native Connector Guidance](#native-connector-guidance)
4. [Asana Datapill Paths](#asana-datapill-paths)
5. [Adhoc HTTP for Extended API Coverage](#adhoc-http-for-extended-api-coverage)
6. [Common Patterns](#common-patterns)
7. [Validation](#validation)
8. [Templates](#templates)
9. [References](#references)

---

## When to Use This Skill

Use this skill when building Workato recipes that:
- Create, read, update, or delete Asana resources (tasks, projects, goals, etc.)
- Search or list Asana resources with filtering
- Manage relationships between Asana resources (task→project, user→team, etc.)
- React to Asana events (task changed, project updated, etc.)
- Handle operations not covered by native actions via adhoc HTTP

**Prerequisites:**
- `workato-recipes` base skill loaded
- Workato workspace with Asana connection configured
- Understanding of target Asana workspace structure (workspace GID, project GIDs)

---

## Asana Config Requirements

Every recipe using Asana actions requires the `asana` provider in the config section:

```json
{
  "keyword": "application",
  "provider": "asana",
  "skip_validation": false,
  "account_id": {
    "zip_name": "my_asana_account.connection.json",
    "name": "My Asana account",
    "folder": ""
  }
}
```

**Combined with API endpoint trigger** (for testability via curl):

```json
"config": [
  { "keyword": "application", "provider": "workato_api_platform", "skip_validation": false, "account_id": null },
  { "keyword": "application", "provider": "asana", "skip_validation": false, "account_id": { "zip_name": "my_asana_account.connection.json", "name": "My Asana account", "folder": "" } }
]
```

**Combined with callable recipe trigger:**

```json
"config": [
  { "keyword": "application", "provider": "workato_recipe_function", "skip_validation": false, "account_id": null },
  { "keyword": "application", "provider": "asana", "skip_validation": false, "account_id": { "zip_name": "my_asana_account.connection.json", "name": "My Asana account", "folder": "" } }
]
```

---

## Native Connector Guidance

The Asana connector provides 16 native actions, 2 triggers, and `__adhoc_http_action` for everything else. See `lint-rules.json` for the authoritative list of valid action and trigger names.

### Choosing the Right Action

**Get vs Search vs List:**
- **`get_*_by_id`** actions — Use when you already have the resource GID
- **`search_*`** actions — Use when filtering by criteria (name, assignee, workspace, etc.)
- **`list_*`** actions — Use when enumerating all items in a scope (project tasks, workspace members, tagged tasks)

**Triggers:**
- **`new_event`** — Webhook trigger for Asana change events. Requires `workspace_id`. Use `dynamicPickListSelection` for workspace and action filtering. Filter with `actions` array: `changed`, `deleted`, `removed`, `added`, `undeleted`.
- **`new_or_updated_task_v2`** — Polling trigger for new or updated tasks.

**Uncovered operations:** Use `__adhoc_http_action` for any Asana REST API endpoint not in the 16 native actions (goals, portfolios, budgets, webhooks, time tracking, etc.). See [Adhoc HTTP for Extended API Coverage](#adhoc-http-for-extended-api-coverage) below.

---

## Asana Datapill Paths

Asana action outputs are accessed directly — no `["body"]` wrapper:

```json
// CORRECT
"path": ["gid"]
"path": ["name"]
"path": ["assignee", "gid"]

// WRONG — do NOT use body wrapper
"path": ["body", "gid"]
```

---

## Adhoc HTTP for Extended API Coverage

The Asana REST API covers **217 operations** across 20+ resource types (tasks, projects, goals, portfolios, teams, users, workspaces, sections, tags, webhooks, custom fields, stories, attachments, status updates, budgets, rates, allocations, time tracking, memberships, and more).

For the full operation catalog with per-resource recipes, see `patterns/api-endpoint-recipes.md`.

---

## Common Patterns

### 1. Search → Act pattern

Search for a task, then update or process it:

```
Step 1: search_tasks (find matching tasks)
Step 2: if/else (check if results found)
Step 3: update_task or create_task (act on results)
```

### 2. Event-driven pattern

React to Asana changes:

```
Trigger: new_event (workspace_id, actions: ["changed"])
Step 1: get_task_details_by_id (get full details of changed task)
Step 2: [downstream action — Slack notification, Salesforce update, etc.]
```

### 3. Adhoc HTTP for uncovered operations

For operations not in the 16 native actions (goals, portfolios, webhooks, etc.), use `__adhoc_http_action`:

```json
{
  "number": 1,
  "provider": "asana",
  "name": "__adhoc_http_action",
  "keyword": "action",
  "input": {
    "mnemonic": "GET /api/1.0/goals?workspace={workspace_gid}"
  },
  "uuid": "get-goals-001"
}
```

### 4. Asana resource GIDs

All Asana resources are identified by GID (string, not integer). Always type GID fields as `"type": "string"`:

```json
{ "name": "task_gid", "type": "string", "label": "Task GID", "optional": false }
```

### 5. Resource subtypes

Tasks can be `default_task`, `milestone`, or `approval`. Use `pick_list` for these enums:

```json
{
  "name": "resource_subtype",
  "type": "string",
  "pick_list": [["Default task", "default_task"], ["Milestone", "milestone"], ["Approval", "approval"]]
}
```

---

## Validation

See [validation-checklist.md](validation-checklist.md) for Asana-specific validation, which references the base checklist in `workato-recipes/validation-checklist.md`.

---

## Templates

See `templates/` directory:
- `create-task.json` — Create a task with full field support (assignee, due dates, custom fields, followers, projects, tags)
- `get-task.json` — Get a task by ID with opt_fields
- `search-tasks.json` — Search tasks in a workspace with filters

---

## References

- **Base Skill:** `workato-recipes` — Recipe structure, triggers, control flow, formulas
- **Templates:** `templates/` directory — 3 reference recipes (create, get, search tasks)
- **Patterns:** `patterns/` directory — API endpoint recipe pattern for full REST API coverage
- **Asana API Docs:** https://developers.asana.com/docs/asana
- **Connector actions:** See `lint-rules.json` for the authoritative list of valid action/trigger names
- **Full API coverage:** 217 reference recipes covering the complete Asana REST API surface
