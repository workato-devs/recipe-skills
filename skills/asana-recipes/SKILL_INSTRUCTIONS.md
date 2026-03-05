# Asana Recipes Skill - Agent Instructions

> **DEPENDENCY: Load `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, formulas, and recipe structure.

This skill provides Asana-specific knowledge for generating Workato recipes. It extends the **workato-recipes** base skill and focuses on Asana-specific patterns, including:

- **Native Asana connector** (`provider: "asana"`) — 18 built-in actions for common operations
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
3. [Native Asana Connector Actions](#native-asana-connector-actions)
4. [Asana Datapill Paths](#asana-datapill-paths)
5. [Asana API Resources (Full Coverage)](#asana-api-resources-full-coverage)
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

## Native Asana Connector Actions

The Workato Asana connector (`provider: "asana"`) provides 18 built-in actions.

### Trigger

| Name | Description | Key Inputs |
|------|-------------|------------|
| `new_event` | Webhook trigger for Asana events | `workspace_id` (required), `project_id`, `team_id`, `actions` (changed/deleted/removed/added/undeleted) |

The trigger uses `dynamicPickListSelection` for workspace and action filtering.

### CRUD Actions

| Name | Description |
|------|-------------|
| `create_task` | Create a new task |
| `create_subtask` | Create a subtask under a parent task |
| `create_tag` | Create a new tag |
| `update_task` | Update an existing task |
| `get_task_details_by_id` | Get full task details |
| `get_people_details_by_id` | Get user details |
| `get_project_detail_by_id` | Get project details |
| `get_project_sections` | Get sections in a project |

### Search & List Actions

| Name | Description | Key Inputs |
|------|-------------|------------|
| `search_tasks` | Search tasks with filters | |
| `search_projects` | Search projects | |
| `search_tags` | Search tags | |
| `list_project_tasks` | List tasks in a project | `ProjectID`, `limit` |
| `list_all_tasks_with_tag` | List tasks with a specific tag | |
| `list_people` | List workspace members | |
| `list_workspaces` | List accessible workspaces | |

### Relationship Actions

| Name | Description |
|------|-------------|
| `add_task_to_section` | Move/add a task to a section |

### Raw HTTP

| Name | Description |
|------|-------------|
| `__adhoc_http_action` | Direct HTTP call to any Asana API endpoint not covered by native actions |

Use `__adhoc_http_action` for Asana REST API operations not covered by the 17 native actions above (e.g., goals, portfolios, budgets, webhooks, time tracking). See the Asana API resource reference below for the full operation catalog.

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

## Asana API Resources (Full Coverage)

The templates directory includes reference recipes from the full Asana REST API covering **217 operations** across the following resources:

### Tasks (52 recipes) — Primary resource
| Operation | Recipe |
|-----------|--------|
| Create | `create_a_task`, `create_a_subtask` |
| Get | `get_a_task`, `get_multiple_tasks` |
| Update | `update_a_task` |
| Delete | `delete_a_task` |
| Duplicate | `duplicate_a_task` |
| Search | `search_tasks_in_a_workspace` |
| List | `get_tasks_from_a_project`, `get_tasks_from_a_section`, `get_tasks_from_a_tag`, `get_tasks_from_a_user_task_list` |
| Subtasks | `get_subtasks_from_a_task`, `set_the_parent_of_a_task` |
| Dependencies | `get_dependencies_from_a_task`, `set_dependencies_for_a_task`, `unlink_dependencies_from_a_task` |
| Dependents | `get_dependents_from_a_task`, `set_dependents_for_a_task`, `unlink_dependents_from_a_task` |
| Tags | `add_a_tag_to_a_task`, `remove_a_tag_from_a_task`, `get_a_task_s_tags` |
| Projects | `add_a_project_to_a_task`, `remove_a_project_from_a_task`, `get_projects_a_task_is_in` |
| Followers | `add_followers_to_a_task`, `remove_followers_from_a_task` |
| Custom ID | `get_a_task_for_a_given_custom_id` |

### Projects (35 recipes)
CRUD, duplicate, task counts, custom fields, members, followers, template instantiation, workspace/team scoped creation.

### Goals (18 recipes)
CRUD, metrics, relationships (supporting goals), collaborators, custom fields, parent goals.

### Portfolios (16 recipes)
CRUD, items, custom fields, memberships, users.

### Teams (12 recipes)
CRUD, memberships (team and user scoped), add/remove users.

### Users (12 recipes)
Get, update, list (workspace/team scoped), favorites, task lists.

### Workspaces (8 recipes)
Get, update, list, memberships, add/remove users, events.

### Sections (7 recipes)
CRUD, list in project, add task, move/insert.

### Tags (7 recipes)
CRUD, list (workspace scoped).

### Webhooks (5 recipes)
CRUD, list.

### Custom Fields (7 recipes)
CRUD, enum options (create, update, reorder), list by project/portfolio/goal/team/workspace.

### Stories (5 recipes)
CRUD, list from task.

### Attachments (4 recipes)
Get, delete, list from object, upload.

### Status Updates (4 recipes)
CRUD, list from object.

### Budgets & Rates (10 recipes)
Full CRUD for both.

### Allocations (5 recipes)
Full CRUD.

### Time Tracking (7 recipes)
CRUD, list entries per task and globally.

### Memberships (5 recipes)
CRUD for generic memberships, plus specialized portfolio/project/team/workspace memberships.

### Other (17 recipes)
Access requests, audit logs, events, exports, jobs, typeahead, parallel requests, rules, time periods, reactions.

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

For operations not in the 17 native actions (goals, portfolios, webhooks, etc.), use `__adhoc_http_action`:

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
- **Connector actions:** 18 native actions (see [Native Asana Connector Actions](#native-asana-connector-actions))
- **Full API coverage:** 217 reference recipes covering the complete Asana REST API surface
