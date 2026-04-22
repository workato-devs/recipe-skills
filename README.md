# Recipe Skills

An open-source knowledge library for agent-assisted Workato recipe development. A **Workato Labs** project.

## What are Recipe Skills?

Recipe Skills teach AI agents how to generate valid Workato recipe JSON. Each skill encapsulates the connector-specific knowledge an agent needs -- which actions exist, when to use each one, how datapills work for that connector, and what gotchas to avoid. Without skills, agents hallucinate action names, produce malformed schemas, and miss critical connector rules.

**A skill IS:**
- A knowledge bundle that teaches agents how to write recipes for a specific connector
- Documentation, validated templates, and patterns an agent can reference during generation
- Audited lint rules defining every valid action and trigger name for the connector

**A skill is NOT:**
- A code library you import at runtime
- Pre-packaged operations or a connector SDK
- A replacement for the Workato platform

## Available Skills

### Base Skill

| Skill | Description |
|-------|-------------|
| [workato-recipes](skills/workato-recipes/) | Core Workato recipe fundamentals -- triggers, control flow, datapills, formulas, recipe JSON structure |

### Connector Skills

| Skill | Connector | Native Actions | Triggers |
|-------|-----------|:-:|:-:|
| [asana-recipes](skills/asana-recipes/) | Asana | 16 | 2 |
| [gmail-recipes](skills/gmail-recipes/) | Gmail | 3 | 1 |
| [jira-recipes](skills/jira-recipes/) | Jira | 17 | 11 |
| [salesforce-recipes](skills/salesforce-recipes/) | Salesforce | 32 | 15 |
| [slack-recipes](skills/slack-recipes/) | Slack (native + Workbot) | 9 | 2 |
| [stripe-recipes](skills/stripe-recipes/) | Stripe | 7 | 4 |

Action and trigger counts reflect what is audited in each skill's `lint-rules.json`. All connectors also support `__adhoc_http_action` for API operations beyond the native action set.

## Quick Start

### With Claude Code

This repo includes slash commands for each skill. From this repo directory:

```bash
/workato-recipes    # Load recipe fundamentals
/stripe-recipes     # Generate Stripe recipes
/salesforce-recipes # Generate Salesforce recipes
/slack-recipes      # Generate Slack/Workbot recipes
/gmail-recipes      # Generate Gmail recipes
/jira-recipes       # Generate Jira recipes
/asana-recipes      # Generate Asana recipes
```

Then ask the agent to generate a recipe:
- "Create an API endpoint recipe that accepts customer data"
- "Create a recipe to search for a Stripe customer by email and create a PaymentIntent"
- "Create a recipe to upsert a Salesforce Contact by external ID"
- "Create a slash command that collects user input via dialog and posts to Slack"
- "Create a recipe that searches Jira issues by JQL and returns sprint status"
- "Create a recipe that creates an Asana task with subtasks"

The agent uses the skill's documentation, templates, and lint rules to generate valid recipe JSON.

### With Other AI Agents (Codex, Cursor, Windsurf, etc.)

Each skill directory contains a `SKILL.md` file following the [open agent skills standard](https://agentskills.io). Any SKILL.md-aware tool can discover and load these skills automatically.

To load skills manually, point your agent to the entry points:

1. **Load the base skill first:**
   ```
   Read skills/workato-recipes/SKILL.md
   ```

2. **Then load a connector skill:**
   ```
   Read skills/<connector>-recipes/SKILL.md
   ```

Each `skill.yaml` defines an `entry_point` and `extends: workato-recipes` to declare the base dependency. Agents or tooling can parse this metadata to automate skill loading.

### Deploy

Generated recipes are standard Workato recipe JSON. Push them to your workspace:

```bash
wk push
```

## Skill Structure

Each connector skill follows this structure:

```
skills/<connector>-recipes/
├── skill.yaml              # Metadata and manifest
├── SKILL.md   # Main knowledge document
├── lint-rules.json         # Valid action/trigger names (source of truth)
├── validation-checklist.md # Connector-specific validation checks
├── templates/              # Validated recipe templates
│   └── *.json
└── patterns/               # Pattern documentation
    └── *.md
```

The base skill (`workato-recipes`) additionally includes `fundamentals/`, `triggers/`, and `control-flow/` subdirectories covering core Workato concepts that all connector skills inherit.

## How It Works

Skills are structured around a key principle: **lint rules own the "what," instructions own the "how."**

- **`lint-rules.json`** defines every valid action and trigger name for the connector, audited against the actual Workato connector. This is the single source of truth that prevents agents from hallucinating action names.

- **`SKILL.md`** teaches agents when and how to use each action through decision-logic guidance (e.g., "use `search_sobjects` for exact match, `search_sobjects_soql` for complex SOQL queries"). It references `lint-rules.json` for valid names rather than duplicating them.

- **`templates/`** provide complete, validated recipe JSON that agents can reference and adapt. These are real recipes that have been pushed to Workato, not placeholder scaffolds.

- **`validation-checklist.md`** gives agents a pre-push verification checklist covering connector-specific rules that lint alone cannot catch (datapill path formats, EIS requirements, query syntax).

## Documentation

### Skill Instructions
- [workato-recipes](skills/workato-recipes/SKILL.md) -- Recipe fundamentals and base patterns
- [asana-recipes](skills/asana-recipes/SKILL.md) -- Asana task and project management
- [gmail-recipes](skills/gmail-recipes/SKILL.md) -- Gmail email operations
- [jira-recipes](skills/jira-recipes/SKILL.md) -- Jira issue tracking and JQL
- [salesforce-recipes](skills/salesforce-recipes/SKILL.md) -- Salesforce CRM operations
- [slack-recipes](skills/slack-recipes/SKILL.md) -- Slack and Workbot integration
- [stripe-recipes](skills/stripe-recipes/SKILL.md) -- Stripe payment processing

### Project
- [Contributing Guide](CONTRIBUTING.md) -- How to add or improve skills
- [wk CLI + Recipe Lint Guide](docs/cli-guidance.md) -- Linter setup, tiers, rule reference

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

- **Add a new connector skill** -- build a skill for a connector you use
- **Improve existing skills** -- fix bugs, add patterns, add templates
- **Extend the base skill** -- improve core recipe knowledge that all connector skills inherit

## Roadmap

### Shipped
- [x] Base skill: triggers, control flow, datapills, formulas, recipe JSON structure
- [x] Connector skills: Salesforce, Stripe, Slack, Gmail, Jira, Asana
- [x] Audited lint rules for all connectors
- [x] Claude Code slash commands for all connectors (7/7)
- [x] SKILL.md standard conformance (agent-agnostic skill discovery)
- [x] wk CLI + recipe-lint integration guide
- [x] Contribution guidelines

### Next
- [ ] Expand connector coverage (additional connectors)
- [ ] wk CLI plugin ecosystem (additional lint rules, recipe generation)

## License

MIT License -- see [LICENSE](LICENSE) for details.

## Support

- **Issues:** [GitHub Issues](https://github.com/workato/recipe-skills/issues)
- **Discussions:** [GitHub Discussions](https://github.com/workato/recipe-skills/discussions)
