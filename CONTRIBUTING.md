# Contributing to Recipe Skills

Thank you for your interest in contributing to Recipe Skills! This guide explains how to add new skills, improve existing ones, and submit your contributions.

## Types of Contributions

### 1. Improve Existing Skills

- Fix errors in documentation
- Add new patterns or templates
- Improve code examples
- Update for API changes

### 2. Add New Templates

- Create validated recipe JSON for common operations
- Ensure templates follow skill patterns
- Include comments explaining key sections

### 3. Create New Skills

- Build skills for connectors you use
- Follow the skill structure guidelines
- Include comprehensive documentation

## Skill Structure

Every skill must follow this structure:

```
skills/<connector>-recipes/
├── skill.yaml              # Required: Manifest
├── SKILL_INSTRUCTIONS.md   # Required: Main documentation
├── templates/              # Recommended: Recipe templates
│   └── *.json
└── patterns/               # Recommended: Pattern docs
    └── *.md
```

## Creating a New Skill

### Step 1: Create Directory Structure

```bash
mkdir -p skills/my-connector-recipes/{templates,patterns}
```

### Step 2: Write skill.yaml

```yaml
name: my-connector-recipes
version: 1.0.0
description: >
  Description of what integrations this skill enables.
  Focus on the value to developers.

author: Your Name
license: MIT

capabilities:
  - Capability 1
  - Capability 2
  - Capability 3

entry_point: SKILL_INSTRUCTIONS.md

templates:
  - templates/example-operation.json

patterns:
  - patterns/pattern-name.md

platforms:
  - workato

tags:
  - relevant
  - tags
```

### Step 3: Write SKILL_INSTRUCTIONS.md

Follow this outline:

1. **Overview** - What the skill enables, when to use it
2. **Recipe Structure** - JSON anatomy specific to this connector
3. **Connector Patterns** - Unique patterns for this API
4. **Critical Patterns** - Error handling, idempotency, etc.
5. **Datapill Syntax** - Connector-specific datapill rules
6. **Template Usage** - How to adapt templates
7. **Validation Checklist** - Pre-push requirements

### Step 4: Create Templates

Copy validated recipes as templates:

```bash
cp /path/to/validated/recipe.json skills/my-connector-recipes/templates/
```

Templates should:
- Be valid Workato recipe JSON
- Include all required schema elements
- Have descriptive UUIDs
- Include comments where helpful

### Step 5: Document Patterns

Create focused pattern documents for:
- Connector-specific datapill syntax
- Error handling patterns
- Idempotency patterns
- Common operations

## Code Standards

### JSON Recipes

- Use descriptive UUIDs: `"uuid": "search-customer-001"`
- Include all required fields (uuid, as, provider, etc.)
- Follow Workato recipe structure exactly

### Documentation

- Use clear, concise language
- Include code examples for every concept
- Document common errors and solutions
- Keep agent/AI consumption in mind

### Templates

Templates should include placeholder markers for customization:

```json
{
  "name": "{{RECIPE_NAME}}",
  "config": [
    {
      "provider": "{{CONNECTOR}}",
      "account_id": {
        "name": "{{CONNECTION_NAME}}"
      }
    }
  ]
}
```

## Testing Your Skill

### 1. Manual Validation

- Verify templates are valid JSON
- Check all links work
- Ensure code examples are correct

### 2. Recipe Push Test

```bash
# Copy template to a Workato project
cp skills/my-skill/templates/example.json /path/to/workato/project/

# Push to validate
cd /path/to/workato/project
workato push
```

### 3. Agent Test

Load the skill in Claude Code and test recipe generation:

```
/my-connector-recipes

Generate a recipe to [operation description]
```

Verify the generated recipe:
- Has correct structure
- Uses correct datapill syntax
- Includes all required elements

## Submitting Changes

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b add-salesforce-skill`
3. **Make your changes**
4. **Test thoroughly**
5. **Submit PR with description:**
   - What skill/change
   - Why it's valuable
   - How you tested it

### PR Requirements

- [ ] skill.yaml is valid YAML
- [ ] SKILL_INSTRUCTIONS.md is comprehensive
- [ ] Templates are valid JSON
- [ ] All code examples work
- [ ] No sensitive data (API keys, credentials)

## Style Guide

### Naming Conventions

- Skill names: `<connector>-recipes` (e.g., `stripe-recipes`)
- Template files: `<operation>.json` (e.g., `create-customer.json`)
- Pattern files: `<pattern-name>.md` (e.g., `idempotency.md`)

### Documentation Style

- Use active voice
- Be specific and concrete
- Include "CORRECT" and "WRONG" examples
- Add tables for quick reference

### Code Style

```json
{
  "consistent": "indentation",
  "with": "2 spaces",
  "and": "no trailing commas"
}
```

## Questions?

- Open an issue for questions
- Start a discussion for ideas
- Tag maintainers for urgent items

## Recognition

Contributors are recognized in:
- Release notes
- Skill documentation (as author)
- README contributors section

Thank you for helping make Recipe Skills better!
