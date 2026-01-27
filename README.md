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

When a user invokes a skill (`/workato-recipes`, `/stripe-recipes`, `/salesforce-recipes`), you will have full context to help them generate valid Workato recipe JSON using natural language.

Users can ask you to build recipes using requests like:
- "Create an API endpoint recipe that accepts customer data"
- "Create a recipe to search for a Stripe customer by email"
- "Create a recipe to upsert a Salesforce Contact by external ID"

Each skill contains documentation, templates, and patterns you can reference to generate recipes that follow Workato best practices.

### For Human Developers

Skills are designed for AI agents to generate recipes. As a human developer:

1. Navigate to this repo directory in Claude Code
2. Invoke a skill: `/workato-recipes`, `/stripe-recipes`, or `/salesforce-recipes`
3. Ask the agent to generate a recipe using natural language
4. Review and test the generated recipe JSON
5. Deploy: `workato push`

For reference and learning, you can browse:
- Skill documentation: `skills/{skill-name}/SKILL_INSTRUCTIONS.md`
- Example templates: `skills/{skill-name}/templates/*.json`

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

## Using with AI Agents

### Claude Code

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

The agent will have full context from the skill to generate valid Workato recipe JSON.

### Other AI Agents (Codex, Cursor, Windsurf, etc.)

Point your agent to the skill entry points directly:

1. **Load the base skill first:**
   ```
   Read skills/workato-recipes/SKILL_INSTRUCTIONS.md
   ```

2. **Then load a connector skill:**
   ```
   Read skills/stripe-recipes/SKILL_INSTRUCTIONS.md
   Read skills/salesforce-recipes/SKILL_INSTRUCTIONS.md
   ```

Each `skill.yaml` defines an `entry_point` field pointing to the main instruction file, plus an `extends` field for dependencies. Agents or tooling can parse this metadata to automate skill loading.

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

## Roadmap

### Completed (v1.0)
- [x] workato-recipes base skill (triggers, control flow, fundamentals)
- [x] stripe-recipes skill with templates and patterns
- [x] salesforce-recipes skill with SObject operations
- [x] Claude Code slash command integration
- [x] CLI extension specification

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
