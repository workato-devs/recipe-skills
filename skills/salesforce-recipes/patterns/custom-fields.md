# Custom Fields and Objects Pattern

## Overview

Salesforce allows organizations to create custom objects and fields specific to their business needs. These customizations are NOT standard across all Salesforce orgs and require special handling when generating recipes.

## CRITICAL: Custom vs Standard

### Standard SObjects and Fields

**Available in ALL Salesforce orgs:**

| SObject | Standard Fields |
|---------|----------------|
| Contact | Id, FirstName, LastName, Email, Phone, AccountId |
| Account | Id, Name, Phone, BillingAddress, OwnerId |
| Lead | Id, FirstName, LastName, Email, Company, Status |
| Opportunity | Id, Name, StageName, CloseDate, Amount, AccountId |
| Case | Id, Subject, Status, Priority, ContactId |

### Custom Objects and Fields

**Specific to each implementation:**

| Suffix | Type | Example | Standard? |
|--------|------|---------|-----------|
| `__c` | Custom Object/Field | `Booking__c`, `Status__c` | ❌ NO |
| `__mdt` | Custom Metadata Type | `Config__mdt` | ❌ NO |
| `__e` | Platform Event | `Order_Event__e` | ❌ NO |
| `__x` | External Object | `SAP_Account__x` | ❌ NO |
| (none) | Standard | `Contact`, `Email` | ✅ YES |

## Agent Requirements

### When You See Custom Suffixes

If a recipe requires objects/fields with `__c`, `__mdt`, `__e`, or `__x`:

1. **Document the requirement**
2. **Warn the user**
3. **Never assume it exists**
4. **Prefer standard alternatives when possible**

### Documentation Pattern

```json
{
  "name": "Upsert contact with loyalty program",
  "description": "REQUIRES: Contact.Loyalty_Number__c (custom text field), Contact.Contact_Type__c (custom picklist)",
  ...
}
```

## Working with Custom Fields

### Example: Custom Text Field

```json
{
  "provider": "salesforce",
  "name": "upsert_sobject",
  "input": {
    "sobject_name": "Contact",
    "FirstName": "#{first_name}",      // Standard field
    "LastName": "#{last_name}",        // Standard field
    "Loyalty_Number__c": "#{loyalty}"  // CUSTOM field - not in all orgs
  }
}
```

### Example: Custom Picklist Field

```json
{
  "provider": "salesforce",
  "name": "upsert_sobject",
  "input": {
    "sobject_name": "Contact",
    "LastName": "#{last_name}",
    "Contact_Type__c": "Guest"  // CUSTOM picklist - not in all orgs
  }
}
```

**Note:** Picklist values are case-sensitive and must match Salesforce configuration.

### Example: Custom Object

```json
{
  "provider": "salesforce",
  "name": "upsert_sobject",
  "input": {
    "sobject_name": "Booking__c",          // CUSTOM object - not in all orgs
    "External_ID__c": "#{booking_id}",     // CUSTOM field
    "Status__c": "Confirmed",              // CUSTOM picklist
    "Check_In_Date__c": "#{checkin}",      // CUSTOM date field
    "Primary_Guest__c": "#{contact_id}",   // CUSTOM lookup to Contact
    "Room__c": "#{room_id}"                // CUSTOM lookup to Room__c
  }
}
```

## Schema Metadata for Custom Fields

Custom fields include metadata in `extended_input_schema`:

```json
{
  "name": "Contact_Type__c",
  "label": "Contact Type",
  "type": "string",
  "control_type": "select",
  "custom": true,                    // Indicates custom field
  "optional": true,
  "pick_list": "sobject_field_values_list",
  "sfdc_createable": true,
  "sfdc_updateable": true
}
```

**Key indicator:** `"custom": true`

## Custom Metadata Types (`__mdt`)

Custom Metadata Types store application configuration.

### Example: Reading Configuration

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "App_Config__mdt",  // CUSTOM metadata type
    "DeveloperName": "Default_Settings"
  }
}
```

**Use case:** Storing API keys, feature flags, business rules

## Platform Events (`__e`)

Platform events enable event-driven architecture.

### Example: Publishing Event

```json
{
  "provider": "salesforce",
  "name": "create_sobject",
  "input": {
    "sobject_name": "Order_Event__e",  // CUSTOM platform event
    "Order_ID__c": "#{order_id}",
    "Status__c": "Shipped"
  }
}
```

**Use case:** Real-time integration, asynchronous processing

## External Objects (`__x`)

External objects reference data stored outside Salesforce.

### Example: Querying External Data

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "SAP_Account__x",  // CUSTOM external object
    "AccountNumber__c": "#{account_num}"
  }
}
```

