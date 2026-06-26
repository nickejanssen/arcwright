# Mini-game Authoring Guide

This guide is for engine, Nightcap, and third-party developers building a
mini-game on top of Arcwright. It documents the package layout, the renderer
contract, the lifecycle rules, the performance budgets every mini-game ships
against, and a worked example.

For platform context, read first:

- `docs/architecture/03-arc-execution.md` (arc and beat model)
- `docs/decisions/0009-mini-game-runtime-boundary.md` (engine ownership of
  timers, scoring, clue unlocking; renderer ownership of presentation only)
- `docs/specs/0050-aw-253-nightcap-web-mini-game-rendering.md` (the
  renderer architecture and package-local renderer convention)

---

## 1. Package layout

Every mini-game ships as a self-contained directory.

```
nightcap/mini_games/<game-id>/
  manifest.json                  ← lifecycle, version, definition path
  definitions/
    <semver>.json                ← schema-validated definition
  content/                       ← (optional) authored content separated from schema
  assets/                        ← (optional) images, audio, fonts
  client/
    renderer.ts                  ← browser surface renderer
    styles.css                   ← (optional) scoped styles
    renderer.test.ts             ← (optional) co-located tests
  README.md                      ← (recommended) game-author docs
```

The package directory is the unit of authoring. Adding a new mini-game is a
directory drop; you do not edit `nightcap-web/` to register or wire it.

### manifest.json required fields

```json
{
  "schema_version": "1.0",
  "game_id": "your-game-id",
  "title": "Your Game",
  "lifecycle": "draft",
  "current_version": "0.1.0",
  "definition_path": "definitions/0.1.0.json",
  "asset_paths": []
}
```

Lifecycle states: `draft`, `playtest`, `active`, `retired`. Once a definition
reaches `playtest` it is immutable; changes require a new version.

### Definition schema

See `nightcap/mini_games/_fixtures/individual/definitions/0.1.0.json` for a
worked example and the Pydantic schema in
`engine/mini_games/schemas.py` for the authoritative field list.

The renderer reads `authored_content` and `generation_constraints` to drive
its UI. Everything else (timing, validation, scoring, clue unlocking) belongs
to the Python engine.

---

## 2. The renderer contract

Renderers live at `nightcap/mini_games/<game-id>/client/renderer.ts` and
default-export a `MiniGameRenderer` produced by `defineRenderer` from the
`@arcwright/mini-game-kit` module.

```typescript
import {
  defineRenderer,
  useCountdown,
  formatRemaining,
  createSubmissionGuard,
  el,
  on,
  setText,
  setDisabled,
  clearChildren,
  type SurfaceLifecycle,
} from "@arcwright/mini-game-kit";

export default defineRenderer({
  gameId: "your-game-id",

  phone: {
    mount(root, ctx): SurfaceLifecycle {
      // 1. Render initial DOM into `root`
      // 2. Wire up input handlers using createSubmissionGuard
      // 3. Start a countdown via useCountdown
      // 4. Return a lifecycle: { update, handleEvent, unmount }
    },
  },

  sharedDisplay: {
    mount(root, ctx): SurfaceLifecycle { /* ... */ },
  },

  host: {
    mount(root, ctx): SurfaceLifecycle { /* ... */ },
  },
});
```

You do not need to implement every surface. A missing surface mounts an inert
lifecycle and the page degrades gracefully.

### MiniGameContext (`ctx`) surface

| Field | Purpose |
|---|---|
| `surface` | `"phone"`, `"shared_display"`, or `"host"` |
| `sessionId`, `participantId`, `characterId` | Identifiers; do not display participant IDs to other players |
| `state` | The current `MiniGameState` (run id, status, deadline, your submissions) |
| `definition` | The full `MiniGameDefinition` (game schema) |
| `submit(payload)` | Send a submission to Arcwright; engine validates content |
| `onEvent(handler)` | Subscribe to filtered events for this surface |
| `reportPerf(name, value)` | Emit a performance measurement to Arcwright telemetry |

### Lifecycle returned from `mount`

| Method | When called |
|---|---|
| `update(state)` | Status, deadline, or your submissions changed |
| `handleEvent(event)` | A `ContentEvent` was delivered (already audience-filtered) |
| `unmount()` | Renderer is being torn down; clean up timers, listeners, DOM |

---

## 3. Hard rules (every renderer must follow)

1. **Never compute outcomes locally.** No scores, no winner detection, no
   clue selection. The engine owns canonical state. Display only.
2. **Never own time.** Countdowns read `state.deadlineAt`; the engine times
   the run. `useCountdown` enforces this — it reads the system clock against
   a fixed deadline rather than counting down.
3. **`MiniGamePayload` is opaque.** Build the payload object, submit it, and
   wait for the engine's accept/reject. Do not encode game logic into the
   payload (such as a precomputed score).
4. **Never render another player's private content.** The audience filter is
   defense-in-depth; the primary boundary is the scoped player token.
5. **Never reveal clue text on timeout or completion.** Clue delivery comes
   as a separate `private_delivery` event from Arcwright.
6. **No provider names or model strings.** Renderers run in the browser and
   have no business referencing AI providers.

---

## 4. Performance contract

Every mini-game ships against these budgets. CI enforces them.

