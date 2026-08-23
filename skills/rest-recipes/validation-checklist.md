# REST Connector Validation Checklist

> **Run the base checklist first:** See [workato-recipes/validation-checklist.md](../workato-recipes/validation-checklist.md).

## Config and connection

- [ ] Config includes the `rest` provider and the intended named connection.
- [ ] Action `name` matches a valid name in `lint-rules.json`.
- [ ] The stored connection constrains authentication and the base URL; caller input cannot select either.
- [ ] Request paths are relative and bounded.

## Request controls

- [ ] Method, path, headers, query parameters, and body are fixed or derived only from validated contract fields.
- [ ] Connector retries and enclosing monitor retries match the operation's idempotency policy.
- [ ] Timeout and streaming controls are intentional.
- [ ] Connector-owned control fields are not copied into recipe-authored EIS solely to silence lint.

## Response and datapills

- [ ] Recipe-specific response fields are declared in the action response schema before downstream use.
- [ ] Transport datapills are limited to connector-declared intrinsic fields in `lint-rules.json`.
- [ ] HTTP status is checked before parsing or trusting the response body.
- [ ] Dynamic/raw responses are validated against a closed contract before use.

## Security and observability

- [ ] REST action and all raw-output consumers are masked.
- [ ] Caught error text, raw headers, raw body, and connection configuration are never returned or logged.
- [ ] Returned errors use bounded recipe-authored codes and messages.
- [ ] A bounded Development canary verifies status mapping, masking, and retry behavior, then the recipe is stopped and read back before broader activation.
