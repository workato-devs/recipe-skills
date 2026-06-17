# Asana Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

The following checks are specific to Asana connector recipes.

---

## Config & Connection

- [ ] Config includes `asana` provider with connection reference
- [ ] Connection `account_id` has correct `name` matching the workspace's Asana connection
- [ ] If using adhoc HTTP, the `asana` provider is still in config (not a separate HTTP connector)

## Actions

- [ ] Action `name` matches a valid name in `lint-rules.json` or is `__adhoc_http_action`
- [ ] For operations not covered by native actions, uses `__adhoc_http_action` with correct `mnemonic`
- [ ] `keyword` is `"action"` for all non-trigger steps

## Adhoc HTTP (`__adhoc_http_action`)

- [ ] Path uses a leading `/` — e.g. `/api/1.0/tasks` not `api/1.0/tasks`
- [ ] `extended_output_schema` is declared for every field referenced by downstream datapills
- [ ] Workspace GID passed as plain string in `input.data` — NOT as `'gid'` with surrounding quotes (causes "Not a Long" 400)
- [ ] `mnemonic` describes the operation for readability

## Asana-Specific

- [ ] Resource GIDs are typed as `"string"`, not `"integer"`
- [ ] Workspace/project GIDs are parameterized OR intentionally hardcoded — if exposing as an MCP tool, consider hardcoding the workspace GID to prevent AI agents from substituting GIDs from their own integrations
- [ ] `pick_list` values match Asana API enum values (e.g., `resource_subtype`: default_task, milestone, approval)
- [ ] `dynamicPickListSelection` included where the connector requires it (e.g., `new_event` trigger)

## Datapill Paths

- [ ] Datapill paths do NOT include `["body"]` wrapper
- [ ] Array access uses `{"path_element_type":"current_item"}` in foreach loops

## Trigger (if using `new_event`)

- [ ] `workspace_id` is provided (required)
- [ ] `actions` filter is set appropriately (changed/deleted/removed/added/undeleted)

## Naming

- [ ] Recipe name describes the operation clearly
- [ ] Filename uses snake_case matching the operation (e.g., `create_a_task.recipe.json`)
