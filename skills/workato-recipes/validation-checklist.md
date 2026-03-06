# Base Recipe Validation Checklist

Use this checklist to validate any Workato recipe JSON before pushing. Run the cross-cutting checks below first, then run the pattern-specific checklist in each skill file your recipe uses.

## Adding New Checklist Items

Each skill file owns its own `## Validation Checklist` with rules specific to that construct. This file holds only cross-cutting rules that apply to every recipe.

- **New rule specific to one pattern** (e.g., "no `elsif` keyword") → add to that skill file's `## Validation Checklist`
- **New rule that applies to all recipes** (e.g., "UUIDs max 36 chars") → add to this file under Cross-Cutting Checks

Never duplicate items between this file and the inline checklists.

---

## Cross-Cutting Checks

### Recipe Structure

- [ ] Top-level keys present: `name`, `version`, `private`, `concurrency`, `code`, `config`
- [ ] `code` is an object (the trigger), NOT an array
- [ ] `code` is NOT wrapped in a `recipe` object
- [ ] Trigger has `number: 0`
- [ ] All action `number` fields are sequential with no gaps (0, 1, 2, 3...)
- [ ] Filename matches `name` field (lowercase, underscores for spaces)

### UUIDs

- [ ] All `uuid` values are unique within the recipe
- [ ] All `uuid` values are max 36 characters
- [ ] All `uuid` values use descriptive format — e.g., `search-contact-001`, `return-success-005`
- [ ] No random hex UUIDs (do NOT copy hex UUIDs from existing UI-created recipes)

### Config & Connections

- [ ] Every provider used in actions has a matching entry in `config`
- [ ] `workato` provider is NOT used — use `workato_variable` instead (see [variables-and-lists.md](patterns/variables-and-lists.md))
- [ ] Connection config is ONLY at top-level `config` array, NOT inside action blocks
- [ ] `account_id` references use correct `zip_name`, `name`, and `folder` fields

### Formulas

- [ ] All formula methods used are in the [Supported Formula Methods allowlist](SKILL_INSTRUCTIONS.md#supported-formula-methods-complete-allowlist)
- [ ] No `.utc` — use `in_time_zone("UTC")` or `strftime('%Y-%m-%dT%H:%M:%SZ')`
- [ ] No `.parse_json` — use `json_parser` connector's `parse_json_v2` action
- [ ] No integer array index (`[0]`, `[n]`) — use `.first` / `.last`
- [ ] No Ruby-only methods (`.each`, `.map`, `.select`, `.chomp`, `.merge`, etc.)

### Datapills

- [ ] All `_dp()` JSON is valid (parseable after unescaping)
- [ ] `provider` in `_dp()` matches the source action's actual provider
- [ ] Catch block datapills use `"provider":"catch"`, NOT `"provider":null`
- [ ] `line` in `_dp()` matches the `as` alias of the source action
- [ ] Path arrays use correct structure: strings for field names, `{"path_element_type":"current_item"}` for array access, `{"path_element_type":"size"}` for counts
- [ ] No `["body"]` wrapper in paths for native connectors (Salesforce, Stripe, Slack native). Only adhoc HTTP uses `["body"]`
- [ ] Formula mode (`=` prefix) used for concatenation and `.present?` checks — no `#{}` wrapper
- [ ] Single datapills use `#{}` interpolation syntax

### Extended Schemas

- [ ] Every field in `input` has a corresponding entry in `extended_input_schema`
- [ ] Nested objects in `input` have matching nested `properties` in the schema
- [ ] Field names match exactly between `input` and schema
- [ ] For adhoc HTTP actions, the nested `input.data` object is fully defined in EIS
- [ ] **Exception:** Native connector internal parameters (e.g., Salesforce `sobject_name`, `limit`) must NOT be in EIS — see connector-specific checklist

### Error Handling

- [ ] ALL code paths (success AND catch) provide values for required return fields
- [ ] Catch blocks use `"=null"` for unavailable fields, NOT empty string `""`
- [ ] All required fields in `result_schema_json` are mapped in every return path

---

## Pattern-Specific Checklists

Run the inline checklist in each pattern your recipe uses:

- [If/Else](control-flow/if-else.md#validation-checklist)
- [Try/Catch](control-flow/try-catch.md#validation-checklist)
- [Foreach](control-flow/foreach.md#validation-checklist)
- [Variables & Lists](patterns/variables-and-lists.md#validation-checklist)
- [Adhoc HTTP Actions](patterns/adhoc-http-actions.md#validation-checklist)
- [Custom Connector Actions](patterns/custom-connector-actions.md#validation-checklist)
- [API Endpoint Trigger](triggers/api-endpoint.md#validation-checklist)
- [Callable Recipe Trigger](triggers/callable-recipe.md#validation-checklist)

---

## Connector-Specific Validation

After completing the checks above, run the connector-specific checklist for your target connector:

- **Salesforce:** See [salesforce-recipes/validation-checklist.md](../salesforce-recipes/validation-checklist.md)
- **Slack:** See [slack-recipes/validation-checklist.md](../slack-recipes/validation-checklist.md)
- **Gmail:** See [gmail-recipes/validation-checklist.md](../gmail-recipes/validation-checklist.md)
