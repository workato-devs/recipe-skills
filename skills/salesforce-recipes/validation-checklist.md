# Salesforce Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

The following checks are specific to Salesforce connector recipes.

---

## Config & Connection

- [ ] Config includes `salesforce` provider with connection reference

## Actions

- [ ] Action uses correct `name`: `upsert_sobject`, `update_sobject`, `search_sobjects`, or `search_sobjects_soql`
- [ ] `sobject_name` matches target SObject API name exactly
- [ ] `dynamicPickListSelection` is present on all Salesforce actions
- [ ] `sobject_name` is in both `dynamicPickListSelection` AND `input`

## Upsert Operations

- [ ] `query_field.primary_key` is specified (user-provided external ID field)
- [ ] `dynamicPickListSelection` includes `query_field.primary_key` with label/value pair

## Update Operations

- [ ] Required `id` field is included in `input`

## Search Operations (`search_sobjects`)

- [ ] `sobject_name` and `limit` are NOT in `extended_input_schema` (they are connector internals — including them produces malformed SOQL)
- [ ] Field filter fields (e.g., `Id`, `Email`, `AccountId`) ARE in `extended_input_schema` (or they get silently dropped)
- [ ] `limit` parameter uses `"type":"integer"` with `"parse_output":"integer_conversion"` (NOT `"type":"number"` which produces `LIMIT 50.0`)

## SOQL Queries (`search_sobjects_soql`)

- [ ] Action name is `search_sobjects_soql`, NOT `search_sobjects` with a `query` parameter
- [ ] No `extended_input_schema` needed on the SOQL search action itself
- [ ] String values in SOQL use `'#{datapill}'` (NOT `:#{datapill}` bind variables)
- [ ] Dates and numbers in SOQL use `#{datapill}` (no quotes)

## Datapill Paths

- [ ] Datapill paths do NOT include `["body"]` wrapper
- [ ] Search results accessed via `{"path_element_type":"current_item"}` in path

## Custom Objects

- [ ] Custom fields/objects (with `__c`, `__mdt`, `__e`, `__x`) are documented as implementation-specific in recipe description
