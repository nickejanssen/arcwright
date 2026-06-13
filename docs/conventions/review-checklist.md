# Review Checklist

Spend more time here than feels comfortable. This is the most leveraged work in the AI-assisted workflow.

## Before Reading the Diff

- [ ] Is the spec linked, current, and approved?
- [ ] Are acceptance criteria testable and tested?
- [ ] Does the change scope match the spec scope?
- [ ] Do product-scope additions have durable approval evidence in `docs/product/decisions-log.csv` plus an ADR or approved spec when needed?

## While Reading the Diff

- [ ] Read every file changed, not just the highlights.
- [ ] Look for scope creep beyond the approved spec.
- [ ] Look for product-scope additions that appear only in a story bible, PR description, chat summary, or diff.
- [ ] Look for weakened, deleted, or narrowly mocked tests that reduce confidence.
- [ ] Look for suppressed errors, broad exception handling, or TODOs that hide breakage.
- [ ] Look for new dependencies and confirm they were explicitly approved.
- [ ] Look for secrets, credentials, or unsafe logging of sensitive data.
- [ ] Look for hardcoded values that should live in config, env, or routing tables.
- [ ] Verify LLM-dependent code keeps prompts version-controlled.
- [ ] Verify eval cases were updated when prompt, routing, or model behavior changed.
- [ ] Verify model selection is justified and consistent with routing policy.

## Before Merging

- [ ] CI is green.
- [ ] No review comments are unresolved.
- [ ] An ADR was added if the architecture changed.
- [ ] Docs were updated if user-visible behavior changed.
