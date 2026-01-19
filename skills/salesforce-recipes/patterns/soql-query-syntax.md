# SOQL Query Syntax Pattern

## Overview

When using `search_sobjects` with the `query` parameter for complex SOQL queries, the syntax for embedding datapills differs from standard SOQL bind variables. This pattern documents the correct syntax to avoid common failures.

## CRITICAL: No Bind Variables

Workato's Salesforce connector does **NOT** support SOQL bind variable syntax (`:variable`). This is a common source of bugs when developers familiar with Apex try to use the same patterns in Workato.

## When to Use

- Complex queries with multiple conditions
- Queries using `IN`, `NOT IN`, `LIKE` operators
- Date range queries
- Queries with relationship traversal (e.g., `Room__r.Room_Number__c`)
- Queries that need `OR` logic (not supported by simple field matching)

## Basic Pattern

### String Values (MUST wrap in single quotes)

**WRONG (bind variable syntax - WILL NOT WORK):**
```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "Contact",
    "query": "Email = :#{_dp('{...email...}')}"
  }
}
```

**CORRECT (string interpolation with single quotes):**
```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "Contact",
    "query": "Email = '#{_dp('{\"pill_type\":\"output\",\"provider\":\"workato_recipe_function\",\"line\":\"trigger\",\"path\":[\"parameters\",\"email\"]}')}'"
  }
}
```

### Date/Number Values (NO quotes)

**CORRECT (dates - no quotes):**
```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "Booking__c",
    "query": "Check_In_Date__c <= #{_dp('{...checkout_date...}')} AND Check_Out_Date__c >= #{_dp('{...checkin_date...}')}"
  }
}
```

**CORRECT (numbers - no quotes):**
```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "input": {
    "sobject_name": "Opportunity",
    "query": "Amount > #{_dp('{...minimum_amount...}')}"
  }
}
```

## Syntax Quick Reference

| Value Type | Syntax | Example |
|------------|--------|---------|
| String | `'#{datapill}'` | `Email = '#{_dp(...)}'` |
| Date | `#{datapill}` | `CreatedDate >= #{_dp(...)}` |
| DateTime | `#{datapill}` | `LastModifiedDate > #{_dp(...)}` |
| Number | `#{datapill}` | `Amount > #{_dp(...)}` |
| Boolean | `#{datapill}` | `IsActive = #{_dp(...)}` |
| Picklist | `'#{datapill}'` | `Status = '#{_dp(...)}'` |
| ID | `'#{datapill}'` | `AccountId = '#{_dp(...)}'` |

## Complex Query Examples

### Multi-Condition Query

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "search_bookings",
  "input": {
    "sobject_name": "Booking__c",
    "query": "Room__r.Room_Number__c = '#{_dp('{...room_number...}')}' AND Status__c NOT IN ('Cancelled', 'No Show', 'Checked Out') AND Check_In_Date__c <= #{_dp('{...checkout_date...}')} AND Check_Out_Date__c >= #{_dp('{...checkin_date...}')}"
  }
}
```

### Date Range Query

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "search_recent_cases",
  "input": {
    "sobject_name": "Case",
    "query": "CreatedDate >= #{_dp('{...start_date...}')} AND CreatedDate <= #{_dp('{...end_date...}')} AND Status != 'Closed'"
  }
}
```

### Query with OR Logic

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "search_contacts",
  "input": {
    "sobject_name": "Contact",
    "query": "Email = '#{_dp('{...email...')}' OR Phone = '#{_dp('{...phone...')}'"
  }
}
```

### Query with IN Operator

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "search_active_bookings",
  "input": {
    "sobject_name": "Booking__c",
    "query": "Status__c IN ('Reserved', 'Checked In', 'Confirmed')"
  }
}
```

### Query with NOT IN Operator

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "search_valid_bookings",
  "input": {
    "sobject_name": "Booking__c",
    "query": "Status__c NOT IN ('Cancelled', 'No Show', 'Checked Out')"
  }
}
```

### Query with Relationship Traversal

```json
{
  "provider": "salesforce",
  "name": "search_sobjects",
  "as": "search_room_bookings",
  "input": {
    "sobject_name": "Booking__c",
    "query": "Room__r.Room_Number__c = '#{_dp('{...room_number...}')}' AND Primary_Guest__r.Email = '#{_dp('{...guest_email...')}'"
  }
}
```

## Common Mistakes and Fixes

### Mistake 1: Using Bind Variable Syntax

**WRONG:**
```json
"query": "Email = :#{_dp('...')}"
"query": "Room_Number__c = :#{_dp('...')}"
```

**FIX:**
```json
"query": "Email = '#{_dp('...')}'"
"query": "Room_Number__c = '#{_dp('...')}'"
```

### Mistake 2: Missing Single Quotes for Strings

**WRONG:**
```json
"query": "Email = #{_dp('...')}"  // Missing quotes
```

**FIX:**
```json
"query": "Email = '#{_dp('...')}'"  // Single quotes added
```

### Mistake 3: Using Quotes for Dates/Numbers

**WRONG:**
```json
"query": "Check_In_Date__c = '#{_dp('...')}'"  // Dates don't need quotes
"query": "Amount > '#{_dp('...')}'"  // Numbers don't need quotes
```

**FIX:**
```json
"query": "Check_In_Date__c = #{_dp('...')}"  // No quotes for dates
"query": "Amount > #{_dp('...')}"  // No quotes for numbers
```

### Mistake 4: Incorrect Escaping in Query String

**WRONG (double quotes inside JSON string):**
```json
"query": "Email = "test@example.com""  // Breaks JSON
```

**FIX (use single quotes for SOQL literals):**
```json
"query": "Email = 'test@example.com'"  // Single quotes in SOQL
```

## Debugging Tips

### Query Returns No Results

1. Check if you're using bind variable syntax (`:#{...}`)
2. Verify string values are wrapped in single quotes
3. Check field API names are correct
4. Verify relationship field syntax (e.g., `Room__r.Field__c`)

### Query Fails with Error

1. Check JSON string escaping
2. Verify all datapills are correctly formatted
3. Check for mismatched quotes
4. Verify SOQL syntax (use Salesforce Developer Console to test query)

### Test Query Structure

To verify your SOQL query structure, test it in Salesforce Developer Console first:

```sql
SELECT Id, Email FROM Contact WHERE Email = 'test@example.com'
```

Then translate to Workato format:

```json
"query": "Email = '#{_dp('{...email...')}'"
```

## Best Practices

### 1. Always Single-Quote String Values

```json
// Picklists, strings, IDs - all need single quotes
"query": "Status = '#{status}' AND Email = '#{email}' AND AccountId = '#{account_id}'"
```

### 2. Never Quote Dates or Numbers

```json
// Dates and numbers - no quotes
"query": "Amount > #{amount} AND CreatedDate >= #{start_date}"
```

### 3. Test Queries with Static Values First

Before adding datapills, test with static values:

```json
// Step 1: Test with static value
"query": "Email = 'test@example.com'"

// Step 2: Replace with datapill
"query": "Email = '#{_dp('{...email...')}'"
```

### 4. Use NOT IN for Exclusions

```json
// Exclude multiple statuses
"query": "Status__c NOT IN ('Cancelled', 'No Show', 'Checked Out')"
```

## Related Patterns

- See `search-sobjects.md` for basic search without SOQL query
- See `custom-fields.md` for working with custom objects in queries
- See base skill for datapill syntax reference
