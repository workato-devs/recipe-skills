# Salesforce Recipes Skill - Agent Instructions

> **⚠️ DEPENDENCY: Load `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, formulas, and recipe structure.

This skill provides Salesforce-specific knowledge for generating Workato recipes. It extends the **workato-recipes** base skill and focuses on Salesforce-specific patterns.

---

## CRITICAL: Pre-Generation Checklist

### For EXISTING projects:
1. **Read existing Salesforce `.recipe.json` files** to understand local patterns

### For GREENFIELD projects:
1. **Use skill templates** - see `templates/upsert-contact.json` as reference
2. **Use descriptive UUIDs** - e.g., `upsert-contact-001`, `search-account-002`

### ALWAYS:
1. **Ask for connection name** - exact name of Salesforce connection in Workato
2. **Confirm object type** - standard (Contact, Account) vs custom (ends in `__c`)
3. **Verify external ID field** - for upsert operations, which field is the external ID?
4. **Use API endpoint trigger** for testability via curl
5. **Use descriptive UUIDs** - never copy random hex UUIDs from existing recipes
6. **Remember datapill paths** - Salesforce does NOT use `["body"]` wrapper

> **WARNING:** Never assume custom objects/fields exist. Always ask if uncertain whether an object or field is custom. Custom objects are org-specific and NOT portable.

---

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Salesforce Config Requirements](#salesforce-config-requirements)
3. [Standard vs Custom Objects and Fields](#standard-vs-custom-objects-and-fields)
4. [Native Connector Guidance](#native-connector-guidance)
5. [Salesforce Datapill Paths](#salesforce-datapill-paths)
6. [Salesforce Patterns](#salesforce-patterns)
7. [Pre-Push Checklist (Salesforce)](#pre-push-checklist-salesforce)

---

## When to Use This Skill

Use this skill when building Workato recipes that:
- Search Salesforce records (Contacts, Accounts, Opportunities, Cases, Leads, custom objects)
- Create new records in Salesforce
- Upsert records using external IDs
- Update existing records by Salesforce ID
- Work with standard or custom SObjects

**Prerequisites:**
- `workato-recipes` base skill loaded
- Workato workspace with Salesforce connection configured
- Understanding of the target Salesforce org's object schema

---

## Salesforce Config Requirements

Every Salesforce recipe requires the `salesforce` provider in the config section:

```json
{
  "keyword": "application",
  "provider": "salesforce",
  "skip_validation": false,
  "account_id": {
    "zip_name": "Workspace Connections/salesforce_connection.connection.json",
    "name": "Salesforce Connection Name",
    "folder": "Workspace Connections"
  }
}
```

**Combined with trigger provider:**

For callable recipe trigger:
```json
"config": [
  { "provider": "workato_recipe_function", "account_id": null, ... },
  { "provider": "salesforce", "account_id": { ... }, ... },
  { "provider": "logger", "account_id": null, ... }
]
```

---

## Standard vs Custom Objects and Fields

### CRITICAL: Custom Objects Are Implementation-Specific

**Standard SObjects** (available in ALL Salesforce orgs):
- `Contact`, `Account`, `Lead`, `Opportunity`, `Case`, `Task`, `Event`
- Standard fields: `Id`, `Name`, `Email`, `Phone`, `AccountId`, etc.

**Custom Objects and Fields** (specific to each Salesforce implementation):
- Custom objects: `Booking__c`, `Room__c`, `Property__c`
- Custom fields: `Contact_Type__c`, `Unique_Email__c`, `Status__c`
- Custom metadata types: `Config__mdt`, `Settings__mdt`

### Object and Field Suffixes

| Suffix | Type | Example | Notes |
|--------|------|---------|-------|
| `__c` | Custom Object/Field | `Booking__c`, `Status__c` | **NOT standard across orgs** |
| `__mdt` | Custom Metadata Type | `Config__mdt` | **NOT standard across orgs** |
| `__e` | Platform Event | `Order_Event__e` | **NOT standard across orgs** |
| `__x` | External Object | `SAP_Account__x` | **NOT standard across orgs** |
| (none) | Standard Object/Field | `Contact`, `Email` | Standard across all orgs |

### Agent Requirements for Custom Objects

> **WARNING:** When generating recipes that use custom objects or fields (anything with `__c`, `__mdt`, `__e`, `__x`), you MUST:
>
> 1. **Never assume** these objects/fields exist in the target environment
> 2. **Document clearly** that the recipe requires specific custom objects/fields
> 3. **Ask the user** if uncertain whether an object/field is custom or standard
> 4. **Use standard objects** whenever possible for maximum portability

**Example of proper documentation:**

```json
{
  "name": "Upsert contact with custom type",
  "description": "REQUIRES CUSTOM FIELD: Contact.Contact_Type__c (picklist)",
  ...
}
```

---

## Native Connector Guidance

The Salesforce connector provides 32 native actions and 15 triggers. See `lint-rules.json` for the authoritative list of valid action and trigger names.

> **CRITICAL:** All Salesforce actions require `dynamicPickListSelection` in addition to the `input` block. See [dynamicPickListSelection](#dynamicpicklistselection-critical) below.

### Choosing the Right Trigger

- **Polling (most common):** `scheduled_sobject_soql_query` — runs a SOQL query on a schedule to detect new/changed records. V2 variant: `scheduled_sobject_soql_query_v2`.
- **Real-time CDC:** `change_data_capture` — streams record changes as they happen. Requires CDC enabled on the SObject. Prefer over `new_pushtopic_event` (legacy).
- **Platform Events:** `new_platform_event` — listens for platform event messages.
- **Outbound Messages:** `new_outbound_message` — triggered by Salesforce workflow/process builder.
- **Bulk:** `sobject_created_bulk`, `sobject_batch_created`, `scheduled_sobject_bulk_v2_created`, `scheduled_sobject_bulk_v2_created_or_updated` — for high-volume record processing.
- **Custom objects:** `new_custom_object`, `updated_custom_object` (+ `_webhook` variants for real-time).
- **Deletions:** `sobject_deleted` — triggers on record deletion.

### Choosing the Right Action

**Record CRUD:**
- **`upsert_sobject`** — Create or update by external ID. Best default for sync workflows. See [detail below](#upsert_sobject-detail).
- **`update_sobject`** — Update by Salesforce record ID when you already have the ID. See [detail below](#update_sobject-detail).
- **`delete_sobject`** — Delete by Salesforce record ID.
- **`create_custom_object`** / **`get_custom_object`** — Create or retrieve custom object records.
- **No native "get standard record by ID" action** — use `search_sobjects` with an `Id` filter or `search_sobjects_soql` with `WHERE Id = '...'`.

**Search:**
- **`search_sobjects`** — Exact field match only (equality). Has critical EIS rules. See [detail below](#search_sobjects-detail).
- **`search_sobjects_soql`** — Raw SOQL for complex criteria (LIKE, IN, OR, ORDER BY). See [detail below](#search_sobjects_soql-detail).
- **`search_sobjects_soql_v2`** — V2 of SOQL search.

**Bulk operations** (thousands+ records):
- **`insert_bulk_job`** / **`upsert_bulk_job`** / **`update_bulk_job`** — Bulk create/upsert/update. V1 variants (`_v1` suffix) also available.
- **`retry_bulk_jobs`** — Retry failed bulk jobs.
- **`search_sobjects_soql_bulk_csv`** / **`_v2`** — Bulk SOQL query returning CSV.

**Composite** (multiple operations in one API call):
- **`composite_create_sobject`** / **`composite_update_sobject`** / **`upsert_composite_sobject`**

**Approvals:** `approve_process`, `reject_process`, `submit_process`

**Files & attachments:** `upload_file_content`, `get_attachment_body`, `get_combined_attachment`

**Reports & metadata:** `get_report_by_id`, `get_related`, `get_sobject_schema`

**Platform events:** `create_custom_platform_event`

**Data categories:** `list_data_category_groups`, `read_data_category_group`

**Uncovered operations:** Use `__adhoc_http_action` for REST API endpoints, Tooling API, Metadata API, or custom Apex REST services not covered by native actions.

---

### dynamicPickListSelection (CRITICAL)

**All Salesforce actions require `dynamicPickListSelection` in addition to the `input` block.** This is used by the Workato UI for field discovery.

```json
{
  "provider": "salesforce",
  "name": "upsert_sobject",
  "as": "upsert_contact",
  "keyword": "action",
  "dynamicPickListSelection": {
    "sobject_name": "Contact",
    "query_field.primary_key": [
      { "label": "Email", "value": "Email" }
    ]
  },
  "input": {
    "sobject_name": "Contact",
    "query_field": { "primary_key": "Email" },
    ...
  }
}
```

**Note:** Both `dynamicPickListSelection.sobject_name` AND `input.sobject_name` are required. They should have the same value.

### upsert_sobject Detail

**Use when:** Creating or updating records based on an external ID field.

```json
{
  "provider": "salesforce",
  "name": "upsert_sobject",
  "as": "upsert_contact",
  "keyword": "action",
  "dynamicPickListSelection": {
    "sobject_name": "Contact",
    "query_field.primary_key": [
      { "label": "Email", "value": "Email" }
    ]
  },
  "input": {
    "sobject_name": "Contact",
    "query_field": {
      "primary_key": "Email"
    },
    "Email": "#{email_datapill}",
    "FirstName": "#{first_name_datapill}",
    "LastName": "#{last_name_datapill}"
  }
}
```

**Key fields:**
- `sobject_name` - SObject API name (e.g., `Contact`, `Account`, `Booking__c`)
- `query_field.primary_key` - Field to use for upsert matching (must be marked as External ID in Salesforce OR be a standard unique field)
- Other fields - SObject field values to set

**IMPORTANT:** The `query_field.primary_key` value must be:
- A field marked as "External ID" in Salesforce, OR
- A standard unique field like `Email` or `Id`
- **User must specify which field to use** - do not assume

### update_sobject Detail

**Use when:** Updating an existing record by Salesforce ID.

```json
{
  "provider": "salesforce",
  "name": "update_sobject",
  "as": "update_booking",
  "keyword": "action",
  "input": {
    "sobject_name": "Booking__c",
    "id": "#{booking_id_datapill}",
    "Status__c": "#{status_datapill}",
    "Check_Out_Date__c": "=checkout_date_datapill"
  }
}
```

**Key fields:**
- `sobject_name` - SObject API name
- `id` - Salesforce 18-character record ID (required)
- Other fields - Field values to update

### search_sobjects Detail

**Use when:** Finding records by exact field match (equality only, no LIKE/IN/OR).

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "search_contact",
  "keyword": "action",
  "dynamicPickListSelection": {
    "sobject_name": "Contact"
  },
  "input": {
    "sobject_name": "Contact",
    "limit": "150",
    "Email": "#{email_datapill}"
  },
  "extended_input_schema": [
    {
      "control_type": "text",
      "label": "Email",
      "name": "Email",
      "type": "string"
    }
  ]
}
```

