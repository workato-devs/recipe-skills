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

### Base Skill

| Skill | Description | Status |
|-------|-------------|--------|
| [workato-recipes](skills/workato-recipes/) | Core Workato recipe fundamentals (triggers, control flow, datapills) | v1.0.0 |

### Connector-Specific Skills

| Skill | Description | Status |
|-------|-------------|--------|
| [salesforce-recipes](skills/salesforce-recipes/) | Salesforce CRM recipes (standard & custom objects) | v1.0.0 |
| [stripe-recipes](skills/stripe-recipes/) | Stripe payment integration recipes | v1.0.0 |

## Quick Start

### For AI Agents (Claude Code)

1. Navigate to this repo directory
2. Invoke a skill:
   - `/workato-recipes` - Learn recipe fundamentals and trigger types
   - `/stripe-recipes` - Generate Stripe payment integration recipes
   - `/salesforce-recipes` - Generate Salesforce CRM recipes
3. Ask to generate a recipe:
   - "Create an API endpoint recipe that accepts customer data"
   - "Create a recipe to search for a Stripe customer by email"
   - "Create a recipe to upsert a Salesforce Contact by external ID"

### For Human Developers

Skills are designed for AI agents to generate recipes. As a human developer:

1. Use Claude Code (or another AI agent) with the appropriate skill to generate recipes
2. Review and test the generated recipe JSON
3. Deploy: `workato push`

For reference and learning, you can browse:
- Skill documentation: `skills/{skill-name}/SKILL_INSTRUCTIONS.md`
- Example templates: `skills/{skill-name}/templates/*.json`
- Generated examples: `test-deploy/`

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
/workato-recipes   # Learn recipe structure and triggers
/stripe-recipes    # Generate Stripe recipes
/salesforce-recipes # Generate Salesforce recipes

# Examples:
"Generate a recipe with an API endpoint trigger"
"Create a recipe to create a Stripe PaymentIntent"
"Create a recipe to search and update Salesforce Accounts"
```

The agent will have full context from the skill to generate valid Workato recipe JSON. See `test-deploy/` for example generated recipes.

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

### Skills
- [workato-recipes Instructions](skills/workato-recipes/SKILL_INSTRUCTIONS.md) - Recipe fundamentals and base patterns
- [stripe-recipes Instructions](skills/stripe-recipes/SKILL_INSTRUCTIONS.md) - Stripe payment integration patterns
- [salesforce-recipes Instructions](skills/salesforce-recipes/SKILL_INSTRUCTIONS.md) - Salesforce CRM integration patterns

### Project Documentation
- [CLI Extension Spec](docs/cli-extension-spec.md) - Proposed Workato CLI integration
- [test-deploy/](test-deploy/) - Example generated recipes

## Roadmap

### Completed (v1.0)
- [x] workato-recipes base skill (triggers, control flow, fundamentals)
- [x] stripe-recipes skill with templates and patterns
- [x] salesforce-recipes skill with SObject operations
- [x] Claude Code slash command integration
- [x] CLI extension specification
- [x] Example recipes in test-deploy/

### Next
- [ ] Expand connector skill coverage
- [ ] Community and vendor contribution guidelines and templates
- [ ] Workato CLI integration (pending platform support)
- [ ] Skill validation rules

### Future
- [ ] Central skill registry
- [ ] Vendor contribution program
- [ ] CI/CD recipe validation

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues:** [GitHub Issues](https://github.com/workato/recipe-skills/issues)
- **Discussions:** [GitHub Discussions](https://github.com/workato/recipe-skills/discussions)

---

Built with insights from the [Dewy Resort Hotel Demo](https://github.com/workato-devs/demo-workato-dewy-resort-hotel) project.