**Use case:** Accessing ERP, legacy systems without data duplication

## Best Practices

### 1. Document Custom Requirements

At the top of recipes using custom objects/fields:

```json
{
  "name": "Process hotel booking",
  "description": "Manages booking lifecycle. REQUIRES CUSTOM OBJECTS: Booking__c, Room__c. REQUIRES CUSTOM FIELDS: Contact.Loyalty_Number__c",
  ...
}
```

### 2. Prefer Standard Objects

```json
// BETTER - Uses standard Contact object
{
  "sobject_name": "Contact",
  "FirstName": "#{first_name}",
  "LastName": "#{last_name}"
}

// AVOID - Custom object that may not exist
{
  "sobject_name": "Guest__c",
  "First_Name__c": "#{first_name}",
  "Last_Name__c": "#{last_name}"
}
```

### 3. Ask About Custom Fields

When user requests features that might need custom fields:

**User:** "Track customer loyalty tier"

**Agent:** "To track loyalty tiers, does your Salesforce org have a custom field on Contact for this? For example, `Loyalty_Tier__c`? Or should I use a standard field?"

### 4. Validate Field API Names

Custom field API names must match exactly:
- ✅ `Contact_Type__c`
- ❌ `ContactType__c`
- ❌ `Contact_Type`

## Schema Definition for Custom Fields

### Text Field

```json
{
  "control_type": "text",
  "custom": true,
  "label": "Loyalty Number",
  "name": "Loyalty_Number__c",
  "optional": true,
  "type": "string",
  "sfdc_createable": true,
  "sfdc_updateable": true
}
```

### Picklist Field

```json
{
  "control_type": "select",
  "custom": true,
  "label": "Contact Type",
  "name": "Contact_Type__c",
  "optional": true,
  "pick_list": "sobject_field_values_list",
  "pick_list_params": {
    "sobject_name": "\"Contact\"",
    "field_name": "\"Contact_Type__c\""
  },
  "toggle_field": {
    "control_type": "text",
    "label": "Contact Type",
    "toggle_hint": "Enter custom value",
    "optional": true,
    "custom": true,
    "type": "string",
    "name": "Contact_Type__c"
  },
  "toggle_hint": "Select from list",
  "type": "string",
  "sfdc_createable": true,
  "sfdc_updateable": true
}
```

### Date Field

```json
{
  "control_type": "date",
  "custom": true,
  "label": "Check-In Date",
  "name": "Check_In_Date__c",
  "optional": true,
  "parse_output": "parse_iso8601_date",
  "type": "date_time",
  "render_input": "render_iso8601_date",
  "sfdc_createable": true,
  "sfdc_updateable": true
}
```

### Lookup/Relationship Field

```json
{
  "control_type": "text",
  "custom": true,
  "label": "Primary Guest",
  "name": "Primary_Guest__c",
  "optional": true,
  "type": "string",
  "sfdc_createable": true,
  "sfdc_updateable": true
}
```

**Note:** Lookup fields store the 18-character Salesforce ID of the related record.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "No such column" | Field doesn't exist in org | Verify field exists and API name is correct |
| "Invalid field" | Wrong API name | Check for `__c` suffix, verify spelling |
| "Bad value for restricted picklist" | Invalid picklist value | Use exact picklist value from Salesforce |
| "Object type not supported" | Custom object not deployed | Verify object exists in target org |

## Portability Checklist

Before sharing a recipe that uses custom objects/fields:

- [ ] Document all custom objects used
- [ ] Document all custom fields used
- [ ] Specify required picklist values
- [ ] Note any external ID fields required
- [ ] Warn users about org-specific requirements
- [ ] Provide fallback to standard objects if possible

## Related Patterns

- See `upsert-with-external-id.md` for using custom External ID fields
- See `search-sobjects.md` for querying custom objects
- See SKILL_INSTRUCTIONS.md for complete list of suffixes
