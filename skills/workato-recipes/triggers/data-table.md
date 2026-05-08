# Data Table Trigger

Use the data table trigger when your recipe should run in response to row creation or updates in a Workato data table. This is the canonical pattern for "row-driven notification" workflows — e.g. a row appearing in a `pending_approvals` table fires a Slack DM with action buttons.

## Provider Details

| Field | Value |
|-------|-------|
| Provider | `workato_db_table` |
| Action (new record) | `new_record_v2` |
| Action (updated record) | `updated_record_v2` |
| Config provider | `workato_db_table` with `account_id: null` |

> **Required:** `workato_db_table` config entries must include `"account_id": null` explicitly. Omitting the field can cause `Passed nil into T.must` at import time.

---

## New Record Trigger

Fires once per row inserted into the table.

```json
{
  "number": 0,
  "provider": "workato_db_table",
  "name": "new_record_v2",
  "as": "new_pending_approval",
  "keyword": "trigger",
  "input": {
    "table_id": {
      "zip_name": "data tables/pending_approvals.workato_db_table.json",
      "name": "pending_approvals",
      "folder": "data tables"
    }
  },
  "extended_output_schema": [
    {
      "label": "Record",
      "name": "record",
      "type": "object",
      "properties": [
        { "control_type": "text", "label": "Approval ID", "name": "<column-uuid-with-underscores>", "type": "string" },
        { "control_type": "text", "label": "Status", "name": "<column-uuid-with-underscores>", "type": "string" }
      ]
    }
  ],
  "uuid": "trigger-001"
}
```

### Key structural rules

- **`table_id` must be a reference object**, not a string. The `zip_name` path must match the data-table file's location in the project zip.
- **Output column names use the column UUIDs**, with hyphens replaced by underscores. Example: a column with UUID `5d420ed4-eafd-44d7-89ae-77ed9c46dba5` is referenced as `5d420ed4_eafd_44d7_89ae_77ed9c46dba5` in the EOS and in datapill paths.
- **Datapill access:**
  ```json
  "#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"new_pending_approval\",\"path\":[\"record\",\"<column-uuid-with-underscores>\"]}')}"
  ```

  The `record` wrapper is always present.

---

## Updated Record Trigger

Same provider, action `updated_record_v2`, same input shape. Fires when an existing row is modified.

---

## Universal Meta Record ID

Every data-table-triggered row has a built-in Record ID column you can reference without declaring it in your EOS. Use the universal meta UUID:

```
11fbe9a6_a16d_4d7e_86ea_afe42ec03005
```

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_db_table\",\"line\":\"new_pending_approval\",\"path\":[\"record\",\"11fbe9a6_a16d_4d7e_86ea_afe42ec03005\"]}')}"
```

This Record ID is what `update_record` and `delete_record` actions need as their target — pass it through to any downstream "update this same row" step (e.g. saving a Slack message channel/timestamp back to the row after sending the DM).

---

## Common Pattern: Row-Driven Slack Notification with Buttons

Wire a data-table trigger to:

1. **Look up Slack user** by email (datapill from the row).
2. **Send a Slack DM** with action buttons via `post_bot_message` (Workbot).
3. **Update the same row** with the resulting Slack channel + message timestamp via `update_record`, so a later button click can find the message to update.

For the Slack-side patterns (button shapes, params format, `post_bot_message`, `update_blocks_by_block_id`), see [slack-recipes/patterns/workbot-triggers.md](../../slack-recipes/patterns/workbot-triggers.md).

---

## Validation Checklist

- [ ] Provider is `workato_db_table`
- [ ] Action name is `new_record_v2` or `updated_record_v2`
- [ ] `input.table_id` is a reference object with `zip_name`/`name`/`folder` (NOT a string)
- [ ] Config entry includes `"account_id": null` explicitly
- [ ] Datapill paths use `["record", "<column-uuid-with-underscores>"]`
- [ ] Record ID datapill uses the universal meta UUID `11fbe9a6_a16d_4d7e_86ea_afe42ec03005`

---

## Related Documentation

- [Recipe Structure](../fundamentals/recipe-structure.md)
- [Datapill Syntax](../fundamentals/datapill-syntax.md)
- [Slack Workbot Triggers](../../slack-recipes/patterns/workbot-triggers.md) — the Slack-side patterns for button-driven row updates
