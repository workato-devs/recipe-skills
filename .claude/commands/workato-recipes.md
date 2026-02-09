# Workato Recipes Base Skill

You are now equipped with foundational knowledge for writing Workato recipe JSON. This skill covers platform fundamentals that apply to ALL connector recipes.

## CRITICAL WARNING: extended_input_schema

**The `extended_input_schema` MUST fully define ALL fields in the action's `input` object, including nested objects.** If any input field is missing from the schema, Workato will **silently drop that data** during execution, causing cascading failures.

This affects ALL connectors. Complex connectors (Salesforce, NetSuite, etc.) are particularly vulnerable.

**Always verify:** Every field in `input` has a matching entry in `extended_input_schema`, including nested objects.

## Capabilities

With this skill loaded, you can:
- Generate recipes with different trigger types (API endpoint, callable recipe)
- Structure control flow (if/else, try/catch)
- Write correct datapill references
- Configure recipe settings and connections

## Trigger Types

### API Endpoint (External HTTP access)
```json
{
  "provider": "workato_api_platform",
  "name": "receive_request",
  "keyword": "trigger"
}
```
Use `response_index` to return different HTTP status codes.

### Callable Recipe (Internal recipe calls)
```json
{
  "provider": "workato_recipe_function",
  "name": "execute",
  "keyword": "trigger"
}
```
Use `return_result` to return values.

## Quick Reference

### Datapill Format
```
#{_dp('{\"pill_type\":\"output\",\"provider\":\"PROVIDER\",\"line\":\"STEP_ALIAS\",\"path\":[\"field\"]}')}"
```

### If/Else (else is INSIDE if block)
```json
{
  "keyword": "if",
  "block": [
    { /* true action */ },
    { "keyword": "else", "block": [{ /* false action */ }] }
  ]
}
```

### Try/Catch (catch is INSIDE try block)
```json
{
  "keyword": "try",
  "block": [
    { /* action */ },
    { "keyword": "catch", "provider": null, "block": [{ /* error handling */ }] }
  ]
}
```

### Block Requirements
- Every block needs: `number`, `keyword`, `uuid`, `as`
- Actions need: `provider`
- If/else: NO provider
- Catch: `"provider": null`

## Reference Files

- `skills/workato-recipes/SKILL_INSTRUCTIONS.md` - Full documentation
- `skills/workato-recipes/triggers/` - Trigger type details
- `skills/workato-recipes/templates/` - Starter templates
- `skills/workato-recipes/validation-checklist.md` - Base validation checklist

## Usage

Ask to generate a recipe with a specific trigger type:
- "Create an API endpoint recipe that echoes the input"
- "Create a callable recipe that validates an email"