**Key fields:**
- `sobject_name` - SObject API name
- `limit` - Max records to return (default 150)
- Search criteria fields - Field names with values to match (exact equality)

**Output:** Returns array of matching records

**CRITICAL - EIS Rules for `search_sobjects`:**

- `sobject_name` and `limit` are **connector internals** — do NOT include them in `extended_input_schema`. Including them causes Workato to treat them as WHERE clause field filters, producing malformed SOQL.
- Search filter fields (e.g., `Email`, `Id`, `AccountId`) **MUST** be in `extended_input_schema` or Workato silently drops them.
- Only include actual Salesforce field names in EIS, never connector parameters.

**IMPORTANT - Limit Parameter Type:**

When accepting `limit` as a user input parameter, use **integer** type in the schema:

```json
{
  "name": "limit",
  "type": "integer",
  "control_type": "integer",
  "parse_output": "integer_conversion"
}
```

Do **NOT** use `"type": "number"` - this causes Workato to treat values as floats, producing malformed SOQL (e.g., `LIMIT 50.0`) which Salesforce rejects.

### search_sobjects_soql Detail

**Use when:** Finding records with complex criteria (LIKE, IN, OR, ORDER BY, relationship fields) using raw SOQL.

**CRITICAL:** Use action name `search_sobjects_soql`, NOT `search_sobjects` with a `query` parameter. The `query` parameter is not recognized by `search_sobjects` via CLI push — it gets treated as a field name.

