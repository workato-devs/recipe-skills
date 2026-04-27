# Roadmap

## Vision

Recipe Skills is a community-driven knowledge library. The goal is broad connector coverage built and maintained by the people who use those connectors daily. The project provides the architecture, the base skill, and reference implementations -- the community extends it to the connectors they care about.

## How We Prioritized the Initial Connector Set

The six launch connectors were chosen based on a combination of: **adoption** and **architectural coverage**.

The primary driver of recipe skills is usefulness. A skill for a connector that many people use every day delivers more value than one for a niche connector with a more complex action set. These six connectors make it easy for contributors to understand the skill format across a range of architectural complexity levels, and provide a baseline set of value to get started building common recipes. 

| Connector | Skill complexity profile |
|-----------|------------------------|
| **Salesforce** | Complex: SOQL, EIS rules, polymorphic fields, 32 actions / 15 triggers |
| **Jira** | Complex: query language (JQL), deep trigger configuration |
| **Slack** | Dual-mode: native Slack actions + Workbot interaction model |
| **Stripe** | API-heavy: most work goes through `__adhoc_http_action` |
| **Asana** | Mid-complexity: 16 actions, 2 triggers |
| **Gmail** | Simple: 3 actions, 1 trigger -- good first-contribution reference |

## Connector Coverage

### Contributing a new connector skill

The fastest way to get a skill for a connector you use is to build it. The architecture is designed to make this approachable:

- **Start from a reference.** `gmail-recipes` takes under an hour to read end-to-end. `salesforce-recipes` shows how to handle a complex connector. Pick the reference closest to your target connector's complexity.
- **The hard part is the audit, not the code.** Most of the work is enumerating valid action/trigger names from a real Workato workspace. The file structure and patterns are established.
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** walks through every step, from directory creation to PR submission.

### How we prioritize connector requests

When the community requests a connector (via [Issues](https://github.com/workato/recipe-skills/issues) or [Discussions](https://github.com/workato/recipe-skills/discussions)), we prioritize based on:

1. **Adoption** -- widely used connectors benefit the most people. A skill for a popular SaaS application is high-priority regardless of its connector complexity.
2. **Community demand** -- how many people are asking for it, and are any willing to contribute?
3. **Connector complexity** -- connectors with many actions, complex query languages, or non-obvious gotchas tend to benefit *more* from a skill, but a simple widely-used connector still deserves one. Agent accuracy improves with any well-structured skill.

The best way to signal demand is to open an issue. The best way to unblock a connector is to contribute it.

## Beyond Connectors

Connector coverage is the most visible axis of growth, but not the only one. Areas we're investing in:

- **`wk` CLI integration** -- deeper integration between skills and the `wk` CLI plugin ecosystem, including additional lint rules and recipe generation capabilities.
- **Skill architecture improvements** -- refining the base skill and skill structure as we learn from community contributions and real-world agent usage.

## How to Get Involved

- **Build a skill** for a connector you use -- see [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Request a connector** -- open an [issue](https://github.com/workato/recipe-skills/issues) describing your use case
- **Improve existing skills** -- add templates, fix patterns, improve guidance
- **Join the discussion** -- [GitHub Discussions](https://github.com/workato/recipe-skills/discussions) for ideas and questions
