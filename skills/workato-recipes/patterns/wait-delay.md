# Pausing a Recipe Mid-Job (Wait / Delay)

To pause a recipe's execution for a fixed length of time before continuing to the next action — for example, spacing out a sequence of API calls, or waiting before a follow-up step in a scheduled/webhook-triggered recipe — use the `clock` connector's `wait_for_interval` action. This is a general-purpose platform action, not tied to any specific connector.

**UI label:** "Wait for specified length of time." Its own description: *"The job pauses for the specified length of time before carrying out subsequent actions in the recipe. Maximum time a job can be configured to remain paused is 732 days."*

> **NOT usable in every trigger type.** Confirmed via a real job failure: a recipe triggered by Workbot for Microsoft Teams' `bot_command` fails outright if it contains this action, with the exact platform error `"Use of long actions is not allowed in WorkBot recipes"`. This is very likely true of any "Real-time"-labeled Workbot trigger (Teams' `help_event`/`new_message_event` at minimum — see `teams-recipes`' [SKILL.md](../../teams-recipes/SKILL.md) and `lint-rules.json`), and plausibly other chat-platform Workbot connectors (e.g. Slack) with similar real-time response constraints, though that hasn't been directly checked. If a Workbot-triggered recipe needs to pause before a follow-up action, don't reach for this — use an interactive button instead (e.g. Teams' `action_continue_flow` button type) to suspend the job until the user responds or a timeout elapses.

## Shape

```json
{
  "number": 3,
  "provider": "clock",
  "name": "wait_for_interval",
  "as": "wait-004",
  "keyword": "action",
  "toggleCfg": {
    "interval": false
  },
  "input": {
    "interval": "3"
  },
  "uuid": "wait-004"
}
```

- `interval` is always a **number of seconds**, as a string — confirmed via the field's own UI label, "Interval (seconds)."
- `toggleCfg.interval` selects the input mode, same as any other toggleable field in this platform:
  - `false` — a custom value (a literal string, or a formula/datapill) in seconds, e.g. `"3"`.
  - `true` — a preset picklist (e.g. "5 minutes"). The stored `input.interval` value is still the equivalent number of seconds as a string, e.g. `"300"` for 5 minutes — the picklist is purely a UI convenience, the underlying field is identical either way.

Use `false`/a raw literal for short, precise waits (a handful of seconds); either mode works for longer, round-number waits.

## Requires the `clock` provider in config

Same as the [scheduler trigger](../triggers/scheduler.md) — `account_id: null`, no real connection needed:

```json
{
  "keyword": "application",
  "name": "clock",
  "provider": "clock",
  "skip_validation": false,
  "account_id": null
}
```

## Verification

Confirmed by a human tester adding this action live in the Workato recipe editor (not merely guessed), for both the custom-seconds mode and the preset-picklist mode, then re-pulling the recipe and reading its actual saved JSON for each. No production recipe in the source workspace was found using this action prior to this — it was previously undocumented anywhere in this repo.

## Validation Checklist

### `wait_for_interval`
- [ ] `provider` is `clock`, not a connector-specific provider — this action is available in any recipe, not tied to whatever connector the surrounding steps use
- [ ] `input.interval` is a string containing a plain number of **seconds** — do not add a separate unit field or assume minutes/hours
- [ ] Config includes a `clock` provider entry with `account_id: null` (no real connection needed, same as the scheduler trigger)
- [ ] The recipe's trigger is NOT a Workbot "Real-time" trigger (e.g. Teams' `bot_command`, `help_event`, `new_message_event`) — confirmed disallowed there with a hard platform error; use a button-based continue-flow pattern instead
