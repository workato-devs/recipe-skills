# Workato CLI Skills Extension Specification

**Status:** Proposed
**Version:** 0.1.0
**Author:** Zayne Turner
**Date:** January 2026

---

## Overview

This document proposes an extension to the Workato CLI that adds support for Recipe Skills - reusable knowledge bundles that help developers (and AI agents) write production-grade recipes more efficiently.

## Vision

Skills abstract away the complexity of writing connector-specific recipe JSON. A developer who imports the `stripe-recipes` skill gains:

1. **Knowledge** - Patterns, gotchas, and best practices encoded in documentation
2. **Templates** - Validated recipe JSON files to start from
3. **Validation** - Pre-push checks specific to that connector
4. **AI Compatibility** - Documentation formatted for agent consumption

## Proposed Commands

### `workato skills list`

List all available skills (local + registry).

```bash
$ workato skills list

Local Skills:
  stripe-recipes     v1.0.0   Stripe payment integration recipes

Registry Skills:
  salesforce-recipes v1.2.0   Salesforce CRM recipes
  netsuite-recipes   v0.9.0   NetSuite ERP recipes
  zendesk-recipes    v1.0.0   Zendesk support recipes
  slack-recipes      v1.1.0   Slack communication recipes

Use 'workato skills info <skill>' for details.
```

### `workato skills info <skill>`

Get detailed information about a skill.

```bash
$ workato skills info stripe-recipes

stripe-recipes v1.0.0
━━━━━━━━━━━━━━━━━━━━━

Description:
  Stripe payment integration recipes for Workato. Enables AI agents to
  generate valid recipe JSON for customer management, payment processing,
  and refunds.

Author: Workato
License: MIT

Capabilities:
  • Create/search Stripe customers (with deduplication)
  • Create and confirm PaymentIntents
  • Handle 3D Secure authentication
  • Process refunds

Templates:
  • create-customer.json     Search-before-create pattern
  • confirm-payment.json     Payment confirmation with 3D Secure
  • create-refund.json       Refund processing

Patterns:
  • datapill-syntax.md       Stripe-specific datapill rules
  • error-handling.md        Error response flattening
  • idempotency.md           Idempotency header patterns
  • search-before-create.md  Customer deduplication

Use 'workato skills import stripe-recipes' to add to your project.
```

### `workato skills import <skill>`

Import a skill into the current project.

```bash
$ workato skills import stripe-recipes

Importing stripe-recipes v1.0.0...

Created:
  .skills/stripe-recipes/
  ├── skill.yaml
  ├── SKILL_INSTRUCTIONS.md
  ├── templates/
  │   ├── create-customer.json
  │   ├── confirm-payment.json
  │   └── create-refund.json
  └── patterns/
      ├── datapill-syntax.md
      ├── error-handling.md
      ├── idempotency.md
      └── search-before-create.md

✓ Skill imported successfully.

Tip: Use templates as starting points for new recipes.
     Read SKILL_INSTRUCTIONS.md for complete documentation.
```

### `workato skills validate <recipe> --skill <skill>`

Validate a recipe against skill-specific rules.

```bash
$ workato skills validate my-recipe.recipe.json --skill stripe-recipes

Validating my-recipe.recipe.json against stripe-recipes...

✓ Config section includes stripe provider
✓ Idempotency header present on POST action
✓ Datapill paths use correct format (no body wrapper)
✓ All result fields present in error return
✗ Missing extended_output_schema on action at line 45

1 error, 0 warnings

Fix the error and run validation again.
```

### `workato skills generate <skill> --description <desc> --output <file>`

Generate a recipe from natural language description (AI-assisted).

```bash
$ workato skills generate stripe-recipes \
    --description "Search for customer by email, create if not found" \
    --output search-or-create-customer.recipe.json

Generating recipe...

Using patterns:
  • search-before-create
  • idempotency

Created: search-or-create-customer.recipe.json

✓ Recipe generated successfully.

Next steps:
  1. Review the generated recipe
  2. Update connection references
  3. Run 'workato push' to deploy
```

## Skill Package Format

### Directory Structure

