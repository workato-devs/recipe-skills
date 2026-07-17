# Scheduler Trigger

## Overview

**Use when:** Recipe should run on a recurring time-based schedule (daily digests,
periodic sync jobs, nightly reports) rather than in response to an external event.

**Provider:** `clock`
**Action:** `scheduled_event`

This is a **platform provider** (no external connection) — same category as
`workato_api_platform` or `workato_recipe_function`. Its config entry uses
`account_id: null` and requires `"name"` set to `"clock"` (see the base skill's
[config-section.md](../fundamentals/config-section.md) rule for platform providers).

---

## Trigger Structure

Verified from a real exported recipe (`wk recipes export`):

```json
{
  "number": 0,
  "provider": "clock",
  "name": "scheduled_event",
  "as": "trigger",
  "keyword": "trigger",
  "input": {
    "time_unit": "days",
    "trigger_every": "1",
    "trigger_at": "05:00:00.000"
  },
  "extended_input_schema": [
    {
      "control_type": "integer",
      "default": "5",
      "enforce_template_mode": true,
      "extends_schema": true,
      "hint": "Define repeating schedule. Enter whole numbers only. This field can be set to a minimum of 5 minutes.",
      "label": "Trigger every",
      "name": "trigger_every",
      "optional": false,
      "suffix": { "text": "days" },
      "type": "string"
    },
    {
      "change_on_blur": true,
      "control_type": "time",
      "enforce_template_mode": true,
      "extends_schema": true,
      "hint": "Set a time to schedule the job using supported formats only.",
      "label": "Trigger at",
      "name": "trigger_at",
      "optional": false,
      "type": "string"
    },
    {
      "control_type": "select",
      "hint": "Select the timezone to use. Leave it blank to use the account default.",
      "label": "Timezone",
      "name": "timezone",
      "optional": true,
      "pick_list": "timezone_id_global_pick_list",
      "pick_list_connection_less": true,
      "type": "string"
    },
    {
      "control_type": "date_time",
      "enforce_template_mode": true,
      "extends_schema": true,
      "hint": "Set date and time to start or leave blank to start immediately. Once recipe has been run or tested, value cannot be changed.",
      "ignore_timezone": true,
      "label": "Start after",
      "name": "start_after",
      "optional": true,
      "parse_output": "date_time_conversion",
      "render_input": "date_time_conversion",
      "since_field": true,
      "type": "date_time"
    }
  ],
  "dynamicPickListSelection": {
    "time_unit": "Days"
  },
  "unfinished": false
}
```

## Input Fields

| Field | Verified value(s) | Description |
|---|---|---|
| `time_unit` | `"days"` (lowercase in `input`) | The recurrence unit. `dynamicPickListSelection.time_unit` uses the capitalized display form (`"Days"`) alongside it — include both, matching case, as shown above. Other units (`"minutes"`, `"hours"`, `"weeks"`) are presumed to exist by analogy but are **not verified**. |
| `trigger_every` | `"1"` | How many `time_unit`s between runs, as a **string** integer. The EIS default (`"5"`) is just the UI's suggested starting value, not a constraint — the verified example uses `"1"`. |
| `trigger_at` | `"05:00:00.000"` | Time of day to run, 24-hour `HH:MM:SS.mmm` string. |

## Optional Fields (present in EIS, not set in the verified example)

- `timezone` — leave unset to use the account's default timezone
- `start_after` — a `date_time` value to delay the first run; **once the recipe has
  run or been tested, this value cannot be changed** (per the field's own hint text)

## Config Entry

```json
{
  "keyword": "application",
  "name": "clock",
  "provider": "clock",
  "skip_validation": false,
  "account_id": null
}
```

## Gotchas

1. **`time_unit` appears twice, in two cases.** `input.time_unit` is lowercase
   (`"days"`); `dynamicPickListSelection.time_unit` is capitalized (`"Days"`). Both
   are required together — this mirrors the same dual-field pattern seen in other
   dynamic-picklist-backed inputs (see the GitHub connector's `search_issues` in
   `github-recipes` skill for another example of this shape).
2. **Numeric fields are strings.** `trigger_every` is `"1"`, not `1` — consistent with
   the rest of Workato's recipe JSON convention of quoting numeric-looking values.
3. **This trigger has no downstream datapills of its own** worth noting beyond the
   standard trigger metadata — it doesn't emit event-specific data the way a webhook
   or API endpoint trigger does. Downstream actions run purely on the schedule, with
   no input payload from the trigger itself.
4. **Unverified units beyond `"days"`.** Only `"days"` has been confirmed against a
   real workspace. If you need `"minutes"`/`"hours"`/`"weeks"`, verify the exact
   lowercase/capitalized pairing in the Workato UI before relying on it — don't
   assume it follows the same pattern without checking.

## Related Documentation

- [Config Section](../fundamentals/config-section.md) — platform provider config rules
- [API Endpoint Trigger](api-endpoint.md) — for on-demand/testable triggers instead
- `github-recipes` skill's `templates/search-open-prs.json` — a real recipe using this trigger
