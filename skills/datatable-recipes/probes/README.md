# probes

Runnable evidence for claims in this skill that are about **platform behaviour at runtime** —
things no offline fixture can settle, because activation accepts the payloads in question and the
failure only appears in the job output.

There is one today.

## `probe_operands.py`

Measures the `get_records` filter operand vocabulary, and reproduces the silent-drop behaviour
documented in [`../patterns/get-records.md`](../patterns/get-records.md).

Per candidate operand it builds a clock-triggered recipe carrying a single `get_records` step,
activates it, waits for a job, reads the step output, then **stops and deletes the recipe**.
Nothing is left in the workspace.

```sh
export WK_TOKEN=...            # Developer API token for YOUR workspace
python3 probe_operands.py \
    --host https://app.<dc>.workato.com \
    --folder <folder-id> \
    --table <table-id> \
    --column <column-uuid-hyphenated> \
    --value <a value matching exactly one row> \
    --total-rows <unfiltered row count of that table>
```

No dependencies beyond the standard library. Every workspace-specific value is a required
argument — there is nothing from the author's workspace baked in.

### Reading the output

| Verdict | Means |
|---|---|
| `MEMBER` | the job ran; the operand is in the backend `ApiQueryOperation` enum |
| `NOT-A-MEMBER` | the job failed with `Expected input type "ApiQueryOperation"` |
| `WRONG-TYPE` | the job failed some other way — a valid operand on the wrong column type |
| `applied(n rows)` / `IGNORED(all rows)` | whether the filter actually took effect |

`--total-rows` is what separates a filter that worked from one that was silently ignored: an
ignored filter returns unfiltered rows and the job is still green.

**`MEMBER` and `WRONG-TYPE` are different outcomes, and a name absent from the member list is not
therefore a non-member** — it may have been rejected for the column type instead. Record each
candidate's exact verdict and error string; a member/non-member partition alone cannot answer that
question afterwards, which is a mistake already paid for once.

### What this cannot do

It needs a Developer API token and a workspace, because the claims are about how a live platform
responds. It is not a unit test and this repo has no harness to make it one.

To reproduce the silent drop specifically, point `--column` at an **integer** column and give
`--value` something no row matches. A working filter returns 0 rows; the measured behaviour is that
every row comes back with the job green. Run it against a **string** column as a control — the same
invocation returns 0 rows there.

Note the probe sets `limit: "50"`. On a table smaller than that a dropped filter returns the whole
table, which is how it was first spotted; on a larger table it returns an unfiltered *page*. Judge
by whether returned records satisfy the filter, not by the row count.
