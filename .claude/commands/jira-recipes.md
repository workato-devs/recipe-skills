# Jira Recipes Skill

> **DEPENDENCY: Run `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

You are now equipped with Jira-specific knowledge for writing Workato recipes. This skill extends the **workato-recipes** base skill and focuses on Jira-specific patterns.

## Capabilities

With this skill loaded, you can:
- Search Jira issues using JQL queries with dynamic filters
- Query sprint status and issue breakdowns
- Create and update Jira issues with full field support
- Get issue details by ID or key
- Manage comments, users, and attachments
- Handle operations not covered by native actions via adhoc HTTP

## Trigger Type Selection

Ask the user which trigger type they need:
- **API Endpoint** (`workato_api_platform`) - External HTTP access
- **Callable Recipe** (`workato_recipe_function`) - Internal recipe calls

See `workato-recipes` skill for trigger implementation details.

## Jira-Specific Knowledge

### Action Name Casing (CRITICAL)

**`search_issues_by_JQL` is case-sensitive.** The `JQL` portion MUST be uppercase. Using `search_issues_by_jql` or any other casing will fail with "Select an app and action" in the Workato UI.

### `jql` Is a Connector Internal (CRITICAL)

The `jql` field is Jira's native parameter. It must **NEVER** appear in `extended_input_schema`. Set `extended_input_schema: []` for search actions.

```json
// CORRECT
"input": { "jql": "='project = \"ENG\"'" },
"extended_input_schema": []

// WRONG - causes duplicate field in UI
"input": { "jql": "='project = \"ENG\"'" },
"extended_input_schema": [{ "name": "jql", "type": "string" }]
```

### Field Name: `jql` Not `query`

The native field name is `jql`, not `query`. Using `query` causes "Field not recognized."

### JQL Formula Mode (CRITICAL)

JQL values use `=` formula mode with bare `_dp()` calls. No `#{}` interpolation. No outer parentheses.

```json
"jql": "='project = \"' + _dp('{...project_key...}') + '\" AND sprint in openSprints()'"
```

### Datapill Paths (CRITICAL)

**Jira does NOT use the `["body"]` wrapper** in datapill paths:

```json
// CORRECT for Jira
"path": ["issues"]
"path": ["issues", {"path_element_type": "current_item"}, "key"]

// WRONG - Do NOT use for Jira
"path": ["body", "issues"]
```

### Array Serialization

Use `.to_json` to serialize arrays for return responses. Use `path_element_type: "size"` for counts -- NOT `.size`.

```json
"issues_json": "=_dp('{...path:[\"issues\"]}').to_json",
"total_issues": "=_dp('{...path:[\"issues\",{\"path_element_type\":\"size\"}]}')"
```

## Reference Files

- `skills/workato-recipes/SKILL.md` - Base platform knowledge
- `skills/jira-recipes/SKILL.md` - Jira-specific knowledge
- `skills/jira-recipes/templates/` - Validated recipe templates
- `skills/jira-recipes/patterns/` - JQL query syntax reference
- `skills/jira-recipes/validation-checklist.md` - Jira validation checklist

## Usage

When asked to create a Jira recipe:

1. **Ask for connection name** - exact name of Jira connection in Workato
2. **Confirm project key** - the Jira project key (e.g., `ENG`, `MOB`)
3. **Ask about trigger type** - API endpoint or callable recipe?
4. **Identify the Jira operation** - search, create, update, get
5. **Apply Jira patterns** - JQL formula mode, case-sensitive action names, no body wrapper
6. **Generate valid JSON** using base skill structure + Jira specifics

## Example Prompts

- "Create a recipe that searches Jira issues by JQL and returns sprint status"
- "Create a recipe that creates a Jira issue with project key and assignee"
- "Create a recipe that gets an issue by key and returns its details"
- "Create a recipe that searches for open bugs in a sprint and returns a summary"
