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

## Asana-Specific

- [ ] Resource GIDs are typed as `"string"`, not `"integer"`
- [ ] Workspace/project GIDs are parameterized (not hardcoded)
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
