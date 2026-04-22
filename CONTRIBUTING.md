# Contributing to Recipe Skills

This guide covers how to contribute to the recipe-skills project. Read the section that matches your goal:

- [Creating a New Connector Skill](#creating-a-new-connector-skill) -- add support for a new Workato connector
- [Contributing to Existing Skills](#contributing-to-existing-skills) -- fix, extend, or improve a connector skill
- [Contributing to the Base Skill](#contributing-to-the-base-skill-workato-recipes) -- extend the core Workato recipe knowledge

---

## Architecture Principles

These principles prevent the drift and bloat patterns that degrade agent accuracy over time. Every contribution must follow them.

**1. lint-rules.json is the single source of truth for action/trigger names.**
Every valid action and trigger name for a connector is defined in `lint-rules.json`. This file is audited against the actual Workato connector. No other file should enumerate or duplicate these names.

**2. SKILL.md owns behavioral guidance, not name enumeration.**
Instructions teach agents *when* and *how* to use actions via decision trees. They reference `lint-rules.json` for *which* actions exist. They never list action names in tables.

**3. validation-checklist.md defers to lint-rules.json for name checks.**
The action name validation line item should read: `Action name matches a valid name in lint-rules.json or is __adhoc_http_action`. It should not reproduce action names.

**4. Decision-logic guidance outperforms flat tables.**
Organize actions by use case ("when to use X vs Y") rather than listing them alphabetically. Agents need to make choices, not scan inventories.

**5. Templates use real, validated values.**
No placeholder syntax like `{{RECIPE_NAME}}` or `{{CONNECTOR}}`. Templates are actual recipe JSON that has been pushed to Workato and validated.

### Anti-Patterns

Do not:
- Create action/trigger enumeration tables in SKILL.md
- Hardcode action counts (e.g., "18 native actions") -- they go stale when connectors update
- Duplicate lint-rule names in validation checklists
- Add connector-specific content to the base workato-recipes skill
- Use placeholder syntax in templates

---

## Skill Architecture

### Connector Skill (required files)

```
skills/<connector>-recipes/
├── SKILL.md     # REQUIRED - Behavioral guidance, decision logic
├── lint-rules.json           # REQUIRED - Authoritative action/trigger name list
├── skill.yaml                # REQUIRED - Manifest (must set extends: workato-recipes)
├── validation-checklist.md   # REQUIRED - Connector-specific validation checks
├── patterns/                 # Recommended - Deep-dive pattern docs (one topic per file)
└── templates/                # Recommended - Validated recipe JSON examples
```

### Base Skill (workato-recipes)

```
skills/workato-recipes/
├── SKILL.md
├── skill.yaml
├── validation-checklist.md
├── fundamentals/             # Recipe structure, datapills, config
├── triggers/                 # API endpoint, callable recipe
├── control-flow/             # if/else, try/catch, foreach
├── patterns/                 # Adhoc HTTP, custom connectors, variables
└── templates/                # Base recipe templates
```

### Base vs Connector Boundary

| Belongs in base (workato-recipes) | Belongs in connector skill |
|---|---|
| Trigger types (API endpoint, callable) | Connector-specific actions and triggers |
| Control flow (if/else, try/catch, foreach) | Connector-specific datapill path exceptions |
| Datapill syntax fundamentals | Connector-specific config examples |
| Formula methods and allowlist | Connector-specific EIS rules |
| Recipe JSON structure | Connector-specific validation items |
| Adhoc HTTP action patterns | Connector-specific query syntax (SOQL, JQL, etc.) |
| Variables and lists | |

---

## Creating a New Connector Skill

Use `gmail-recipes` as the simplest existing skill to reference (3 actions, 1 trigger). For a complex example, see `salesforce-recipes` (32 actions, 15 triggers).

### Step 1: Create directory structure

```bash
mkdir -p skills/<connector>-recipes/{templates,patterns}
```

### Step 2: Create lint-rules.json

This is the most critical file. It defines every valid action and trigger name for the connector.

**Process:**
1. Open the target connector in a Workato workspace
2. Enumerate every available action by its internal `name` field (not the display label)
3. Enumerate every available trigger by its internal `name` field
4. Create the file following this schema:

```json
{
  "version": "0.1.0",
  "connector": "<connector>",
  "connector_internals": [],
  "valid_action_names": [
    "action_one",
    "action_two"
  ],
  "valid_trigger_names": [
    "trigger_one"
  ],
  "action_rules": []
}
```

**Every name must be verified against the actual connector in a Workato workspace.** Do not guess action names from vendor API documentation -- the Workato connector may not expose all API endpoints, and internal names often differ from API method names.

### Step 3: Write skill.yaml

```yaml
name: <connector>-recipes
version: 1.0.0
description: >
  <Connector> integration recipes for Workato. This skill enables AI agents
  to generate valid Workato recipe JSON for <connector> operations.

author: Your Name
license: MIT

extends: workato-recipes

capabilities:
  - Capability 1
  - Capability 2

entry_point: SKILL.md

templates:
  - templates/example-operation.json

patterns:
  - patterns/pattern-name.md

validation:
  - validation-checklist.md

platforms:
  - workato
  - <connector>

tags:
  - <connector>
  - integration
  - recipes
```

`extends: workato-recipes` is required -- it declares the dependency on the base skill.

### Step 4: Write SKILL.md

Follow this established section structure:

```markdown
# <Connector> Recipes Skill - Agent Instructions

> **DEPENDENCY: Load `/workato-recipes` first if not already loaded.**

[Brief intro: what the skill provides]

## CRITICAL: Pre-Generation Checklist
### For EXISTING projects:
### For GREENFIELD projects:
### ALWAYS:

## Table of Contents

## When to Use This Skill

## <Connector> Config Requirements

## Native Connector Guidance          <-- decision trees, NOT enumeration tables

## <Connector> Datapill Paths

## [Connector-specific sections]      <-- SOQL syntax, JQL syntax, etc.

## Common Patterns

## Validation

## Templates

## References
```

**The "Native Connector Guidance" section is where most contributors go wrong.** Here is the correct approach:

Open with counts and a pointer to lint-rules.json:
```markdown
The <Connector> connector provides N native actions and M triggers.
See `lint-rules.json` for the authoritative list of valid action and trigger names.
```

Then organize by **decision context**, not alphabetical listing:

```markdown
### Choosing the Right Trigger
- **`trigger_a`** -- Use when [scenario]. Requires [key inputs].
- **`trigger_b`** -- Use when [different scenario].

### Choosing the Right Action
**Record operations:**
- **`create_thing`** -- Use for [scenario].
- **`update_thing`** -- Use when you already have the ID.

**Search:**
- **`search_things`** -- Exact match. Has critical EIS rules. See [detail below].
- **`search_things_by_query`** -- Full query language for complex criteria.
```

See `skills/asana-recipes/SKILL.md` for the cleanest example of this pattern.

### Step 5: Write validation-checklist.md

Must open with a reference to the base checklist:

```markdown
# <Connector> Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md)

## Config & Connection
- [ ] Config includes `<connector>` provider with connection reference
- [ ] Action `name` matches a valid name in `lint-rules.json` or is `__adhoc_http_action`

## Datapill Paths
- [ ] Datapill paths do NOT include `["body"]` wrapper (for native actions)

## [Connector-specific sections]
```

See `skills/gmail-recipes/validation-checklist.md` for the simplest example.

### Step 6: Create templates

- Must be actual Workato recipe JSON that has been successfully pushed via `wk push`
- Use real values, not placeholders
- Use descriptive UUIDs: `search-contact-001`, `create-task-002`
- Include at least one template for the connector's most common operation
- Update `skill.yaml` to list each template

### Step 7: Create patterns (recommended)

One markdown file per deep-dive topic:
- Connector-specific query syntax (SOQL, JQL, Gmail query operators)
- Complex field mapping or schema rules
- API endpoint catalogs for connectors where most work goes through adhoc HTTP
- Update `skill.yaml` to list each pattern

---

## Contributing to Existing Skills

### Updating lint-rules.json

- Every addition or removal must be verified against the actual connector in a Workato workspace
- Do not add names based on vendor API documentation alone
- Keep the list sorted alphabetically

### Updating SKILL.md

- **Never add action name enumerations** -- add behavioral guidance instead
- When a new action is added to lint-rules.json, add decision-logic guidance for when to use it in the "Native Connector Guidance" section
- When fixing a bug, add a CORRECT/WRONG example pair
- Keep the established section structure intact
- Add new connector-specific sections between "Datapill Paths" and "Patterns"

### Adding templates

- Must be validated by pushing to Workato (`wk push`)
- Use descriptive UUIDs
- Update `skill.yaml` to reference the new template

### Adding patterns

- One topic per file
- Update `skill.yaml` to reference the new pattern

---

## Contributing to the Base Skill (workato-recipes)

Changes to the base skill affect all connector skills. Proceed carefully.

### What belongs in the base skill

- Recipe JSON structure fundamentals (numbering, blocks, UUIDs)
- Trigger types (API endpoint, callable recipe)
- Control flow patterns (if/else, try/catch, foreach)
- Datapill syntax fundamentals
- Formula methods and the allowlist
- Adhoc HTTP action patterns
- Custom connector SDK patterns
- Variables and lists
- Cross-cutting validation rules

### What does NOT belong

Anything specific to a single connector: actions, triggers, datapill exceptions, config examples, EIS rules, query syntax. These belong in the connector's own skill.

### Testing requirement

Before submitting, verify your changes against at least 2 connector skills. The base validation checklist (`workato-recipes/validation-checklist.md`) is referenced by every connector checklist -- a mistake here propagates everywhere.

---

## Code Standards

### JSON recipes

- 2-space indentation, no trailing commas
- Descriptive UUIDs: `search-contact-001`, `return-success-005` (max 36 characters)
- Sequential `number` fields starting at 0 for the trigger
- Real values in all fields -- no placeholder syntax

### Documentation

- Active voice, concise
- CORRECT/WRONG example pairs for gotchas
- Decision trees over flat tables
- Written for AI agent consumption -- clarity and precision matter more than prose

### Naming conventions

| Item | Convention | Example |
|---|---|---|
| Skill directory | `<connector>-recipes` | `stripe-recipes` |
| Template file | `<operation>.json` | `create-customer.json` |
| Pattern file | `<pattern-name>.md` | `jql-query-syntax.md` |

---

## Submitting Changes

### Pull request process

1. Fork the repository
2. Create a feature branch: `git checkout -b add-<connector>-skill`
3. Make changes following this guide
4. Test thoroughly (see checklist below)
5. Submit PR with: what changed, why, how you tested it

### PR checklist

- [ ] `lint-rules.json` is present and every name verified against actual Workato connector
- [ ] `skill.yaml` is valid YAML and includes `extends: workato-recipes`
- [ ] `SKILL.md` follows the established section structure
- [ ] `SKILL.md` does not enumerate action names (references `lint-rules.json` instead)
- [ ] `validation-checklist.md` is present and references `lint-rules.json` for name checks
- [ ] Templates are valid JSON with real values (no placeholders)
- [ ] Templates have been pushed to a Workato workspace successfully
- [ ] All code examples are correct
- [ ] No sensitive data (API keys, credentials, real account names)

### Testing

**Manual validation:**
- Verify templates are valid JSON
- Check all internal links resolve
- Confirm code examples match the patterns described

**Recipe push test:**
```bash
cd /path/to/workato/project
cp skills/<connector>-recipes/templates/example.json .
wk push
```

**Agent test:**
Load the skill in Claude Code and generate a recipe. Verify it uses correct action names from `lint-rules.json` and follows the behavioral guidance from `SKILL.md`.

---

## Questions?

- Open an issue for questions
- Start a discussion for ideas
- Tag maintainers for urgent items

## Recognition

Contributors are recognized in release notes, skill documentation (as author), and the README contributors section.
