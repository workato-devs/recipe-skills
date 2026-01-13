# Search SObjects Pattern

## Overview

The `search_sobjects` action finds Salesforce records matching field criteria. This is the primary method for querying records by field values.

## When to Use

- Find records by email, name, or other fields
- Check if a record exists before creating
- Retrieve related records
- Look up records for subsequent operations

## Basic Pattern

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "search_contact",
  "input": {
    "sobject_name": "Contact",
    "limit": "150",
    "Email": "#{email}"
  }
}
```

### Key Fields

| Field | Required | Description |
|-------|----------|-------------|
| `sobject_name` | Yes | SObject API name to search |
| `limit` | No | Max records to return (default: 150) |
| Search fields | Yes | Field names with values to match |

## Search Criteria

### Single Field Search

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "Contact",
    "Email": "#{email}"
  }
}
```

### Multiple Field Search (AND logic)

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "Contact",
    "FirstName": "#{first_name}",
    "LastName": "#{last_name}",
    "AccountId": "#{account_id}"
  }
}
```

**Note:** Multiple criteria are combined with AND logic.

### Custom Field Search

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "Contact",
    "Unique_Email__c": "#{email}",
    "Contact_Type__c": "Guest"
  }
}
```

## Output Structure

Search results return an array of matching records:

```json
{
  "Contact": [
    {
      "Id": "0031234567890ABC",
      "Email": "john@example.com",
      "FirstName": "John",
      "LastName": "Doe"
    }
  ]
}
```

### Accessing Search Results

**First matching record:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_contact\",\"path\":[\"Contact\",{\"path_element_type\":\"current_item\"},\"Id\"]}')}"
```

**Specific field from first result:**
```json
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_contact\",\"path\":[\"Contact\",{\"path_element_type\":\"current_item\"},\"Email\"]}')}"
```

## Common Patterns

### Pattern 1: Search and Check if Found

```json
// Step 1: Search
{
  "number": 2,
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
  "number": 3,
  "keyword": "if",
  "input": {
    "conditions": [{
      "operand": "present",
      "lhs": "#{_dp('{...search_contact...Contact[].Id...}')}"
    }]
  },
  "block": [
    // Record found - use it
  ]
}
```

### Pattern 2: Search with Result Branching

```json
{
  "keyword": "if",
  "input": {
    "conditions": [{
      "operand": "present",
      "lhs": "#{search_contact.Contact[].Id}"
    }]
  },
  "block": [
    {
      // Found - return existing record
      "provider": "workato_recipe_function",
      "name": "return_result",
      "input": {
        "result": {
          "id": "#{search_contact.Contact[].Id}",
          "found": "true"
        }
      }
    },
    {
      "keyword": "else",
      "block": [
        {
          // Not found - return not found
          "provider": "workato_recipe_function",
          "name": "return_result",
          "input": {
            "result": {
              "id": "=null",
              "found": "false"
            }
          }
        }
      ]
    }
  ]
}
```

### Pattern 3: Search Before Update

```json
// Step 1: Search for record
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "find_contact",
  "input": {
    "sobject_name": "Contact",
    "Email": "#{email}"
  }
}

// Step 2: Update if found
{
  "keyword": "if",
  "input": {
    "conditions": [{
      "operand": "present",
      "lhs": "#{find_contact.Contact[].Id}"
    }]
  },
  "block": [
    {
      "provider": "salesforce",
      "name": "update_sobject",
      "input": {
        "sobject_name": "Contact",
        "id": "#{find_contact.Contact[].Id}",
        "Phone": "#{new_phone}"
      }
    }
  ]
}
```

### Pattern 4: Search with Limit

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "Opportunity",
    "limit": "10",
    "AccountId": "#{account_id}",
    "StageName": "Closed Won"
  }
}
```

## Extended Output Schema

Define which fields to return from search:

```json
"extended_output_schema": [
  {
    "label": "Contacts",
    "name": "Contact",
    "of": "object",
    "properties": [
      {
        "control_type": "text",
        "label": "Contact ID",
        "name": "Id",
        "optional": true,
        "custom": false,
        "type": "string"
      },
      {
        "control_type": "text",
        "label": "Email",
        "name": "Email",
        "optional": true,
        "custom": false,
        "type": "string"
      },
      {
        "control_type": "text",
        "label": "First Name",
        "name": "FirstName",
        "optional": true,
        "custom": false,
        "type": "string"
      }
    ],
    "type": "array"
  }
]
```

## Search by Related Object

### Searching with Lookup Field

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "Contact",
    "AccountId": "#{account_id}"  // Lookup to Account
  }
}
```

### Accessing Related Data

```json
// Contact with Account relationship
"#{_dp('{\"pill_type\":\"output\",\"provider\":\"salesforce\",\"line\":\"search_contact\",\"path\":[\"Contact\",{\"path_element_type\":\"current_item\"},\"Account\",\"Name\"]}')}"
```

## Searching Custom Objects

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "Booking__c",  // CUSTOM object
    "Primary_Guest__c": "#{contact_id}",
    "Status__c": "Confirmed"
  }
}
```

**Remember:** Custom objects (`__c`) are implementation-specific.

## Performance Considerations

### Limit Results

Always specify a reasonable limit:

```json
"limit": "150"  // Default
"limit": "10"   // For single record lookups
"limit": "1000" // Max for most operations
```

### Index Fields

Search performance is best on indexed fields:
- Id (always indexed)
- External ID fields (indexed)
- Unique fields (indexed)
- Standard name fields (often indexed)

### Non-Indexed Fields

Searches on non-indexed custom fields may be slower:

```json
// May be slower
{
  "sobject_name": "Contact",
  "Custom_Notes__c": "VIP customer"  // Non-indexed text field
}
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "No such column" | Field doesn't exist | Verify field API name |
| "Object not supported" | Invalid SObject name | Check SObject API name (e.g., Contact not Contacts) |
| "Search query timed out" | Too many results | Add limit, use indexed fields |
| "Cannot search on field" | Field not searchable | Use different field or SOQL query |

## Best Practices

### 1. Check for Results

Always check if search returned results:

```json
{
  "keyword": "if",
  "input": {
    "conditions": [{
      "operand": "present",
      "lhs": "#{search_results.Contact[].Id}"
    }]
  }
}
```

### 2. Use Specific Criteria

```json
// BETTER - More specific
{
  "sobject_name": "Contact",
  "Email": "#{email}",
  "AccountId": "#{account_id}"
}

// WORSE - Too broad
{
  "sobject_name": "Contact",
  "LastName": "Smith"  // May return many results
}
```

### 3. Set Appropriate Limits

```json
// Looking for one record
"limit": "1"

// Looking for recent records
"limit": "50"

// Need many records
"limit": "1000"  // Max
```

### 4. Handle No Results

Always provide a path for when no results are found:

```json
{
  "keyword": "if",
  "input": {
    "conditions": [{
      "operand": "present",
      "lhs": "#{search.Contact[].Id}"
    }]
  },
  "block": [
    { /* Found */ },
    {
      "keyword": "else",
      "block": [
        { /* Not found - handle this case */ }
      ]
    }
  ]
}
```

## Limitations

- Default limit: 150 records
- Maximum limit: Varies by Salesforce edition
- No OR logic (only AND between criteria)
- For complex queries, consider SOQL via custom HTTP action

## Related Patterns

- See `upsert-with-external-id.md` for search-and-upsert pattern
- See `custom-fields.md` for searching custom objects
- See base skill for if/else control flow
