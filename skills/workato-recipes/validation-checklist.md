# Base Recipe Validation Checklist

Use this checklist to validate any Workato recipe JSON before pushing. Run through each section sequentially.

---

## Recipe Structure

- [ ] Top-level keys present: `name`, `version`, `private`, `concurrency`, `code`, `config`
- [ ] `code` is an object (the trigger), NOT an array
- [ ] `code` is NOT wrapped in a `recipe` object
- [ ] Trigger has `number: 0`
- [ ] All action `number` fields are sequential with no gaps (0, 1, 2, 3...)
- [ ] Filename matches `name` field (lowercase, underscores for spaces)

## UUIDs

- [ ] All `uuid` values are unique within the recipe
- [ ] All `uuid` values are max 36 characters
- [ ] All `uuid` values use descriptive format — e.g., `search-contact-001`, `return-success-005`
- [ ] No random hex UUIDs (do NOT copy hex UUIDs from existing UI-created recipes)

## Config & Connections

- [ ] Every provider used in actions has a matching entry in `config`
- [ ] `workato` provider is NOT in `config` (it's built-in)
- [ ] Connection config is ONLY at top-level `config` array, NOT inside action blocks
- [ ] `account_id` references use correct `zip_name`, `name`, and `folder` fields

## Datapills

- [ ] All `_dp()` JSON is valid (parseable after unescaping)
- [ ] `provider` in `_dp()` matches the source action's actual provider
- [ ] Catch block datapills use `"provider":"catch"`, NOT `"provider":null`
- [ ] `line` in `_dp()` matches the `as` alias of the source action
- [ ] Path arrays use correct structure: strings for field names, `{"path_element_type":"current_item"}` for array access, `{"path_element_type":"size"}` for counts
- [ ] No `["body"]` wrapper in paths for native connectors (Salesforce, Stripe, Slack native). Only adhoc HTTP uses `["body"]`
- [ ] Formula mode (`=` prefix) used for concatenation and `.present?` checks — no `#{}` wrapper
- [ ] Single datapills use `#{}` interpolation syntax

## Extended Schemas

- [ ] Every field in `input` has a corresponding entry in `extended_input_schema`
- [ ] Nested objects in `input` have matching nested `properties` in the schema
- [ ] Field names match exactly between `input` and schema
- [ ] For adhoc HTTP actions, the nested `input.data` object is fully defined in EIS
- [ ] **Exception:** Native connector internal parameters (e.g., Salesforce `sobject_name`, `limit`) must NOT be in EIS — see connector-specific checklist

## Triggers — API Endpoint

- [ ] Trigger has `format_version: 2`
- [ ] `request.schema` is a stringified JSON array defining all input fields
- [ ] `response.responses` array defines at least a 200 and one error status code
- [ ] Every `return_response` action's `http_status_code` matches a defined response
- [ ] ALL `return_response` actions share IDENTICAL `extended_input_schema`
- [ ] ALL `return_response` actions share IDENTICAL `extended_output_schema`
- [ ] `extended_input_schema` fully defines ALL fields referenced in `input.response`
- [ ] Fields that can't always have a value are `"optional": true` in EIS/EOS
- [ ] `pick_list` in EIS/EOS `http_status_code` field lists ALL response codes from trigger

## Triggers — Callable Recipe

- [ ] `result_schema_json` defines all expected return fields
- [ ] Every `return_result` action provides values for all fields in `result_schema_json`

## Control Flow — Try/Catch

- [ ] Catch block is the LAST element in its parent try block's `block` array
- [ ] Catch has `"provider": null` (explicit null, not omitted)
- [ ] Catch has an `as` alias
- [ ] Catch `input` has `max_retry_count` and `retry_interval`
- [ ] Step numbering continues sequentially from try block through catch block

## Control Flow — Foreach

- [ ] Foreach has `as`, `repeat_mode`, `source`, `block`, `input`
- [ ] When mapping arrays in return_response, uses `____source` pattern (NOT flat string datapill)
- [ ] `____source` value points to the array datapill
- [ ] Individual field mappings use `{"path_element_type":"current_item"}` in path
- [ ] List counts use `{"path_element_type":"size"}` — NOT `current_item.list_size`

## Adhoc HTTP Actions

- [ ] Response datapill paths include `["body"]` wrapper
- [ ] `input.input.schema` is a stringified JSON array
- [ ] `input.output` is a stringified JSON array for response schema
- [ ] `verb`, `request_type` (for POST/PUT/PATCH), `response_type` are present
- [ ] `mnemonic` describes the API call

## Error Handling

- [ ] ALL code paths (success AND catch) provide values for required return fields
- [ ] Catch blocks use `"=null"` for unavailable fields, NOT empty string `""`
- [ ] All required fields in `result_schema_json` are mapped in every return path

---

## Connector-Specific Validation

After completing the base checklist above, run the connector-specific checklist for your target connector:

- **Salesforce:** See [salesforce-recipes/validation-checklist.md](../salesforce-recipes/validation-checklist.md)
- **Slack:** See [slack-recipes/validation-checklist.md](../slack-recipes/validation-checklist.md)
- **Gmail:** See [gmail-recipes/validation-checklist.md](../gmail-recipes/validation-checklist.md)
