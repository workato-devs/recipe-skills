# JQL Query Syntax in Workato Recipes

This pattern documents how to build dynamic JQL (Jira Query Language) strings in Workato recipe JSON using formula mode.

---

## Formula Mode Basics

JQL strings in Workato use `=` formula mode. This means:
- The value is prefixed with `=`
- Datapills are bare `_dp()` calls (NOT `#{_dp()}`)
- String concatenation uses `+`
- Literal strings are wrapped in single quotes `'...'`
- JQL values are wrapped in escaped double quotes `\"...\"`

---

## Simple Static JQL

```json
"jql": "='project = \"ENG\" AND sprint in openSprints()'"
```

---

## Dynamic JQL with Datapills

### Single parameter:

```json
"jql": "='project = \"' + _dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"api_trigger\",\"path\":[\"request\",\"project_key\"]}') + '\" AND sprint in openSprints()'"
```

### Multiple parameters:

```json
"jql": "='project = \"' + _dp('{...project_key...}') + '\" AND assignee = \"' + _dp('{...assignee...}') + '\"'"
```

---

## Conditional Clauses with `.present?`

Use the ternary pattern to add optional filter clauses:

```json
"jql": "='project = \"' + _dp('{...project_key...}') + '\"' + (_dp('{...sprint_name...}').present? ? ' AND sprint = \"' + _dp('{...sprint_name...}') + '\"' : ' AND sprint in openSprints()')"
```

**Pattern breakdown:**
```
= '<base_query>'
  + (optional_param.present?
      ? ' AND field = "' + optional_param + '"'
      : ' AND default_clause')
```

**Multiple optional clauses:**
```json
"jql": "='project = \"' + _dp('{...project_key...}') + '\"' + (_dp('{...sprint_name...}').present? ? ' AND sprint = \"' + _dp('{...sprint_name...}') + '\"' : ' AND sprint in openSprints()') + (_dp('{...assignee...}').present? ? ' AND assignee = \"' + _dp('{...assignee...}') + '\"' : '')"
```

---

## Common JQL Operators

| Operator | JQL Syntax | Example |
|----------|-----------|---------|
| Equals | `=` | `project = "ENG"` |
| Not equals | `!=` | `status != "Done"` |
| IN | `IN` | `status IN ("To Do", "In Progress")` |
| NOT IN | `NOT IN` | `status NOT IN ("Done", "Cancelled")` |
| Contains | `~` | `summary ~ "login"` |
| Is empty | `IS EMPTY` | `assignee IS EMPTY` |
| Is not empty | `IS NOT EMPTY` | `fixVersion IS NOT EMPTY` |
| Order by | `ORDER BY` | `ORDER BY created DESC` |

---

## Sprint Functions

JQL provides built-in functions for sprint queries:

| Function | Description | Example |
|----------|-------------|---------|
| `openSprints()` | All currently active sprints | `sprint in openSprints()` |
| `closedSprints()` | All completed sprints | `sprint in closedSprints()` |
| `futureSprints()` | All planned future sprints | `sprint in futureSprints()` |
| Named sprint | Specific sprint by name | `sprint = "Sprint 42"` |

### Sprint + Project Combination (Proven Pattern)

```json
"jql": "='project = \"' + _dp('{...project_key...}') + '\"' + (_dp('{...sprint_name...}').present? ? ' AND sprint = \"' + _dp('{...sprint_name...}') + '\"' : ' AND sprint in openSprints()')"
```

---

## String Quoting Rules

Inside `=` formula mode:
- **Outer wrapper:** Single quotes `'...'` for string literals
- **JQL values:** Escaped double quotes `\"...\"`
- **Datapill values:** Concatenated directly (they produce strings)

**Example anatomy:**
```
='project = \"'     ← literal: project = "
+ _dp('{...}')     ← datapill value, e.g., ENG
+ '\"'             ← literal: "
+ ' AND sprint'    ← literal: AND sprint...
```

**Result at runtime:** `project = "ENG" AND sprint in openSprints()`

---

## Anti-Patterns

### WRONG: Using `#{}` interpolation in formula mode
```json
"jql": "='project = \"#{_dp('{...}')}\"'"
```
Inside `=` formula mode, use bare `_dp()` — NOT `#{_dp()}`.

### WRONG: Outer parentheses wrapping the formula
```json
"jql": "=('project = \"' + _dp('{...}') + '\"')"
```
No outer `()`. This breaks condition LHS parsing in child actions.

### WRONG: Missing `=` prefix
```json
"jql": "'project = \"' + _dp('{...}') + '\"'"
```
Without `=`, the value is treated as a literal string, not a formula.

### WRONG: Single quotes for JQL values
```json
"jql": "='project = \\'' + _dp('{...}') + '\\''"
```
JQL expects double quotes for string values, not single quotes.
