# AW-219: TypeScript SDK — Event and Input Client

**Status**: Approved

**Author**: Nicolas Janssen | **Date**: 2026-06-18

---

# References

- Architecture: `docs/architecture/09-developer-api.md` §9.4 — canonical SDK surface
- Architecture: `docs/architecture/08-event-system.md` §8.2 — ContentEvent schema
- Architecture: `docs/architecture/08-event-system.md` §8.6 — SSE wire format
- Source of truth (event types): `engine/events/models.py`
- Source of truth (REST schemas): `api/schemas/__init__.py`
- SSE endpoint implementation: `api/routers/events.py`
- Auth implementation: `api/auth/__init__.py`
- SDK build config: `sdk/package.json`, `sdk/tsconfig.json`
- Related spec (immediately prior): `docs/specs/0043-aw-221-narrator-bridge-on-resume.md`
- GitHub issue: #72

---

# Overview

Implements the TypeScript game-client SDK (`@arcwright/sdk`). The SDK is a typed
HTTP/SSE client and nothing else — no arc logic, no Firebase knowledge, no game rules.
It wraps four server interactions: subscribing to the live event stream, submitting
player input, fetching the player's character state, and disconnecting.

---

# Decisions Locked Before Implementation

## D1: SSE auth mechanism

`api/routers/events.py` comment (added AW-217): *"query-param trust is removed as of
AW-217."* `require_player_or_host_jwt` uses `HTTPBearer`, which reads exclusively from
the `Authorization: Bearer` header. The browser-native `EventSource` API cannot send
custom headers and is therefore incompatible.

**Decision:** Use `fetch()` with a `ReadableStream` body reader and manual SSE line
parsing. No new npm dependencies. The SSE wire format (`data: <json>\n\n`) is simple
enough to parse inline.

Note: `docs/architecture/08-event-system.md §8.6` states "wraps the browser's native
EventSource API" — that text predates AW-217 and is stale. This spec supersedes it.

## D2: Constructor signature and `character_id` source

The server's `join_session` endpoint returns a Firebase custom token, not a Firebase
ID token. `api/auth/__init__.py` calls `firebase_auth.verify_id_token()`, which
rejects custom tokens. Token exchange (custom → ID) is the caller's responsibility
and is explicitly out of scope for this SDK.

The JWT claims (`JwtClaims`) carry `player_id` (participant UUID) but not
`character_id`. The SDK cannot derive `character_id` from the token alone.

**Decision:** The caller resolves all auth and character assignment externally before
constructing the SDK:
1. Caller calls `GET /v1/sessions/{id}/join?token={rawJoinToken}` → receives
   `{ character_id, player_token }`.
2. Caller exchanges `player_token` (Firebase custom token) for a Firebase ID token
   via `signInWithCustomToken()` in the Firebase JS SDK.
3. Caller constructs `ArcwrightClient(sessionId, idToken, characterId, baseUrl)`.

The SDK treats `playerToken` as an opaque bearer string. This keeps the SDK
auth-provider-agnostic: Monster RPG, enterprise, and third-party developers can
supply tokens from any auth system without fighting Firebase-specific SDK internals.

Constructor signature (extends the 3-param sketch in `docs/architecture/09-developer-api.md §9.4`):
```ts
constructor(sessionId: string, playerToken: string, characterId: string, baseUrl: string)
```

---

# In Scope

- `sdk/src/types.ts` — hand-written TypeScript types aligned with Python source of truth:
  - `AudienceTarget` (string union)
  - `EventCategory` (string union)
  - `PresentationHints`
  - `ContentEvent`
  - `PlayerInput`
  - `CharacterDetail`

- `sdk/src/index.ts` — `ArcwrightClient` class:
  - `constructor(sessionId: string, playerToken: string, characterId: string, baseUrl: string)`
  - `onEvent(callback: (event: ContentEvent) => void): () => void`
  - `submitInput(characterId: string, input: PlayerInput): Promise<void>`
  - `getMyCharacter(): Promise<CharacterDetail>`
  - `disconnect(): void`
  - Re-exports all public types from `sdk/src/types.ts`.

---

# Out of Scope

