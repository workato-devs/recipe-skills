# Jira Recipes Skill - Agent Instructions

> **⚠️ DEPENDENCY: Load `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, formulas, and recipe structure.

This skill provides Jira-specific knowledge for generating Workato recipes. It extends the **workato-recipes** base skill and focuses on Jira-specific patterns.

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects:
1. **Read existing Jira `.recipe.json` files** to understand local patterns

### For GREENFIELD projects:
1. **Use skill templates** - see `templates/search-issues-by-jql.json` as reference
2. **Use descriptive UUIDs** - e.g., `jira-search-sprint-003`, `return-success-jira-004`

### ALWAYS:
1. **Ask for connection name** - exact name of Jira connection in Workato
2. **Confirm project key** - the Jira project key (e.g., `ENG`, `MOB`, `PROJ`)
3. **Use API endpoint trigger** for testability via curl
4. **Use descriptive UUIDs** - never copy random hex UUIDs from existing recipes
5. **Remember action name casing** - `search_issues_by_JQL` is case-sensitive (uppercase `JQL`)

---

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Jira Config Requirements](#jira-config-requirements)
3. [Native Jira Connector Actions](#native-jira-connector-actions)
4. [JQL Query Syntax](#jql-query-syntax)
5. [Jira Datapill Paths](#jira-datapill-paths)
6. [Jira Patterns](#jira-patterns)
7. [Extended Input Schema Rules](#extended-input-schema-rules)
8. [Common Errors](#common-errors)
9. [Validation](#validation)

---

## When to Use This Skill

Use this skill when building Workato recipes that:
- Search Jira issues using JQL queries
- Query sprint status and issue breakdowns
- Create or update Jira issues
- Retrieve issue details by ID or key

**Prerequisites:**
- `workato-recipes` base skill loaded
- Workato workspace with Jira connection configured
- Understanding of the target Jira project structure (project keys, sprint names)

---

## Jira Config Requirements

Every Jira recipe requires the `jira` provider in the config section:

```json
{
  "keyword": "application",
  "provider": "jira",
  "skip_validation": false,
  "account_id": {
    "zip_name": "connectors/jira.connection.json",
    "name": "My Jira Connection",
    "folder": "connectors"
  }
}
```

**Combined with API endpoint trigger:**

```json
"config": [
  {
    "keyword": "application",
    "provider": "workato_api_platform",
    "skip_validation": false,
    "account_id": null
  },
  {
    "keyword": "application",
    "provider": "jira",
    "skip_validation": false,
    "account_id": {
      "zip_name": "connectors/jira.connection.json",
      "name": "My Jira Connection",
      "folder": "connectors"
    }
  }
]
```

---

## Native Jira Connector Actions

The Workato Jira connector (`provider: "jira"`) provides **34 agent-usable actions** and **3 triggers**. Only `search_issues_by_JQL` has been fully tested via CLI push — other actions are available in the connector but should be verified against the Workato UI before production use.

> Actions marked with **(tested)** have been validated via CLI push. All others exist in the connector but have not been CLI-push verified.

### Triggers

| Name | Description |
|------|-------------|
| `new_event` | Webhook trigger for Jira events (issue created, updated, etc.) |
| `deleted_object` | Trigger when a Jira object is deleted |
| `new_project` | Trigger when a new project is created |

### Issues

| Name | Description | Notes |
|------|-------------|-------|
| `create_issue` | Create a new issue | Key inputs: `project_key`, `issue_type`, `summary` |
| `get_issue` | Get full issue details by ID or key | Use this for single-issue lookups |
| `update_issue` | Update an existing issue | Requires `issue_id_or_key` |
| `assign_issue` | Assign an issue to a user | |
| `update_issue_status` | Transition issue to a different workflow state | Use `get_transition_status` first to get valid transitions |

### Search

| Name | Description | Notes |
|------|-------------|-------|
| `search_issues_by_JQL` | Search issues using JQL query **(tested)** | **Primary search action.** Case-sensitive name (uppercase `JQL`). See [detail below](#search_issues_by_jql-detail) |
| `search_issues` | Search issues with field filters | Simpler than JQL but less flexible |
| `get_issues_v3_jql` | JQL search via v3 API | Alternative to `search_issues_by_JQL` |
| `get_issues_v3_jql_count` | Count issues matching a JQL query | Returns count only, no issue data |
| `get_issues_v3_jql_paginated` | Paginated JQL search (v3 API) | For large result sets |
| `get_paginated_issues` | Paginated issue retrieval | |

> **Routing note:** Use `search_issues_by_JQL` for most search scenarios — it is the only tested action and supports full JQL flexibility. Use the `v3_jql` variants only if you specifically need v3 API features or pagination.

### Comments

| Name | Description |
|------|-------------|
| `create_comment` | Add a comment to an issue |
| `update_comment` | Update an existing comment |
| `get_comment` | Get a single comment by ID |
| `get_issue_comments` | Get all comments on an issue |

### Users

| Name | Description |
|------|-------------|
| `find_user` | Find a user by query string |
| `search_assignable_users` | Search for users assignable to a specific issue |
| `search_single_user_by_email` | Find a user by email address |
| `get_current_user` | Get the authenticated user's details |
| `get_assignees` | Get users assignable to a project |
| `create_user` | Create a new Jira user |

### Attachments

| Name | Description |
|------|-------------|
| `upload_attachment` | Upload an attachment to an issue |
| `get_attachment` | Get attachment metadata |

### Projects

| Name | Description |
|------|-------------|
| `get_all_projects` | List all accessible projects |
| `get_paginated_projects` | List projects with pagination |

### Webhooks

| Name | Description |
|------|-------------|
| `create_webhook` | Register a new webhook |
| `delete_webhook` | Delete an existing webhook |

### Reference Data

| Name | Description |
|------|-------------|
| `get_changelog` | Get change history for an issue |
| `get_transition_status` | Get available workflow transitions for an issue |
| `get_priorities` | List all available priorities |
| `get_statuses` | List all workflow statuses |
| `get_status` | Get a specific status by ID |
| `get_all_resolutions` | List all issue resolutions |

### Raw HTTP

| Name | Description |
|------|-------------|
| `__adhoc_http_action` | Direct HTTP call to any Jira REST API endpoint |

Use `__adhoc_http_action` for Jira operations not covered by the 34 native actions above: custom field management, sprint operations, board management, tempo/time tracking, and advanced workflow operations.

---

### search_issues_by_JQL Detail

**(Tested, Production-Proven)**

**Use when:** Finding issues using JQL queries — sprints, filters, project scoping.

**CRITICAL: The action name is case-sensitive. It MUST be `search_issues_by_JQL` (uppercase `JQL`).**

```json
{
  "provider": "jira",
  "name": "search_issues_by_JQL",
  "as": "jira_search",
  "keyword": "action",
  "input": {
    "jql": "='project = \"' + _dp('{...project_key...}') + '\" AND sprint in openSprints()'"
  },
  "extended_input_schema": [],
  "extended_output_schema": [
    {
      "label": "Issues",
      "name": "issues",
      "type": "array",
      "of": "object",
      "properties": [
        { "control_type": "text", "label": "Key", "name": "key", "type": "string" },
        { "control_type": "text", "label": "Summary", "name": "summary", "type": "string" },
        { "control_type": "text", "label": "Status", "name": "status", "type": "string" },
        { "control_type": "text", "label": "Assignee", "name": "assignee", "type": "string" },
        { "control_type": "number", "label": "Story Points", "name": "story_points", "type": "number" }
      ]
    }
  ]
}
```

**Key rules:**
- `jql` is the native field name (NOT `query`) — maps to "JQL query string" in the Workato UI
- `extended_input_schema` MUST be `[]` — `jql` is a connector internal; including it in EIS creates a duplicate field
- JQL string is built using `=` formula mode (bare `_dp()`, no `#{}` wrapper)
- `extended_output_schema` defines the issue fields you want to access via datapills

