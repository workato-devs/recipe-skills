---
name: rest-recipes
description: Generic REST connector recipes for Workato. Use for connection-bound HTTP requests with fixed connection configuration, response schemas, transport status handling, retry controls, and masked external calls.
license: MIT
metadata:
  author: Workato
  version: "1.0.0"
---

# REST Recipes Skill

> **DEPENDENCY: Load the `workato-recipes` base skill first if not already loaded.**

Use this skill for Workato's connection-bound generic REST connector. It complements the base skill's HTTP action pattern with connector-specific authoring and validation guidance.

## Before authoring

- Confirm the exact REST connection and its allowed base URL.
- Keep request paths relative to that base URL; do not accept caller-selected URLs, methods, headers, or authentication fields unless the contract explicitly requires them.
- Read `lint-rules.json` for the audited action and trigger names and the connector-owned input/output metadata.
- Use a response schema when downstream steps require named response fields.
- Treat the raw body, headers, connector error, and credential-bearing connection configuration as sensitive unless a narrower classification is proven.

## Request and response behavior

The connector owns several top-level request-control fields that Workato canonical exports may omit from `extended_input_schema`. Do not copy those fields into a recipe-authored EIS merely to satisfy a mirror check; `lint-rules.json` identifies them for the linter.

Response bodies are dynamic. A configured response schema may be materialized under the recipe's `extended_output_schema`, while stable transport outputs remain available as connector datapills even when the canonical EOS omits them. The connector rules distinguish those intrinsic outputs from recipe-specific response fields.

For security-sensitive reads:

- Disable connector retries and enclosing monitor retries unless the operation is explicitly retry-safe.
- Mask the REST action and every step that receives its raw outputs.
- Prefer `ignore_http_errors` when the recipe must classify bounded HTTP status codes itself; otherwise keep error handling static and never return caught error text.
- Validate exact status and a closed response shape before using response data.
- Return only bounded, recipe-authored fields. Never return or log raw headers, body, connection settings, or caught error messages.

## Related base guidance

- [Ad hoc and REST HTTP actions](../workato-recipes/patterns/adhoc-http-actions.md)
- [Datapill syntax](../workato-recipes/fundamentals/datapill-syntax.md)
- [Try/catch](../workato-recipes/control-flow/try-catch.md)

Run the base and connector validation checklists before push.
