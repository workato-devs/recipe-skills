# Jira Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

The following checks are specific to Jira connector recipes.

---

## Config & Connection

- [ ] Config includes `jira` provider with connection reference (`account_id` with `zip_name`, `name`, `folder`)

## Action Names

- [ ] `search_issues_by_JQL` is exactly case-correct (uppercase `JQL`, NOT `jql` or `Jql`)
- [ ] Action names for untested actions (`create_issue`, `update_issue`, `get_issue`) include a comment or warning noting they are not yet validated via CLI push

## JQL Input Field

- [ ] Native field name is `jql` (NOT `query`) in the `input` block
- [ ] `jql` value uses `=` formula mode prefix (bare `_dp()` calls, no `#{}` wrapper)
- [ ] JQL string values wrapped in double quotes: `\"value\"` inside formula mode strings
- [ ] No outer `()` wrapping the entire formula expression after `=`

## Extended Input Schema

- [ ] `extended_input_schema` is `[]` for `search_issues_by_JQL` — `jql` is a connector internal, NEVER in EIS
- [ ] No connector-internal fields appear in EIS (prevents duplicate fields in UI)

## Datapill Paths

- [ ] Datapill paths do NOT include `["body"]` wrapper (Jira is a native connector)
- [ ] Issues array accessed via `"path":["issues"]`
- [ ] Individual issue fields accessed via `["issues", {"path_element_type": "current_item"}, "field_name"]`

## Array Handling

- [ ] Issues array serialized with `.to_json` when returning as a string in response body
- [ ] Issue count uses `{"path_element_type": "size"}` in datapill path — NOT `.size` formula method
- [ ] Issues array returned in `"optional": true` response fields (may be null on error paths)

## Catch Blocks

- [ ] Catch datapills use `"provider":"catch"` — NOT `"provider":null`

## Conditional JQL

- [ ] Optional filter clauses (sprint name, assignee) use `.present?` ternary pattern
- [ ] Default fallback provided when optional filter is absent (e.g., `openSprints()` when no sprint name given)