```json
{
  "provider": "salesforce",
  "name": "search_sobjects_soql",
  "as": "search_bookings",
  "keyword": "action",
  "dynamicPickListSelection": {
    "sobject_name": "Booking"
  },
  "input": {
    "sobject_name": "Booking__c",
    "query": "Room__r.Room_Number__c = '#{_dp('{...room_number...}')}' AND Status__c NOT IN ('Cancelled', 'No Show')"
  }
}
```

---

## SOQL Query Syntax in search_sobjects

### CRITICAL: No Bind Variables

Workato's Salesforce connector does **NOT** support SOQL bind variable syntax (`:variable`). Use direct string interpolation instead.

**WRONG (bind variable syntax - WILL NOT WORK):**
```json
"query": "Email = :#{_dp('...email...')}"
"query": "Room_Number__c = :#{_dp('...room...')}"
```

**CORRECT (string values - wrap in single quotes):**
```json
"query": "Email = '#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"email\"]}')}'"
"query": "Room_Number__c = '#{_dp('{...room_number...}')}'"
```

**CORRECT (dates/numbers - no quotes):**
```json
"query": "Check_In_Date__c <= #{_dp('{...date...}')}"
"query": "Amount__c > #{_dp('{...amount...}')}"
```

### Query Syntax Quick Reference