```
<skill-name>/
├── skill.yaml              # Manifest (required)
├── SKILL_INSTRUCTIONS.md   # Main documentation (required)
├── templates/              # Recipe templates (optional)
│   └── *.json
├── patterns/               # Pattern documentation (optional)
│   └── *.md
└── validation/             # Validation rules (optional)
    └── rules.yaml
```

### skill.yaml Schema

```yaml
name: string              # Skill identifier (required)
version: string           # Semantic version (required)
description: string       # Short description (required)
author: string            # Author name (required)
license: string           # License identifier (required)

capabilities:             # What the skill enables (required)
  - string

entry_point: string       # Main documentation file (required)

templates:                # Template files (optional)
  - path/to/template.json

patterns:                 # Pattern documentation (optional)
  - path/to/pattern.md

platforms:                # Target platforms (required)
  - workato

tags:                     # Discovery tags (optional)
  - string
```

## Integration with Existing CLI

### Workflow Integration

Skills integrate with existing `workato push/pull` workflow:

```bash
# Import skill for project
workato skills import stripe-recipes

# Create recipe using templates
cp .skills/stripe-recipes/templates/create-customer.json my-customer.recipe.json

# Edit recipe...

# Validate against skill rules
workato skills validate my-customer.recipe.json --skill stripe-recipes

# Push to Workato
workato push
```

### Project Configuration

Add skills to `.workatoenv`:

```
[skills]
stripe-recipes = 1.0.0
salesforce-recipes = 1.2.0
```

## Registry Architecture

### Local Registry

Skills are stored locally in project `.skills/` directory.

### Remote Registry (Future)

A central registry hosted by Workato:

```
https://registry.workato.com/skills/
├── stripe-recipes/
│   ├── 1.0.0/
│   └── 1.1.0/
├── salesforce-recipes/
└── ...
```

Commands would support:

```bash
workato skills search "payment"
workato skills install stripe-recipes@1.0.0
workato skills publish ./my-skill
```

## AI Agent Integration

### Agent-Friendly Format

SKILL_INSTRUCTIONS.md is formatted for AI consumption:
- Clear section headers
- Code examples with annotations
- Common errors with solutions
- Step-by-step workflows

### Claude Code Integration

Skills can be loaded as slash commands:

```
.claude/
└── commands/
    └── stripe-recipes.md  # References skill content
```

User invokes with `/stripe-recipes` to load context.

## Implementation Phases

### Phase 1: Local Skills (Current)

- Manual import of skill packages
- Local validation rules
- Claude Code slash command integration

### Phase 2: CLI Integration

- `workato skills` commands
- Validation integration
- Project configuration

### Phase 3: Registry

- Central skill registry
- Version management
- Publishing workflow

### Phase 4: AI Generation

- `workato skills generate` command
- LLM integration for recipe generation
- Interactive recipe builder

## Security Considerations

### Skill Verification

- Skills from registry are signed by Workato
- Vendor-contributed skills show vendor badge
- Community skills show warning on import

### Code Execution

- Skills contain documentation and templates only
- No executable code in skill packages
- Validation rules are declarative (YAML)

## Success Metrics

- Number of skills published (target: 50+ in first year)
- Skills usage per recipe project
- Time reduction for recipe development
- AI-generated recipe success rate

## Open Questions

1. Should skills be workspace-global or project-local?
2. How to handle skill dependencies?
3. Pricing model for premium skills?
4. Vendor certification program details?

---

## Appendix: Example Validation Rules

```yaml
# validation/rules.yaml

rules:
  - name: stripe-no-body-wrapper
    description: Stripe datapills should not use body wrapper
    pattern: 'path":\["body"'
    provider: stripe
    severity: error
    message: "Stripe datapills don't use body wrapper. Use [\"field\"] not [\"body\", \"field\"]"

  - name: stripe-idempotency-required
    description: Create operations must include idempotency header
    trigger: verb == "post" && provider == "stripe"
    required: headers["Idempotency-Key"]
    severity: error
    message: "POST operations to Stripe require Idempotency-Key header"

  - name: stripe-amount-validation
    description: Payment amounts should be validated
    trigger: path contains "payment_intent" || path contains "charge"
    recommended: if_condition checking amount >= 50
    severity: warning
    message: "Consider validating amount >= 50 (Stripe minimum)"
```
