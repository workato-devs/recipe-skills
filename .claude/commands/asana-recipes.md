# Asana Recipes Skill

> **DEPENDENCY: Run `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

You are now equipped with Asana-specific knowledge for writing Workato recipes. This skill extends the **workato-recipes** base skill and focuses on Asana-specific patterns.

## Capabilities

With this skill loaded, you can:
- Create, read, update, and delete tasks with full field support
- Search tasks in a workspace with filters
- Manage projects, portfolios, goals, and sections
- Handle team memberships and user assignments
- React to Asana events via the `new_event` webhook trigger
- Use adhoc HTTP for 200+ uncovered Asana REST API operations

## Trigger Type Selection

Ask the user which trigger type they need:
- **API Endpoint** (`workato_api_platform`) - External HTTP access
- **Callable Recipe** (`workato_recipe_function`) - Internal recipe calls
- **Asana Event** (`new_event`) - React to Asana changes (requires `dynamicPickListSelection`)

See `workato-recipes` skill for trigger implementation details.

## Asana-Specific Knowledge

### GIDs Are Strings (CRITICAL)

All Asana resource identifiers are GID strings, not integers. Always type as `"type": "string"`:

```json
{ "name": "task_gid", "type": "string", "label": "Task GID", "optional": false }
```

### Datapill Paths (CRITICAL)

**Asana does NOT use the `["body"]` wrapper** in datapill paths:

```json
// CORRECT for Asana
"path": ["gid"]
"path": ["name"]
"path": ["assignee", "gid"]

// WRONG - Do NOT use for Asana
"path": ["body", "gid"]
```

### Get vs Search vs List

Three distinct retrieval patterns:
- **`get_*_by_id`** - Use when you already have the resource GID
- **`search_*`** - Use when filtering by criteria (name, assignee, workspace)
- **`list_*`** - Use when enumerating all items in a scope (project tasks, workspace members)

### `opt_fields` Parameter

Most Asana GET endpoints accept `opt_fields` to select which fields are returned. Include this to get the specific data you need.

### Adhoc HTTP for Extended Coverage

The 16 native actions cover a fraction of Asana's 217 REST API operations. Use `__adhoc_http_action` for goals, portfolios, webhooks, time tracking, budgets, and more:

```json
{
  "provider": "asana",
  "name": "__adhoc_http_action",
  "input": {
    "mnemonic": "GET /api/1.0/goals?workspace={workspace_gid}"
  }
}
```

### Resource Subtypes

Tasks can be `default_task`, `milestone`, or `approval`. Use `pick_list` for these enums.

## Reference Files

- `skills/workato-recipes/SKILL.md` - Base platform knowledge
- `skills/asana-recipes/SKILL.md` - Asana-specific knowledge
- `skills/asana-recipes/templates/` - Validated recipe templates (create, get, search tasks)
- `skills/asana-recipes/patterns/` - API endpoint recipe patterns
- `skills/asana-recipes/validation-checklist.md` - Asana validation checklist

## Usage

When asked to create an Asana recipe:

1. **Ask for connection name** - exact name of Asana connection in Workato
2. **Confirm workspace/project** - which Asana workspace and project GIDs?
3. **Ask about trigger type** - API endpoint, callable recipe, or Asana event?
4. **Identify the operation** - create, get, search, list, update, or adhoc HTTP?
5. **Apply Asana patterns** - GIDs as strings, no body wrapper, opt_fields
6. **Generate valid JSON** using base skill structure + Asana specifics

## Example Prompts

- "Create a recipe that creates an Asana task with subtasks and due dates"
- "Create a recipe that searches for tasks by assignee in a workspace"
- "Create a recipe that gets a task by GID and returns its details"
- "Create a recipe that lists all tasks in a project with custom field values"