| Value Type | Syntax | Example |
|------------|--------|---------|
| String | `'#{datapill}'` | `Email = '#{_dp(...)}'` |
| Date | `#{datapill}` | `CreatedDate >= #{_dp(...)}` |
| Number | `#{datapill}` | `Amount > #{_dp(...)}` |
| Boolean | `#{datapill}` | `IsActive = #{_dp(...)}` |
| Picklist | `'#{datapill}'` | `Status = '#{_dp(...)}'` |

### Complex Query Examples

**Multi-condition query:**
```json
"query": "Room__r.Room_Number__c = '#{_dp('{...room_number...}')}' AND Status__c NOT IN ('Cancelled', 'No Show', 'Checked Out') AND Check_In_Date__c <= #{_dp('{...checkout_date...}')} AND Check_Out_Date__c >= #{_dp('{...checkin_date...}')}"
```

**Date range query:**
```json
"query": "CreatedDate >= #{_dp('{...start_date...}')} AND CreatedDate <= #{_dp('{...end_date...}')}"
```

See: [patterns/soql-query-syntax.md](patterns/soql-query-syntax.md)

---

## Salesforce Datapill Paths

### CRITICAL: No Body Wrapper

**Salesforce actions do NOT use the `["body"]` wrapper in datapill paths.**

This is consistent with Stripe and other native connectors:

```json
// CORRECT for Salesforce
"path": ["Id"]
"path": ["Email"]
"path": ["Status__c"]
"path": ["Account", "Name"]

// WRONG for Salesforce - Do NOT use
"path": ["body", "Id"]
```

### Salesforce Datapill Examples

**Record ID from upsert:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"upsert_contact\",\"path\":[\"id\"]}')}"
```

**Standard field:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_contact\",\"path\":[\"Contact\",{\"path_element_type\":\"current_item\"},\"Email\"]}')}"
```

**Custom field:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"upsert_booking\",\"path\":[\"Status__c\"]}')}"
```

**Relationship field (dot notation in Salesforce, nested in datapill):**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_contact\",\"path\":[\"Contact\",{\"path_element_type\":\"current_item\"},\"Account\",\"Name\"]}')}"
```

### Search Results Array Access

Search actions return arrays. Use `path_element_type: current_item` to access array elements:

```json
"path": ["Contact", {"path_element_type": "current_item"}, "Id"]
```

---

## Salesforce Patterns

### 1. Upsert with External ID

Always specify the external ID field when upserting:

```json
{
  "provider": "salesforce",
  "name": "upsert_sobject",
  "as": "upsert_contact",
  "input": {
    "sobject_name": "Contact",
    "query_field": {
      "primary_key": "Unique_Email__c"  // User specifies this field
    },
    "Unique_Email__c": "#{email}",
    "Email": "#{email}",
    "FirstName": "#{first_name}",
    "LastName": "#{last_name}"
  }
}
```

**Pattern:**
- User provides external ID field name
- Set the external ID field value in input
- Set other field values
- Workato handles create-or-update logic

### 2. Conditional Field Updates

Use Workato formulas (from base skill) to conditionally set fields:

```json
"FirstName": "=_dp('{...}').present? ? _dp('{...}') : skip",
"Phone": "=_dp('{...}').present? ? _dp('{...}') : skip"
```

This skips fields when values are empty, preventing overwrites with blanks.

### 3. Search Before Update Pattern

Search for record, then update if found:

```json
// Step 1: Search
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "search_contact",
  "input": {
    "sobject_name": "Contact",
    "Email": "#{email}"
  }
}

// Step 2: Check if found
{
  "keyword": "if",
  "input": {
    "conditions": [{
      "operand": "present",
      "lhs": "#{search_contact.Contact[].Id}"
    }]
  },
  "block": [
    // Update found record
    {
      "provider": "salesforce",
      "name": "update_sobject",
      "input": {
        "sobject_name": "Contact",
        "id": "#{search_contact.Contact[].Id}",
        "Status": "#{new_status}"
      }
    }
  ]
}
```

### 4. Working with Picklists

Picklist fields have specific allowed values. Use exact API values:

```json
"Status__c": "Confirmed",           // Correct - exact picklist value
"Contact_Type__c": "Guest"          // Correct - exact picklist value
```

**Note:** Picklist values are case-sensitive and must match Salesforce configuration.

### 5. Required Fields

Standard SObjects have required fields:
- Contact: `LastName` (required)
- Account: `Name` (required)
- Opportunity: `Name`, `StageName`, `CloseDate` (required)

Custom objects may have different requirements based on implementation.

---

## Validation

See [validation-checklist.md](validation-checklist.md) for Salesforce-specific validation, which references the base checklist in `workato-recipes/validation-checklist.md`.

### Common Salesforce Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Required field missing" | Missing required field | Add `LastName` for Contact, `Name` for Account, etc. |
| "Invalid field" | Field doesn't exist in org | Verify field API name, check if custom field exists |
| "Invalid external ID field" | Field not marked as External ID | Verify field is marked as External ID in Salesforce |
| "Duplicate value" | Unique constraint violation | Check for existing records before creating |
| "Invalid picklist value" | Wrong picklist value | Use exact API value from Salesforce picklist |
| Query returns no results unexpectedly | Using SOQL bind variable syntax | Replace `:#{datapill}` with `'#{datapill}'` for strings |

---

## Extended Input Schema Requirements

Like all Workato connectors, Salesforce actions require complete `extended_input_schema` definitions.

### Salesforce-Specific Schema Fields

Salesforce schema entries include metadata fields:

```json
{
  "name": "Email",
  "label": "Email",
  "type": "string",
  "control_type": "text",
  "custom": false,              // false for standard, true for custom
  "optional": true,
  "sfdc_createable": true,      // Can be set on create
  "sfdc_updateable": true       // Can be updated
}
```

**Custom field example:**
```json
{
  "name": "Contact_Type__c",
  "label": "Contact Type",
  "type": "string",
  "control_type": "select",
  "custom": true,               // Custom field
  "optional": true,
  "pick_list": "sobject_field_values_list",
  "sfdc_createable": true,
  "sfdc_updateable": true
}
```

---

## Templates

See `templates/` directory:
- `upsert-contact.json` - Upsert contact with external ID
- `search-contact.json` - Search contact by email
- `update-record.json` - Update record by Salesforce ID

---

## References

- **Base Skill:** `workato-recipes` - Recipe structure, triggers, control flow, formulas
- **Templates:** `templates/` directory
- **Patterns:** `patterns/` directory
- **Salesforce Developer Docs:** https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/
