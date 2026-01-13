# Recipe Skills

A library of reusable integration knowledge for Workato recipes, built by **Workato, vendors, and the community**. Abstract away API complexity and compose enterprise integrations like code.

## What are Recipe Skills?

Recipe Skills encapsulate the complexity of vendor-specific API operations and integration patterns. Under the hood, operations like `Stripe.createCustomer` or `Salesforce.updateAccount` involve hundreds of lines of specialized JSON defining authentication, field mappings, error handling, and API-specific logic. Skills make these patterns learnable and repeatable.

**A skill is NOT:**
- Pre-packaged individual operations
- A code library you import at runtime
- A replacement for the Workato platform

**A skill IS:**
- A knowledge bundle that teaches agents (and humans) how to write recipes
- Documentation, templates, and patterns for a connector domain
- Validated examples you can adapt for your use case

## Available Skills

### Connector-Specific Skills

| Skill | Description | Status |
|-------|-------------|--------|
| [stripe-recipes](skills/stripe-recipes/) | Stripe payment integration recipes | v1.0.0 |
| salesforce-recipes | Salesforce CRM recipes | Planned |
| netsuite-recipes | NetSuite ERP recipes | Planned |

## Quick Start

### For AI Agents (Claude Code)

1. Navigate to this repo directory
2. Invoke the skill: `/stripe-recipes`
3. Ask to generate a recipe: "Create a recipe to search for a Stripe customer by email"

### For Human Developers

1. Read the skill instructions: `skills/stripe-recipes/SKILL_INSTRUCTIONS.md`
2. Copy a template: `skills/stripe-recipes/templates/create-customer.json`
3. Adapt for your use case
4. Deploy: `workato push`

### Proposed CLI (Future)

```bash
# List available skills
workato skills list

# Import a skill to your project
workato skills import stripe-recipes

# Validate recipe against skill rules
workato skills validate my-recipe.json --skill stripe-recipes
```

See [CLI Extension Spec](docs/cli-extension-spec.md) for the full proposal.

## Skill Structure

Each skill follows this structure:

```
skills/<skill-name>/
├── skill.yaml              # Metadata and manifest
├── SKILL_INSTRUCTIONS.md   # Main knowledge document
├── templates/              # Validated recipe templates
│   └── *.json
└── patterns/               # Pattern documentation
    └── *.md
```

## Using with Claude Code

This repo includes a `.claude/commands/` directory with slash commands:

```bash
# In Claude Code, from this repo:
/stripe-recipes

# Then ask:
"Generate a recipe to create a Stripe PaymentIntent"
```

The agent will have full context from the skill to generate valid Workato recipe JSON.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

1. **Improve existing skills** - Fix bugs, add patterns, improve documentation
2. **Add new templates** - Create validated recipes for common operations
3. **Create new skills** - Build skills for connectors you use

### Contribution Models

**Workato-maintained:** Core skills maintained by Workato engineering
**Vendor-contributed:** Skills contributed and maintained by API vendors
**Community-contributed:** Skills from the developer community

## Documentation

- [CLI Extension Spec](docs/cli-extension-spec.md) - Proposed Workato CLI integration
- [stripe-recipes Instructions](skills/stripe-recipes/SKILL_INSTRUCTIONS.md) - Full Stripe skill documentation

## Roadmap

### Current (v0.1)
- [x] stripe-recipes skill with templates and patterns
- [x] Claude Code slash command integration
- [x] CLI extension specification

### Next
- [ ] salesforce-recipes skill
- [ ] Workato CLI integration (pending platform support)
- [ ] Skill validation rules

### Future
- [ ] Central skill registry
- [ ] AI-assisted recipe generation
- [ ] Vendor contribution program

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues:** [GitHub Issues](https://github.com/workato/recipe-skills/issues)
- **Discussions:** [GitHub Discussions](https://github.com/workato/recipe-skills/discussions)

---

Built with insights from the [Dewy Resort Hotel Demo](https://github.com/workato-devs/demo-workato-dewy-resort-hotel) project.