### create_issue Detail

> **WARNING:** Not yet tested via CLI push. Verify field names by pulling from the UI before production use.

```json
{
  "provider": "jira",
  "name": "create_issue",
  "as": "create_jira_issue",
  "keyword": "action",
  "input": {
    "project_key": "ENG",
    "issue_type": "Story",
    "summary": "#{summary_datapill}",
    "description": "#{description_datapill}"
  }
}
```

**Expected fields:** `project_key`, `issue_type`, `summary`, `description`, `priority`, `assignee`, `labels`

### update_issue Detail

> **WARNING:** Not yet tested via CLI push. Verify field names by pulling from the UI.

```json
{
  "provider": "jira",
  "name": "update_issue",
  "as": "update_jira_issue",
  "keyword": "action",
  "input": {
    "issue_id_or_key": "ENG-123",
    "summary": "#{summary_datapill}"
  }
}
```

### get_issue Detail

> **WARNING:** Not yet tested via CLI push. Verify field names by pulling from the UI.

```json
{
  "provider": "jira",
  "name": "get_issue",
  "as": "get_jira_issue",
  "keyword": "action",
  "input": {
    "issue_id_or_key": "ENG-123"
  }
}
```

---

## JQL Query Syntax

JQL queries in Workato are built using `=` formula mode. This means bare `_dp()` calls — no `#{}` interpolation.

