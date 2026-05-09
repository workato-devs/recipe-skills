# Data Tables Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md) for base recipe validation.

The following checks are specific to the `workato_db_table` connector.

---

## Config & Connection

- [ ] Config includes `workato_db_table` provider entry
- [ ] `account_id` is explicitly `null` (not omitted)
- [ ] No `zip_name`/`name`/`folder` reference in `account_id` — this is an internal connector

## Table Reference

- [ ] `input.table_id` is a reference object `{zip_name, name, folder}` for portable import (not a numeric string)
- [ ] `zip_name` matches the actual `.workato_db_table.json` filename in the project
- [ ] `dynamicPickListSelection` is present with `{"table_id": "TableDisplayName"}`
- [ ] `dynamicPickListSelection.table_id` uses the table display name (not numeric ID)

## Column Names

- [ ] All column references use UUID format with underscores (e.g., `5d420ed4_eafd_44d7_89ae_77ed9c46dba5`)
- [ ] Record ID references use the universal meta UUID `11fbe9a6_a16d_4d7e_86ea_afe42ec03005`
- [ ] Column UUIDs in `extended_output_schema` match the actual table schema
- [ ] Date/datetime columns include `parse_output: "date_time_conversion"` and `render_input: "date_time_conversion"`

## Triggers

- [ ] Trigger `name` is a valid trigger name from `lint-rules.json`
- [ ] `since` parameter is a valid ISO datetime string
- [ ] `extended_output_schema` includes `record` wrapper object
- [ ] For `updated_records_realtime`: EOS includes both `record` and `old_record` with identical properties
- [ ] `filter` block (if present) uses compound condition syntax with `operand`, `conditions`, `type`

## Actions

- [ ] Action `name` is a valid action name from `lint-rules.json`
- [ ] Update/delete actions include Record ID (`11fbe9a6_a16d_4d7e_86ea_afe42ec03005`) in input

## Datapill Paths

- [ ] Trigger datapills use `["record", "<column-uuid>"]` path (NOT `["body", ...]`)
- [ ] Old record datapills use `["old_record", "<column-uuid>"]` path
- [ ] `provider` in datapill JSON is `"workato_db_table"`
- [ ] `line` in datapill JSON matches the `as` alias of the source step