| Budget | Limit |
|---|---|
| Bundle per package | < 30 KB gzipped |
| Total bundle | < 100 KB uncompressed |
| Mount to first paint | < 100 ms |
| Countdown frame rate | 60 fps via `requestAnimationFrame`; auto-degrades under `prefers-reduced-motion` |
| Cumulative layout shift after first paint | 0 |
| Input latency (tap → visual feedback) | < 16 ms |

The kit primitives (`useCountdown`, `createSubmissionGuard`, the DOM helpers)
are designed so the happy path is the fast path. Avoid:

- `setInterval` for animation (use `useCountdown` or `requestAnimationFrame`)
- `innerHTML` rewrites after mount (use surgical updates via `setText` and
  attribute mutations)
- Synchronous heavy work in event handlers (debounce or defer)
- Layout-triggering CSS properties on animation paths (use `transform`)

---

## 5. Accessibility checklist

The kit and the page shell set up most of these, but renderers must:

- Use `aria-live="polite"` for countdown and tally regions
- Use `aria-live="assertive"` for status changes
- Touch targets must be at least 44 x 44 CSS pixels
- All interactive elements must be reachable via Tab and activated via Enter
  or Space
- Disable animations when `prefers-reduced-motion: reduce` matches (the kit
  helpers handle this automatically; do not re-introduce CSS animations
  without honoring the media query)

---

## 6. Worked example: an individual timed-choice game

```typescript
import {
  defineRenderer,
  useCountdown,
  formatRemaining,
  createSubmissionGuard,
  el,
  on,
  setText,
  setDisabled,
  clearChildren,
  type SurfaceLifecycle,
} from "@arcwright/mini-game-kit";

export default defineRenderer({
  gameId: "tiny-puzzle",

  phone: {
    mount(root, ctx): SurfaceLifecycle {
      const doc = root.ownerDocument;
      clearChildren(root);
      const content = ctx.definition.authored_content as {
        prompt: string;
        choices: string[];
      };

      const status = el(doc, "p", {
        class: "mg-status",
        "aria-live": "assertive",
      }, ["Tap your answer."]);
      const promptNode = el(doc, "h2", {}, [content.prompt]);
      const timer = el(doc, "div", {
        class: "mg-timer",
        "aria-live": "polite",
      }, ["--:--"]);

      const guard = createSubmissionGuard({
        submit: (id, payload) => ctx.submit(payload),
      });

      const buttons: HTMLButtonElement[] = [];
      const choicesList = el(doc, "div", { class: "mg-choices" });
      for (const choice of content.choices) {
        const btn = el(doc, "button", { type: "button" }, [choice]);
        on(btn, "click", async () => {
          if (guard.isPending() || guard.hasSubmitted()) return;
          for (const b of buttons) setDisabled(b, true);
          const result = await guard.submit({ choice });
          if (!result || !result.isAccepted) {
            for (const b of buttons) setDisabled(b, false);
          } else {
            setText(status, "Submitted.");
          }
        });
        buttons.push(btn);
        choicesList.appendChild(btn);
      }

      root.appendChild(status);
      root.appendChild(promptNode);
      root.appendChild(timer);
      root.appendChild(choicesList);

      const countdown = useCountdown({
        deadlineAt: ctx.state.deadlineAt,
        view: doc.defaultView,
        onTick: (remaining) => setText(timer, formatRemaining(remaining)),
      });

      return {
        update(state) {
          if (state.status !== "active") {
            for (const b of buttons) setDisabled(b, true);
            setText(
              status,
              state.status === "timed_out"
                ? "Time ran out."
                : "Round complete.",
            );
          }
        },
        handleEvent() {
          // No per-event UI updates needed; state transitions trigger update().
        },
        unmount() {
          countdown.cancel();
          clearChildren(root);
        },
      };
    },
  },
});
```

---

## 7. Testing your renderer

Co-locate tests with the renderer when possible:

```
nightcap/mini_games/your-game-id/client/renderer.test.ts
```

Use `node:test` and `happy-dom` to mount the renderer against a real DOM:

```typescript
import test from "node:test";
import assert from "node:assert/strict";
import { Window } from "happy-dom";
import renderer from "./renderer.js";

test("phone surface mounts and shows prompt", () => {
  const window = new Window();
  const doc = window.document;
  const root = doc.createElement("section");
  // build a MiniGameContext stub and call renderer.mount(root, ctx)
  // assert DOM contents
});
```

---

## 8. Lifecycle and promotion

| State | Meaning | Mutation rules |
|---|---|---|
| `draft` | Author iteration | Anything mutable |
| `playtest` | Real-user testing | Definition is immutable; new version required for changes |
| `active` | Production | Same as playtest; promote via PR |
| `retired` | No longer used | Reads only; no new runs |

To promote, edit `manifest.json` and submit a PR. CI verifies the definition
schema, asserts the bundle size budgets, and runs the mini-game tests.

---

## 9. References

- `docs/decisions/0009-mini-game-runtime-boundary.md`
- `docs/specs/0050-aw-253-nightcap-web-mini-game-rendering.md`
- `nightcap-web/src/mini-game-kit/` — the kit source
- `nightcap/mini_games/_fixtures/` — three reference renderers