### Dynamic JQL Construction

The `jql` input field uses formula mode (`=` prefix) to concatenate strings and datapills:

```json
"jql": "='project = \"' + _dp('{...project_key...}') + '\" AND sprint in openSprints()'"
```

**Breaking this down:**
- `=` — enters formula mode
- `'project = \"'` — literal string with escaped double quotes for JQL values
- `+ _dp('{...}') +` — concatenates the datapill value
- `'\" AND sprint in openSprints()'` — more literal JQL

### Conditional Clauses with `.present?`

Use the ternary pattern to add optional clauses:

```json
"jql": "='project = \"' + _dp('{...project_key...}') + '\"' + (_dp('{...sprint_name...}').present? ? ' AND sprint = \"' + _dp('{...sprint_name...}') + '\"' : ' AND sprint in openSprints()')"
```

This pattern:
- Checks if `sprint_name` was provided
- If yes: filters by the specific sprint name
- If no: defaults to all open sprints

**IMPORTANT:** No outer `()` wrapping the entire formula. The `=` is followed directly by the expression. Wrapping breaks condition LHS parsing in child actions.

See: [patterns/jql-query-syntax.md](patterns/jql-query-syntax.md) for complete reference.

---

## Jira Datapill Paths

### No Body Wrapper

**Jira actions do NOT use the `["body"]` wrapper in datapill paths.** This is consistent with other native connectors (Salesforce, Stripe).

```json
// CORRECT for Jira
"path": ["issues"]
"path": ["issues", {"path_element_type": "current_item"}, "key"]

// WRONG for Jira — Do NOT use
"path": ["body", "issues"]
```

### Jira Datapill Examples

**Issues array (for `.to_json` serialization):**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"jira\",\"line\":\"jira_search\",\"path\":[\"issues\"]}')}"
```

**Issue count (using `path_element_type: "size"`):**
```json
"=_dp('{\"pill_type\":\"output\",\"provider\":\"jira\",\"line\":\"jira_search\",\"path\":[\"issues\",{\"path_element_type\":\"size\"}]}')"
```

**Issues array as JSON string (for return_response):**
```json
"=_dp('{\"pill_type\":\"output\",\"provider\":\"jira\",\"line\":\"jira_search\",\"path\":[\"issues\"]}').to_json"
```

**Individual issue field (inside foreach):**
```json
"path": ["issues", {"path_element_type": "current_item"}, "key"]
"path": ["issues", {"path_element_type": "current_item"}, "summary"]
"path": ["issues", {"path_element_type": "current_item"}, "status"]
```

---

## Jira Patterns

### 1. Search + Serialize Pattern

Search for issues and return as JSON string with count:

```json
// Step: Jira search
{
  "provider": "jira",
  "name": "search_issues_by_JQL",
  "as": "jira_search",
  "input": {
    "jql": "='project = \"ENG\" AND sprint in openSprints()'"
  },
  "extended_input_schema": [],
  "extended_output_schema": [...]
}

