# Custom Connector Actions (Connector SDK)

This pattern covers recipes that use actions from connectors built with the Workato Connector SDK. These connectors are developed by vendors, partners, or in-house teams to extend Workato's integration capabilities.

---

## When This Applies

Use this pattern when:
- The connector was built using the Workato Connector SDK (Ruby-based)
- The provider name contains workspace/connector IDs (e.g., `notion_connector_2100000735_1762298115`)
- The connection config includes `"custom": true`

---

## Provider Naming Convention

SDK-built connectors have compound provider names:

```
{connector_name}_connector_{workspace_id}_{connector_id}
```

**Examples:**
```json
"provider": "notion_connector_2100000735_1762298115"
"provider": "nabu_casa_home_assistant_cloud__connector_2100002083_1768260720"
```

Compare to built-in connectors:
```json
"provider": "salesforce"
"provider": "stripe"
"provider": "workato_api_platform"
```

> **Important:** The provider name is workspace-specific. When sharing recipes across workspaces, the provider ID will differ even for the same connector.

---

## Config Section

SDK connectors require the `"custom": true` flag in the connection config:

```json
{
  "keyword": "application",
  "provider": "notion_connector_2100000735_1762298115",
  "skip_validation": false,
  "account_id": {
    "zip_name": "Connections/my_notion_account.connection.json",
    "name": "My Notion account",
    "folder": "Connections",
    "custom": true
  }
}
```

### Required Fields

| Field | Description |
|-------|-------------|
| `provider` | Full SDK connector provider ID |
| `custom` | Must be `true` for SDK connectors |
| `name` | Display name of the connection in Workato |
| `zip_name` | Path to connection file for `workato push` |
| `folder` | Folder containing the connection file |

---

## Action Structure

SDK connector actions follow standard Workato action structure. The `name` field corresponds to actions defined in the connector's SDK code.

```json
{
  "number": 3,
  "provider": "nabu_casa_home_assistant_cloud__connector_2100002083_1768260720",
  "name": "get_entity_state",
  "as": "get_ha_entity_state",
  "keyword": "action",
  "input": {
    "entity_id": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"trigger\",\"path\":[\"request\",\"entity_id\"]}')"
  },
  "uuid": "get-entity-state-001"
}
```

### Action Fields

| Field | Description |
|-------|-------------|
| `provider` | Full SDK connector provider ID |
| `name` | Action name as defined in SDK (e.g., `get_entity_state`, `call_service`) |
| `as` | Step alias for datapill references |
| `input` | Input fields matching SDK action schema |

---

## Datapill References

When referencing output from SDK connector actions, use the full provider ID:

```json
"=_dp('{\"pill_type\":\"output\",\"provider\":\"notion_connector_2100000735_1762298115\",\"line\":\"00decb03\",\"path\":[\"page_id\"]}')"
```

The `path` array navigates the output schema defined in the SDK connector.

---

## Extended Schemas

SDK connectors expose their input/output schemas via `extended_input_schema` and `extended_output_schema`. These are defined in the connector's SDK code and serialized into the recipe JSON.

```json
"extended_input_schema": [
  {
    "control_type": "text",
    "label": "Entity ID",
    "name": "entity_id",
    "optional": false,
    "type": "string"
  }
],
"extended_output_schema": [
  {
    "control_type": "text",
    "label": "Page ID",
    "name": "page_id",
    "optional": true,
    "type": "string"
  }
]
```

> **Note:** Copy complete schemas from working recipes or the Workato UI. Simplified schemas may cause validation errors or missing data.

---

## Portability Considerations

SDK connector recipes have portability constraints:

1. **Provider ID is workspace-specific** - The numeric IDs in the provider name differ across workspaces
2. **Connector must be installed** - The target workspace must have the same SDK connector installed
3. **Connection names may differ** - Update `account_id.name` to match the target workspace's connection

### Cross-Workspace Deployment

When deploying to a different workspace:

1. Install the same SDK connector in the target workspace
2. Update the `provider` field with the target workspace's connector ID
3. Update `account_id.name` to match the target connection name
4. Update `account_id.zip_name` if folder structure differs

---

## Example: Complete SDK Action

```json
{
  "number": 6,
  "provider": "notion_connector_2100000735_1762298115",
  "name": "publish_release_notes",
  "as": "publish_to_notion",
  "title": null,
  "description": "Publish content to Notion database",
  "keyword": "action",
  "input": {
    "page_parent": "database",
    "page_parent_id": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"trigger\",\"path\":[\"request\",\"database_id\"]}')",
    "page_title": "Release =_dp('{\"pill_type\":\"output\",\"provider\":\"workato_api_platform\",\"line\":\"trigger\",\"path\":[\"request\",\"version\"]}')",
    "blocks_source": "raw",
    "blocks_json": "=_dp('{\"pill_type\":\"output\",\"provider\":\"workato_custom_code\",\"line\":\"e68ad202\",\"path\":[\"output\",\"output\",\"blocks_json\"]}')"
  },
  "extended_output_schema": [
    {
      "control_type": "text",
      "label": "Page ID",
      "name": "page_id",
      "optional": true,
      "type": "string"
    },
    {
      "control_type": "text",
      "label": "Page URL",
      "name": "page_url",
      "optional": true,
      "type": "string"
    }
  ],
  "extended_input_schema": [
    {
      "control_type": "select",
      "default": "database",
      "label": "Parent type",
      "name": "page_parent",
      "optional": false,
      "pick_list": [
        ["Database", "database"],
        ["Page", "page"]
      ],
      "type": "string"
    },
    {
      "control_type": "text",
      "label": "Parent ID",
      "name": "page_parent_id",
      "optional": false,
      "type": "string"
    },
    {
      "control_type": "text",
      "label": "Page title",
      "name": "page_title",
      "optional": true,
      "type": "string"
    }
  ],
  "uuid": "publish-notion-001"
}
```

---

## Validation Checklist

- [ ] Provider ID matches target workspace's connector installation
- [ ] `"custom": true` is set in `account_id` config
- [ ] Connection name matches target workspace
- [ ] All `extended_input_schema` fields are complete
- [ ] Datapill references use the full SDK provider ID

For cross-cutting validation (UUIDs, numbering, config, datapills), see [validation-checklist.md](../validation-checklist.md).
