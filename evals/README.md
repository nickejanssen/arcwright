# Eval Harness

This directory contains the first runnable eval harness for Arcwright's LLM-dependent code paths.

## Scope Today

The current repo does not yet contain prompt files. The initial harness therefore focuses on the routing and model-selection surface that exists today:

- `engine/routing/router.py`
- `config/routing_table.json`
- provider/model routing-policy invariants

As new prompt files, routing code, or safety-generation paths land, add new case files and runners here rather than replacing this structure.

## Directory Layout

- `cases/`: JSON case files, one case per file
- `runners/`: pytest-based runner code, one runner module per eval surface
- `reports/`: machine-readable run outputs and summaries

## Case Format

Each JSON case file should contain:

- `id`: stable case identifier
- `description`: plain-language explanation of what the case checks
- `input`: structured input for the runner
- `expected_behavior`: free-text description of the intended outcome
- `expected_assertions`: machine-checkable assertions when possible

## Running the Suite

Run the routing evals with:

```bash
pytest evals/runners/test_routing_evals.py -q
```

The runner writes a JSON report to `evals/reports/routing_eval_report.json`.

## Adding Cases

1. Add a new JSON file under `evals/cases/`.
2. Match the schema used by the existing routing cases.
3. Keep `expected_assertions` machine-checkable where possible.
4. Extend the corresponding runner only when the new case shape requires new logic.

## What Passing Means

For deterministic checks, passing means every machine-checkable assertion matched the actual implementation.

For future non-deterministic outputs, passing should mean:

- all hard assertions passed
- the output stayed within the allowed behavioral envelope
- any free-text review notes do not indicate a regression worth blocking on

Until live generation evals exist, this harness is a policy and configuration guardrail rather than a narrative-quality score.