// Step: Return response
{
  "provider": "workato_api_platform",
  "name": "return_response",
  "input": {
    "http_status_code": "200",
    "response": {
      "issues_json": "=_dp('{...path:[\"issues\"]}').to_json",
      "total_issues": "=_dp('{...path:[\"issues\",{\"path_element_type\":\"size\"}]}')"
    }
  }
}
```

**Key:** Use `.to_json` to serialize the issues array into a string for return. Use `path_element_type: "size"` for the count — NOT `.size` formula method.

### 2. Input Validation Pattern

Always validate required inputs before making Jira API calls:

```json
{
  "keyword": "if",
  "input": {
    "conditions": [{
      "operand": "present",
      "lhs": "#{_dp('{...path:[\"request\",\"project_key\"]}')}",
      "uuid": "cond-project-key-001"
    }]
  },
  "block": [
    // Jira search goes here
  ]
}
```

### 3. Try/Catch for Jira Errors

Wrap Jira actions in try/catch to handle API failures:

```json
{
  "keyword": "try",
  "block": [
    // Jira actions...
  ]
},
{
  "keyword": "catch",
  "provider": null,
  "as": "catch_jira_error",
  "input": { "max_retry_count": "0", "retry_interval": "2" },
  "block": [
    {
      "provider": "workato_api_platform",
      "name": "return_response",
      "input": {
        "http_status_code": "500",
        "response": {
          "error_message": "#{_dp('{\"pill_type\":\"output\",\"provider\":\"catch\",\"line\":\"catch_jira_error\",\"path\":[\"message\"]}')}"
        }
      }
    }
  ]
}
```

**Key:** Catch datapills use `"provider":"catch"` — NOT `"provider":null`.

---

## Extended Input Schema Rules

### CRITICAL: `jql` Is a Connector Internal

The `jql` field is Jira's native parameter for the `search_issues_by_JQL` action. It must **NEVER** appear in `extended_input_schema`.

**Correct:**
```json
{
  "input": {
    "jql": "='project = \"ENG\"'"
  },
  "extended_input_schema": []
}
```

**Wrong — causes duplicate field in UI:**
```json
{
  "input": {
    "jql": "='project = \"ENG\"'"
  },
  "extended_input_schema": [
    { "name": "jql", "type": "string", ... }
  ]
}
```

### General Rule

Empty `extended_input_schema: []` is correct for `search_issues_by_JQL` because the only input (`jql`) is a connector internal. If future actions require user-facing fields that are NOT connector internals, those would go in EIS — but for search, `[]` is the right answer.

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Select an app and action" in UI | Action name is wrong or case-incorrect | Use exactly `search_issues_by_JQL` (uppercase `JQL`) |
| Duplicate JQL field in UI | `jql` included in `extended_input_schema` | Remove `jql` from EIS; set `extended_input_schema: []` |
| "Field not recognized" | Using `query` instead of `jql` | The native field name is `jql`, not `query` |
| JQL parse error | Missing double quotes around values in JQL string | Use `\"value\"` inside formula mode strings |
| Empty results | JQL formula not in `=` mode | Prefix JQL value with `=` for formula mode |
| Datapill not found | `["body"]` wrapper in path | Jira is a native connector — no `["body"]` wrapper |

---

## Validation

See [validation-checklist.md](validation-checklist.md) for Jira-specific validation, which references the base checklist in `workato-recipes/validation-checklist.md`.

---

## Templates

See `templates/` directory:
- `search-issues-by-jql.json` - Search issues by JQL with conditional sprint filter, try/catch, multi-status responses

---

## References

- **Base Skill:** `workato-recipes` - Recipe structure, triggers, control flow, formulas
- **Templates:** `templates/` directory
- **Patterns:** `patterns/` directory
- **Jira Cloud REST API:** https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **JQL Reference:** https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/
