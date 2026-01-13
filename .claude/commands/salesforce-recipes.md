# Salesforce Recipes Skill

You are now equipped with Salesforce-specific knowledge for writing Workato recipes. This skill extends the **workato-recipes** base skill.

> **Important:** For trigger types, control flow, and datapill fundamentals, see the `workato-recipes` skill. This skill focuses on Salesforce-specific patterns.

## Capabilities

With this skill loaded, you can:
- Create recipes for Salesforce record searches (Contacts, Accounts, Opportunities, custom objects)
- Create recipes for upserting records with external ID handling
- Create recipes for updating existing records by Salesforce ID
- Work with standard SObjects (Contact, Account, Lead, etc.)
- Work with custom objects and fields (with proper documentation)
- Handle picklist fields and relationship lookups

## Trigger Type Selection

Ask the user which trigger type they need:
- **API Endpoint** (`workato_api_platform`) - External HTTP access
- **Callable Recipe** (`workato_recipe_function`) - Internal recipe calls

See `workato-recipes` skill for trigger implementation details.

## Salesforce-Specific Knowledge

### extended_input_schema (CRITICAL)

All Salesforce actions require complete `extended_input_schema` definitions for every field in the `input` section. **You MUST copy the complete `extended_input_schema` from validated templates.** Simplified schemas will cause validation errors.

See `workato-recipes` base skill for full documentation.

### Datapill Paths (CRITICAL)

**Salesforce does NOT use the `["body"]` wrapper** in datapill paths:

```json
// CORRECT for Salesforce
"path": ["Id"]
"path": ["Email"]
"path": ["Contact", {"path_element_type":"current_item"}, "Email"]

// WRONG - Do NOT use for Salesforce
"path": ["body", "Id"]
```

### Native Salesforce Actions

Workato provides built-in Salesforce connector actions:
- `upsert_sobject` - Create or update records using external ID
- `update_sobject` - Update existing record by Salesforce ID
- `search_sobjects` - Search for records by field criteria

### Custom Objects Warning

Custom objects and fields (ending in `__c`, `__mdt`, `__e`, `__x`) are implementation-specific and NOT standard across Salesforce orgs. Always:
- Ask the user if uncertain whether an object/field is custom
- Document clearly that the recipe requires specific custom objects/fields
- Use standard objects whenever possible for portability

### Upsert External ID Pattern

When upserting, always specify the external ID field in `query_field.primary_key`. This field must be marked as "External ID" in Salesforce OR be a standard unique field like `Email`.

## Reference Files

- `skills/workato-recipes/SKILL_INSTRUCTIONS.md` - Base platform knowledge
- `skills/salesforce-recipes/SKILL_INSTRUCTIONS.md` - Salesforce-specific knowledge
- `skills/salesforce-recipes/templates/` - Validated recipe templates
- `skills/salesforce-recipes/patterns/` - Pattern documentation

## Usage

### Before Generating Recipes

**CRITICAL: Always ask the user for these details first:**

1. **Salesforce connection name** - What is the exact name of their Salesforce connection in Workato?
   - Example: "ZT Dev account", "Salesforce Production", "SF Sandbox"
   - This will be used in the `account_id.name` field in the config section

2. **Trigger type** - API endpoint or callable recipe?

3. **Operation details** - What Salesforce operation do they need?

### Recipe Generation Steps

When asked to create a Salesforce recipe:

1. **Ask for connection name** (see above - REQUIRED)
2. **Ask about trigger type** - API endpoint or callable recipe?
3. **Identify the Salesforce operation** - search, upsert, or update?
4. **Clarify object and fields** - Standard or custom? External ID field?
5. **Apply Salesforce patterns** - Proper datapill paths, complete schemas, external ID handling
6. **Generate valid JSON** using base skill structure + Salesforce specifics with correct connection name

## Example Prompts

- "Create an API endpoint recipe that upserts a Salesforce Contact by email"
- "Create a callable recipe to search for an Account by name and update its status"
- "Create a recipe to update a Booking__c custom object by Salesforce ID"
