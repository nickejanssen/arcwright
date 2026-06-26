# AW-253: Nightcap Web Mini-game Rendering And Device Integration

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-20 (Draft); **Approved**: 2026-06-25

---

# References

- Related ADRs: `docs/decisions/0003-nightcap-web-experience-runtime.md`, `docs/decisions/0009-mini-game-runtime-boundary.md`
- Related specs: `docs/specs/0049-aw-252-mini-game-api-events-and-sdk.md`, `docs/specs/0055-aw-225-nightcap-web-runtime-connector-scaffold.md`
- GitHub issue: #147

---

# Overview

Render mini-games in the Nightcap web experience while Arcwright remains the
only canonical state authority.

---

# In Scope

- Renderer registry keyed by `gameId`, populated by manifest scan
- Individual, collaborative, and group fixture renderers, each living inside
  its mini-game package at `nightcap/mini_games/<id>/client/renderer.ts`
- A small, surface-aware renderer kit (`nightcap-web/src/mini-game-kit/`) that
  every renderer composes: typed `defineRenderer`, deadline-anchored
  `useCountdown`, defense-in-depth `useAudienceGuard`, deduplicating
  `useSubmissionGuard`, and `reportPerf` measurement
- Authorized SDK event/state consumption and action submission, with SSE direct
  from the browser to Arcwright using the player-scoped token; the Worker stays
  out of the data path
- Touch, keyboard, reduced-motion, loading, timeout, error, and reconnect
  states
- Shared-display and private-device privacy verification
- Performance budgets enforced in CI: bundle size, mount-to-paint, no layout
  shift after first paint
- Cloudflare Pages, Workers, and Durable Objects integration after the revisit
  gate (gate already satisfied by AW-225)

---

# Out Of Scope

- Arc execution, timers, scoring, clue unlocking, or canonical state in the web
  runtime
- Production game selection
- Local development CLI and Python-to-TypeScript type generation (tracked as
  separate follow-up tasks)
- Real-user Web Vitals telemetry endpoint in Python (a `reportPerf` hook is
  defined in this task; the receiving endpoint will land in a follow-up)

---

# Acceptance Criteria

- [ ] The ADR 0003 revisit comparison is recorded before the first
  Cloudflare-specific dependency or deployment configuration. (Satisfied by
  AW-225; see `docs/specs/0055-aw-225-nightcap-web-runtime-connector-scaffold.md`
  Cloudflare Revisit Note. No new Cloudflare runtime surface is added by this
  task beyond the AW-225 scaffold.)
- [ ] All three fixture modes render on their intended surfaces (phone, shared
  display, host) and pass surface-specific snapshot tests.
- [ ] Clients submit actions through the SDK contract and cannot resolve
  outcomes locally. Renderers never compute scores, validate submission
  content, time out runs, or unlock clues.
- [ ] Reconnect restores authorized presentation state by re-fetching
  `getMiniGameState` after stream drop and resyncing the renderer.
- [ ] Private payloads never reach another player or the shared display.
  Verified by the privacy matrix test and by the defense-in-depth audience
  filter.
- [ ] Accessibility and degraded-network states pass documented checks: 44 px
  touch targets, keyboard reachability, `aria-live` regions for countdown and
  status, `prefers-reduced-motion` disables animations.
- [ ] CI performance budgets pass: bundle per package under 30 KB gzipped,
  bundle under 100 KB uncompressed, mount-to-first-paint under 100 ms in
  happy-dom, zero layout shift after first paint.

---

# Test Plan

- Component tests for renderer registration and all visual states (loading,
  idle, active, paused, timed_out, completed, cancelled, disconnected)
- Mocked Arcwright integration tests (mocked `fetch` + ReadableStream SSE)
- Real-device privacy and reconnect matrix feeding AW-230
- Performance budget tests in CI (mount-to-paint, bundle size)
- Privacy matrix test: every audience target x every surface

---

# Design Notes (2026-06-25)

Three renderer architectures were considered:

1. Pure server-rendered HTML strings (matches existing `nightcap-web/ui.ts`
   pattern). Rejected because polling-driven UI cannot deliver smooth
   countdowns or per-frame interaction feedback, which are core to mini-game
   feel.
2. DOM-mounted SPA in the browser with the full `ArcwrightClient` shipped to
   the client and Worker proxying all events. Rejected because it duplicates
   Arcwright's SSE fanout work in the Worker, adds a hop to every event, and
   requires a SPA framework that diverges from the rest of `nightcap-web/`.
3. **Selected: Hybrid.** The Worker serves the page shell and a small bundled
   browser module. Each mini-game ships a TypeScript renderer inside its own
   package directory. The browser opens an SSE connection directly to
   Arcwright using the existing player-scoped token, and POSTs submissions
   directly to Arcwright. The Worker stays out of the data path. The mini-game
   kit provides typed primitives so the fast, accessible, secure path is the
   default path.

The hybrid is the only option that satisfies every priority on the founder's
list: best gameplay feel (rAF countdowns, native input latency); best
performance (no Worker proxy hop, SSE fanout already done in Arcwright per
AW-216); best cost efficiency (Worker only serves shell and static asset);
easiest to add new mini-games (package-local renderers are drop-in); best for
the platform (uses the SDK contract as the integration boundary, exactly as
ADR-0003 §"SDK assumptions" prescribes).

## Package-local renderers

Renderers live alongside the manifest and definition in the mini-game package:

```
nightcap/mini_games/<game-id>/
  manifest.json
  definitions/0.1.0.json
  client/
    renderer.ts          ← this task wires three of these
```

The `nightcap-web` build step discovers packages with `client/renderer.ts`,
generates an import module, and bundles the result. Adding a new mini-game is
a directory drop, not a `nightcap-web` edit. Future surfaces (iOS, Unity,
voice) add sibling renderer files in the same package directory.

## Renderer kit

`nightcap-web/src/mini-game-kit/` provides the typed primitives every renderer
composes. The kit lives in `nightcap-web` for AW-253 and will be hoisted to a
shared package once a second game adopts it.

## Performance contract

| Budget | Limit |
|---|---|
| Bundle per package | < 30 KB gzipped |
| Total bundle | < 100 KB uncompressed |
| Mount to first paint | < 100 ms (happy-dom CI gate) |
| Countdown frame rate | 60 fps via `requestAnimationFrame`; degrades to 1 fps under `prefers-reduced-motion` |
| Cumulative layout shift after first paint | 0 |

Budgets are enforced in CI. Bypassing requires an ADR.

## ADR 0003 revisit gate

Already satisfied by AW-225. See
`docs/specs/0055-aw-225-nightcap-web-runtime-connector-scaffold.md` Cloudflare
Revisit Note. AW-253 adds no new Cloudflare-specific surface beyond the
AW-225 scaffold and therefore does not retrigger the gate.

---

# Risks and Unknowns

**Risks**: Durable Objects must remain ephemeral and cannot become a second
session authority. The renderer kit becomes the de-facto standard for future
games and must be designed with that responsibility in mind (small surface,
stable contract, no leaky abstractions).

**Unknowns**: The Cloudflare revisit gate may produce a superseding ADR in a
later task. The current approved default remains Cloudflare.

---

# Open Questions

- Which room abstraction is selected after the revisit gate?
- When does the renderer kit hoist from `nightcap-web/src/mini-game-kit/` to a
  shared `@arcwright/mini-game-kit` package? (Likely at the second game.)
