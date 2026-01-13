# Upsert with External ID Pattern

## Overview

Upserting creates a new record if it doesn't exist, or updates an existing record if found. Salesforce uses External ID fields to determine whether a record already exists.

## When to Use

- Creating or updating records without knowing if they already exist
- Syncing data from external systems
- Avoiding duplicate records
- Idempotent operations (safe to retry)

## External ID Fields

### What Qualifies as an External ID

1. **Fields marked as External ID in Salesforce**
   - Custom fields with External ID checkbox enabled
   - Example: `Unique_Email__c`, `External_System_ID__c`

2. **Standard unique fields**
   - `Id` - Salesforce record ID
   - `Email` - For Contact (not marked as External ID, but can be used)

### User Must Specify the Field

**IMPORTANT:** Always ask the user which field to use as the external ID. Do not assume.

Example questions:
- "Which field should I use to match existing contacts?"
- "Do you have an External ID field set up for this object?"
- "Should I use Email, or do you have a custom External ID field?"

## Pattern Structure

```json
{
  "provider": "salesforce",
  "name": "upsert_sobject",
  "as": "upsert_contact",
  "input": {
    "sobject_name": "Contact",
    "query_field": {
      "primary_key": "Unique_Email__c"  // USER-SPECIFIED FIELD
    },
    "Unique_Email__c": "#{external_id_value}",
    "FirstName": "#{first_name}",
    "LastName": "#{last_name}"
  }
}
```

### Key Components

| Field | Required | Description |
|-------|----------|-------------|
| `sobject_name` | Yes | SObject API name |
| `query_field.primary_key` | Yes | External ID field name (user-specified) |
| External ID field value | Yes | Must set the external ID field in input |
| Other fields | As needed | Fields to create/update |

## Examples

### Example 1: Upsert Contact with Email

```json
{
  "provider": "salesforce",
  "name": "upsert_sobject",
  "as": "upsert_contact",
  "input": {
    "sobject_name": "Contact",
    "query_field": {
      "primary_key": "Email"
    },
    "Email": "#{_dp('{...email...}')}",
    "FirstName": "#{_dp('{...first_name...}')}",
    "LastName": "#{_dp('{...last_name...}')}",
    "Phone": "#{_dp('{...phone...}')}"
  }
}
```

### Example 2: Upsert with Custom External ID

**Scenario:** User has a custom field `External_System_ID__c` marked as External ID.

```json
{
  "provider": "salesforce",
  "name": "upsert_sobject",
  "as": "upsert_account",
  "input": {
    "sobject_name": "Account",
    "query_field": {
      "primary_key": "External_System_ID__c"
    },
    "External_System_ID__c": "#{_dp('{...external_id...}')}",
    "Name": "#{_dp('{...account_name...}')}",
    "BillingCity": "#{_dp('{...city...}')}"
  }
}
```

### Example 3: Conditional Field Updates

Only update fields when values are present:

```json
{
  "provider": "salesforce",
  "name": "upsert_sobject",
  "as": "upsert_contact",
  "input": {
    "sobject_name": "Contact",
    "query_field": {
      "primary_key": "Email"
    },
    "Email": "#{_dp('{...email...}')}",
    "FirstName": "=_dp('{...first_name...}').present? ? _dp('{...first_name...}') : skip",
    "LastName": "#{_dp('{...last_name...}')}",
    "Phone": "=_dp('{...phone...}').present? ? _dp('{...phone...}') : skip"
  }
}
```

## Common Patterns

### Pattern: Deduplicate on Email

```json
"query_field": {
  "primary_key": "Email"
},
"Email": "#{email}"
```

### Pattern: Use Custom External ID

```json
"query_field": {
  "primary_key": "Unique_Email__c"
},
"Unique_Email__c": "#{email}",
"Email": "#{email}"
```

**Note:** Set both the external ID field AND the standard Email field.

### Pattern: Sync from External System

```json
"query_field": {
  "primary_key": "CRM_Contact_ID__c"
},
"CRM_Contact_ID__c": "#{external_system_id}",
"FirstName": "#{first_name}",
"LastName": "#{last_name}"
```

## Best Practices

### 1. Always Set the External ID Field

```json
// CORRECT
"query_field": {
  "primary_key": "Email"
},
"Email": "#{email}",  // Field is set
"FirstName": "#{first_name}"

// WRONG - Missing external ID field in input
"query_field": {
  "primary_key": "Email"
},
"FirstName": "#{first_name}"  // Email not set!
```

### 2. Use Conditional Updates for Optional Fields

Prevent overwriting existing data with blanks:

```json
"FirstName": "=_dp('{...}').present? ? _dp('{...}') : skip"
```

### 3. Verify External ID Configuration

Before using a custom field as external ID:
- Confirm the field exists in the target Salesforce org
- Verify the field is marked as "External ID"
- Test with sample data

### 4. Handle Required Fields

Salesforce required fields must be included:
- Contact: `LastName` (required)
- Account: `Name` (required)
- Opportunity: `Name`, `StageName`, `CloseDate` (required)

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid external ID field" | Field not marked as External ID | Verify field has External ID checkbox in Salesforce |
| "Required field missing" | Missing required field on create | Include all required fields (e.g., LastName for Contact) |
| "Duplicate value" | Field value violates unique constraint | Check for duplicate external ID values |
| "Field does not exist" | Custom field not in org | Verify field API name and deployment to org |

## Datapill Pattern

Access upserted record ID:

```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"upsert_contact\",\"path\":[\"id\"]}')}"
```

## Related Patterns

- See `custom-fields.md` for working with custom fields
- See `search-sobjects.md` for finding existing records before upserting
- See base skill `workato-recipes` for conditional formula syntax
