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
3. [Native Connector Guidance](#native-connector-guidance)
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

## Native Connector Guidance

The Jira connector provides 17 native actions and 11 triggers. See `lint-rules.json` for the authoritative list of valid action and trigger names.

### Choosing the Right Trigger

- **Generic webhook:** `new_event` — fires on any configured Jira event (issue created, updated, etc.).
- **Issue polling:** `new_issue`, `updated_issue` — poll for new or updated issues.
- **Batch polling:** `new_issue_batch`, `updated_issue_batch` — poll for batches of new/updated issues.
- **Bulk:** `issue_created_bulk`, `issue_created_or_updated_bulk` — for high-volume processing.
- **Specific webhooks:** `updated_comment_webhook`, `updated_issue_webhook`, `updated_worklog_webhook` — real-time triggers for specific change types.
- **Deletion:** `deleted_object` — triggers on object deletion.

### Choosing the Right Action

**Issue CRUD:**
- **`create_issue`** — Create a new issue. Key inputs: `project_key`, `issue_type`, `summary`. See [detail below](#create_issue-detail).
- **`get_issue`** — Get full issue details by ID or key. See [detail below](#get_issue-detail).
- **`update_issue`** — Update issue fields. Requires `issue_id_or_key`. See [detail below](#update_issue-detail).
- **`update_issue_status`** — Transition issue to a different workflow state.
- **`assign_issue`** — Assign an issue to a user.

**Search:**
- **`search_issues_by_JQL`** — Primary search action. Full JQL flexibility, battle-tested. **Name is case-sensitive** (uppercase `JQL`). See [detail below](#search_issues_by_jql-detail).
- **`search_issues`** — Simpler field-filter search without JQL. Less flexible.

**Comments:** `create_comment`, `update_comment`, `get_issue_comments`

**Users:** `find_user` (by query string), `search_assignable_users` (users assignable to an issue), `create_user`

**Attachments:** `upload_attachment`, `get_attachment`

**Metadata:** `get_changelog` (issue change history), `get_object_schema`

**Uncovered operations:** Use `__adhoc_http_action` for Jira operations not covered by native actions: workflow transitions, sprint/board management, project listing, custom field management, tempo/time tracking, and advanced operations.

---

### search_issues_by_JQL Detail

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
