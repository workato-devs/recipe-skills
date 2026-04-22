# Stripe Recipes Skill

> **⚠️ DEPENDENCY: Run `/workato-recipes` first if not already loaded.**
> This skill requires the base Workato knowledge for triggers, control flow, datapills, and recipe structure.

You are now equipped with Stripe-specific knowledge for writing Workato recipes. This skill extends the **workato-recipes** base skill and focuses on Stripe-specific patterns.

## Capabilities

With this skill loaded, you can:
- Create recipes for Stripe customer management (search, create, update)
- Create recipes for payment processing (PaymentIntents, confirmations)
- Create recipes for refund processing
- Create recipes for subscription management
- Handle 3D Secure authentication flows

## Trigger Type Selection

Ask the user which trigger type they need:
- **API Endpoint** (`workato_api_platform`) - External HTTP access
- **Callable Recipe** (`workato_recipe_function`) - Internal recipe calls

See `workato-recipes` skill for trigger implementation details.

## Stripe-Specific Knowledge

### extended_input_schema (CRITICAL)

Custom HTTP actions have nested `input.data` structures. **You MUST copy the complete `extended_input_schema` from validated templates.** Simplified schemas will cause input data to be silently dropped.

See `workato-recipes` base skill for full documentation.

### Datapill Exception (CRITICAL)

**Stripe does NOT use the `["body"]` wrapper** in datapill paths:

```json
// CORRECT for Stripe
"path": ["id"]
"path": ["data", {"path_element_type":"current_item"}, "id"]

// WRONG - Do NOT use for Stripe
"path": ["body", "id"]
```

### Custom HTTP Actions Required

Workato's Stripe connector lacks modern endpoints. Use `__adhoc_http_action`:
- `/v1/customers/search`
- `/v1/payment_intents`
- `/v1/payment_intents/{id}/confirm`
- `/v1/refunds`

### Idempotency Required

All create/confirm operations MUST include `Idempotency-Key` header.

### Search-Before-Create Pattern

When creating customers, always search first to prevent duplicates.

## Reference Files

- `skills/workato-recipes/SKILL.md` - Base platform knowledge
- `skills/stripe-recipes/SKILL.md` - Stripe-specific knowledge
- `skills/stripe-recipes/templates/` - Validated recipe templates

## Usage

When asked to create a Stripe recipe:

1. **Ask about trigger type** - API endpoint or callable recipe?
2. **Identify the Stripe operation** - search, create, confirm, refund
3. **Apply Stripe patterns** - idempotency, search-before-create, error flattening
4. **Generate valid JSON** using base skill structure + Stripe specifics

## Example Prompts

- "Create an API endpoint recipe that searches for a Stripe customer by email"
- "Create a callable recipe to process a Stripe refund"
