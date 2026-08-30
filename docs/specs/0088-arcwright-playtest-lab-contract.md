# Arcwright Playtest Lab Contract

**Status**: Approved

**Author**: Codex | **Date**: 2026-08-30

---

# References

- Related ADRs: [D-106](../product/decisions-log.csv)
- Architecture sections: [docs/architecture/12-build-plan.md](../architecture/12-build-plan.md)
- Related specs: [docs/specs/nightcap-external-playtest-harness.md](nightcap-external-playtest-harness.md)
- Design source: [docs/superpowers/specs/2026-08-29-arcwright-playtest-lab-design.md](../superpowers/specs/2026-08-29-arcwright-playtest-lab-design.md)
- Implementation plan: [docs/superpowers/plans/2026-08-29-arcwright-playtest-lab.md](../superpowers/plans/2026-08-29-arcwright-playtest-lab.md)

---

# Overview

This spec defines the canonical contract for the Arcwright Playtest Lab: a minimal Pages homepage with Playtests as the primary entry point, a Nightcap catalog page, immutable versioned fixture routes, and a legacy alias for prior direct access. It also defines the safe local tooling and publish-time checks that keep the Playtest Lab separate from production Arcwright runtime code.

---

# In Scope

- Option C homepage at `/` with Playtests promoted above individual fixture routes.
- Nightcap catalog generation from `playtests/catalog.json`.
- Immutable fixture publishing under `/nightcap/paper-test-02/v2.2/`.
- Legacy alias preservation at `/nightcap-paper-test-02-v2.2/`.
- Root `?reveal=1` compatibility redirect to the legacy fixture alias.
- Safe catalog validation on Windows and safe static site generation.
- Playtest Steward CLI behavior for `list`, `validate`, `new`, `archive`, and `build`.
- HTML escaping for catalog-derived text and attribute values in generated pages.
- Workflow validation before GitHub Pages deployment.

---

# Out of Scope

- Production engine, API, SDK, dashboard, routing, or database changes.
- Jotform submission automation or live form mutation.
- Real-device, live-browser, or founder-session readiness claims.
- New dependencies or provider-specific logic.
- Nightcap canon changes or fixture content expansion beyond the approved non-canon harness.

---

# Human Collaboration Contract

**Interaction profiles:** Independent execution

**Classification rationale:** The direction is already approved by D-106 and the implementation plan. The remaining work is deterministic repository maintenance and verification, not a founder taste decision.

**Required founder inputs:**
- None

**Phase gates:**
- D-106 approval locked the Playtest Lab direction.
- The implementation plan at `docs/superpowers/plans/2026-08-29-arcwright-playtest-lab.md` defines the bounded execution wave.

**Review package:**
- Compare the generated site, catalog validation, CLI behavior, workflow, and fixture README against this spec and the design source.

**Approval evidence:**
- D-106, 2026-08-30, and the approved plan path above.

**Owner actions:**
- External Pages deployment, browser/device verification, and Jotform submission remain pending gates outside this spec.

---

# Acceptance Criteria

- [ ] `python -m pytest scripts/tests -q --basetemp .pytest-tmp-pages` passes locally.
- [ ] `node --test playtests/nightcap-paper-test-02-v2.2/tests/runtime.test.mjs playtests/nightcap-paper-test-02-v2.2/tests/fixture.test.mjs` passes locally.
- [ ] `python scripts/playtest_catalog.py playtests/catalog.json` validates the manifest.
- [ ] `python scripts/build_playtest_site.py --output _site` generates the homepage, Nightcap catalog, immutable fixture route, and legacy alias without deleting source trees.
- [ ] The catalog validator rejects drive-qualified, UNC, rooted, traversal, symlink-escaping, and colliding source or destination paths.
- [ ] Archive refuses to leave the catalog without a current entry and preserves the catalog plus published artifact on failure.
- [ ] Generated pages escape hostile catalog-derived title, summary, and route attribute data.
- [ ] The Pages workflow runs the full scripts test suite, the Node harness tests, catalog validation, and the deterministic build with pinned pytest.
- [ ] The fixture README states that `/` is now the homepage, `/nightcap/paper-test-02/v2.2/` is the stable fixture route, and `/nightcap-paper-test-02-v2.2/` is the legacy alias.
- [ ] The generated homepage preserves the historical root `?reveal=1` reveal flow by redirecting to the legacy fixture alias.

---

# Test Plan

- Unit tests for catalog validation, build safety, archive guards, and CLI behavior.
- Node tests for telemetry field mapping and runtime behavior.
- Deterministic site build verification into `_site`.
- Ruff check and Ruff format check on the touched Python files and tests.

---

# Risks and Unknowns

**Risks**:
- Windows path semantics can drift if route and source validation stops using native `Path` containment checks.
- A future fixture version could reuse legacy route expectations unless the catalog rules stay immutable.

**Unknowns**:
- The live Pages deployment and Jotform connector state remain external and must be verified separately.

---

# Open Questions

- None.