- Code generation or OpenAPI schema sync (deferred).
- Shared display or host-side SDK surface (game client only at MVP).
- Retry logic beyond a single reconnect on SSE stream drop.
- Arc definition or beat graph knowledge.
- Knowledge graph queries or assertions.
- Firebase token exchange (caller's responsibility).
- Test runner (no vitest/jest added in this task; see Test Plan).
- CommonJS output (ESM only per `tsconfig.json`).

---

# Acceptance Criteria

- [ ] AC1: `ArcwrightClient` exposes `onEvent`, `submitInput`, `getMyCharacter`, and
  `disconnect`. All four methods exist and are callable.
- [ ] AC2: Public SDK types cover:
  - `ContentEvent` — all fields: `event_id`, `session_id`, `timestamp`, `category`,
    `event_type`, `actor_id`, `target_audience`, `target_player_id`, `payload`,
    `presentation_hints`, `sequence_number`.
  - `PlayerInput` — `kind` (`'action' | 'dialogue'`), `content`.
  - `CharacterDetail` — `session_id`, `character_id`, `participant_id`, `surface_type`,
    `is_ai_controlled`.
  - `PresentationHints` — all fields.
  - No `any` in any public interface. `payload` uses `Record<string, unknown>`.
- [ ] AC3: `npm run typecheck` and `npm run build` pass without errors. `dist/index.js`
  and `dist/index.d.ts` exist after build. No arc logic in any SDK file.

---

# Implementation Notes

## `sdk/src/types.ts`

Hand-aligned with `engine/events/models.py` and `api/schemas/__init__.py`. UUIDs are
`string` (JSON serialises them as strings). `datetime` is `string` (ISO 8601). Python
`dict` fields become `Record<string, unknown>`. Python enums become string literal unions.

```ts
export type AudienceTarget =
  | 'all'
  | 'host_only'
  | 'specific_player'
  | 'shared_display';

export type EventCategory =
  | 'narrative'
  | 'character_dialogue'
  | 'private_delivery'
  | 'acknowledgement'
  | 'state_transition'
  | 'input_request'
  | 'system';

export interface PresentationHints {
  emotion: string | null;
  urgency: string | null;
  voice_hint: string | null;
  animation_hint: string | null;
  lighting_hint: string | null;
  pause_before_ms: number;
}

export interface ContentEvent {
  event_id: string;
  session_id: string;
  timestamp: string;
  category: EventCategory;
  event_type: string;
  actor_id: string | null;
  target_audience: AudienceTarget;
  target_player_id: string | null;
  payload: Record<string, unknown>;
  presentation_hints: PresentationHints;
  sequence_number: number;
}

export interface PlayerInput {
  kind: 'action' | 'dialogue';
  content: string;
}

export interface CharacterDetail {
  session_id: string;
  character_id: string;
  participant_id: string;
  surface_type: string;
  is_ai_controlled: boolean;
}
```

## `sdk/src/index.ts` — SSE implementation

`onEvent` connects using `fetch()` with `Authorization: Bearer <playerToken>`. On
connect, passes `?since=<lastSequenceNumber>` (tracked internally, starts at 0) so
the server replays any missed events on reconnect. Reads `response.body` as a
`ReadableStream<Uint8Array>`, decodes with `TextDecoder`, splits on `\n\n`, extracts
`data:` lines, JSON-parses, updates `_lastSequenceNumber`, and calls `callback`.

Single reconnect: if the stream ends unexpectedly and `_connected` is still `true`,
the implementation re-calls `fetch()` once with the current `_lastSequenceNumber`.

`disconnect()` sets `_connected = false` and cancels the reader. Reconnect guard
checks `_connected` before retrying.

`submitInput` — `POST /v1/sessions/{sessionId}/characters/{characterId}/input` with
`Content-Type: application/json` and `Authorization: Bearer <playerToken>`. Throws on
non-2xx.

`getMyCharacter` — `GET /v1/sessions/{sessionId}/characters/{characterId}` with
`Authorization: Bearer <playerToken>`. Returns parsed `CharacterDetail`. Throws on
non-2xx.

---

# Test Plan

No test runner (`vitest`, `jest`) is present in `sdk/package.json`. Adding one
requires a devDependency change that is tracked as a separate decision. For this task,
the minimum bar is:

- `npm run typecheck` passes with no errors.
- `npm run build` passes; `dist/index.js` and `dist/index.d.ts` are emitted.

Type correctness for `ContentEvent`, `CharacterDetail`, and `PlayerInput` is enforced
at compile time by strict TypeScript — no runtime test is needed for type alignment.

The PR description must include the full terminal output of `npm run typecheck` and
`npm run build`.

---

# Risks and Unknowns

**Risks:**
- `moduleResolution: Bundler` in `tsconfig.json` requires import paths to be explicit
  (`.ts` extension or directory index). `sdk/src/index.ts` must import types with the
  correct resolution strategy.
- SSE reconnect logic must guard against a tight loop if the server rejects the token
  (401/403). The single-reconnect design avoids this: only one retry, no loop.

**Unknowns:**
- None open at spec time. Both pre-implementation decisions are resolved above.

---

# Open Questions

- None. All questions resolved during codebase review and product sign-off.
