# Couch Race Rehearsal 1 Blocker Log

- Date: 2026-08-01
- Scope: One two-player Couch Race session on a shared TV and two phones.
- Status: Local fixes and founder-confirmed live beat-transition verification
  are complete for the rehearsal thin slice. Full Couch-specific presentation
  and UX follow-ups remain outside this debugging engagement.
- Tracking: GitHub issue #264, closed as completed on 2026-08-01. No new issues
  were opened.

## PR review follow-up

- The player-input path now aggregates distinct player submissions by the
  current beat. One player's action holds the beat; the second player's
  action advances it once. This prevents two phones acting together from
  skipping `scene`.
- Lobby readiness now reports the registered arc's `min_players`, so the
  shared display no longer hardcodes Couch Race's two-player threshold for
  other arcs.
- The rehearsal display URL carries the host custom token in a URL fragment.
  The display exchanges it for a refreshable Firebase session and exposes a
  `Start case` control. The CLI start script remains a fallback.
- Player and host Firebase sessions retain refresh credentials. The SDK accepts
  a token provider, so authenticated requests obtain a current ID token.
- `make rehearsal-smoke` now exchanges both player tokens, submits both
  actions, asserts the beat remains `pour` after the first action, and asserts
  `pour -> scene` after the second.
- Founder confirmation: the live two-player Couch Race rehearsal transitions
  through the authored beats after the merged fixes. The code and automated
  smoke checks agree with that result.

## Blocker 01: Wrong arc selected by rehearsal scripts

- Timestamp: 08:00:00 local, initial reproduction
- Player count at incident: 0
- Device + OS: Windows 11 workstation, PowerShell
- What happened: Both `scripts/rehearsal.py` and
  `scripts/rehearsal_smoke.py` requested `nightcap-v1` instead of the
  registered Couch Race arc `nightcap-couch-race-v1`.
- What you expected: Rehearsal creation and smoke verification target the
  six-beat Couch Race arc.
- Severity: P1
- Repro steps:
  1. Read `DEFAULT_ARC_ID` in both scripts.
  2. Run the scripts against a configured API.
- Screenshot or video link: N/A
- Root cause: The rehearsal scripts retained the pre-pivot default arc after
  Couch Race was registered.
- Fix: Both defaults now use `nightcap-couch-race-v1`; the contract test
  `tests/test_rehearsal_contracts.py` locks this requirement.
- Verification: The contract test passes, and the API tokenized lobby test
  creates the Couch Race arc with initial beat `pour`.
- Triage destination: Fixed in this remediation; retain in #264.
- New issue link: None. Per scope, tracked in #264.

## Blocker 02: `make rehearsal-start` was not wired to the repo wrapper

- Timestamp: 08:00:00 local, initial reproduction
- Player count at incident: 0
- Device + OS: Windows 11 workstation, PowerShell
- What happened: The start script existed, but the repo `make.cmd` had no
  `rehearsal-start` target. The documented start command therefore returned
  `Unknown target: rehearsal-start`.
- What you expected: The documented command exchanges the host custom token
  for a Firebase ID token and starts the saved rehearsal session.
- Severity: P1
- Repro steps:
  1. Run `make rehearsal-start`.
  2. Observe the unknown-target response.
- Screenshot or video link: N/A
- Root cause: The command dispatch table and help text were not updated when
  `scripts/rehearsal_start.py` was added.
- Fix: Added the `rehearsal-start` dispatch and help entry to `make.cmd`.
- Verification: The wrapper contract test passes. A live start call remains
  gated on Firebase configuration and a running rehearsal stack.
- Triage destination: Fixed in this remediation; retain in #264.
- New issue link: None. Per scope, tracked in #264.

## Blocker 03: Firebase configuration was treated as optional

- Timestamp: 08:00:00 local, initial reproduction
- Player count at incident: 0
- Device + OS: Windows 11 workstation, PowerShell
- What happened: The quickstart described `FIREBASE_WEB_API_KEY` as optional,
  while the API needs Firebase custom-token signing for player joins and host
  start. The local `.env` also lacks `ARCWRIGHT_API_KEY`,
  `FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT`, and provider keys.
- What you expected: Preflight stops before boot with the complete list of
  required configuration, rather than allowing a phone or host action to fail
  later.
- Severity: P1
- Repro steps:
  1. Run `make rehearsal` with the current `.env`.
  2. Observe the exact failure: `blank required keys:
     ARCWRIGHT_API_KEY, FIREBASE_TOKEN_SIGNING_SERVICE_ACCOUNT,
     FIREBASE_WEB_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY`.
  3. Run `make rehearsal-smoke`.
  4. Observe: `ARCWRIGHT_API_KEY must be set for rehearsal-smoke`.
- Screenshot or video link: N/A
- Root cause: The rehearsal preflight only required the API key and provider
  settings, and the quickstart did not describe server-side Firebase signing.
- Fix: `rehearsal.py`, `rehearsal_smoke.py`, and the quickstart now require and
  document the Firebase project, signing service account, and web API key.
- Verification: The corrected preflight failures are reproduced locally.
  Real service verification requires the founder's deployment credentials and
  must not be replaced with placeholders.
- Triage destination: M6 ops for environment setup after this remediation.
- New issue link: None. Per scope, tracked in #264.

## Blocker 04: Lobby join stopped before authenticated player input

- Timestamp: 08:00:00 local, source trace
- Player count at incident: 0
- Device + OS: Windows 11 workstation, source and API tests
- What happened: `POST /v1/lobby-join` returned participant and character data
  but no player token. The dashboard therefore could not authenticate a phone
  for `POST /v1/sessions/{id}/characters/{character_id}/input`.
- What you expected: A phone reaches the waiting lobby with an authenticated
  player path ready for an action after the host starts the session.
- Severity: P1
- Repro steps:
  1. Join through the public lobby endpoint.
  2. Inspect the response and observe no `player_token`.
  3. Follow the waiting screen path and attempt a player action.
- Screenshot or video link: N/A
- Root cause: The public join flow was left at an earlier pre-auth contract;
  the dashboard had no token exchange or player input action.
- Fix: Lobby join now mints a session-scoped Firebase custom token. The
  dashboard exchanges it for an ID token and presents a minimal action submit
  control. The API schema and regression test cover the contract.
- Verification: `TestCreateSession.test_lobby_join_returns_player_token_for_device_session`
  now covers two joins, host start, token claims, an authenticated action, and
  the `pour` to `scene` transition. It passes. The existing live progression
  test also passes.
- Triage destination: Fixed in this remediation; retain in #264.
- New issue link: None. Per scope, tracked in #264.

## Blocker 05: Display and waiting surfaces were still pre-Couch Race

- Timestamp: 08:00:00 local, source trace
- Player count at incident: 0
- Device + OS: Windows 11 workstation, dashboard source
- What happened: `make rehearsal` launches `dashboard`, not `nightcap-web`.
  Its display required four players and showed a generic old lobby state. Its
  waiting screen only waited and had no Couch Race action path.
- What you expected: The shared display becomes ready at two players, shows
  the current Couch Race beat, and phones can submit a functional action.
- Severity: P1
- Repro steps:
  1. Follow the quickstart launch path.
  2. Inspect `dashboard/src/screens/DisplayScreen.tsx` and
     `dashboard/src/screens/WaitingScreen.tsx`.
  3. Compare the flow with the Couch Race systems map's six-beat session.
- Screenshot or video link: N/A
- Root cause: The rehearsal surface was inherited from the older TMST/lobby
  path and had not been adapted to the approved two-player Couch Race thin
  slice.
- Fix: The display threshold is two players and reports `current_beat_id`.
  The waiting screen now submits a generic deterministic action through the
  existing player API. This is intentionally text-fallback functionality, not
  a UI polish pass.
- Verification: Dashboard `npm run build` passes when run with the required
  filesystem access. The first sandboxed Vite run failed before compilation
  because esbuild could not access the config directory. API session and
  character tests plus rehearsal contracts pass: 49 tests passed.
- Triage destination: Fixed for the thin slice; remaining Couch-specific
  presentation, interrogation, claims, Leverage, and minigame UI are outside
  this debugging engagement and remain follow-up work in #264.
- New issue link: None. Per scope, tracked in #264.

## Blocker 07: Firebase bearer token was placed in the waiting URL

- Timestamp: 08:30:00 local, code review
- Player count at incident: 0
- Device + OS: Windows 11 workstation, dashboard source review
- What happened: After joining, the dashboard put the Firebase ID token in
  the `/waiting` query string.
- What you expected: The authenticated phone action path does not expose a
  bearer token through browser history, referrers, or ordinary URL logging.
- Severity: P1
- Repro steps:
  1. Join through the dashboard.
  2. Inspect the redirect URL after Firebase token exchange.
  3. Observe `player_token` in the query string.
- Screenshot or video link: N/A
- Root cause: The first thin-slice implementation used query parameters to
  carry the token across the join-to-waiting navigation.
- Fix: The join screen now stores the ID token in `sessionStorage` under the
  session ID. The waiting screen reads it from storage and no longer puts the
  token in the URL.
- Verification: Dashboard `npm run build` passes after the fix. The source
  review confirms no player token is added to the waiting query parameters.
- Triage destination: Fixed in this remediation; retain in #264.
- New issue link: None. Per scope, tracked in #264.

## Blocker 06: `nightcap-web` is not the rehearsal renderer and is generic

- Timestamp: 08:00:00 local, source trace
- Player count at incident: 0
- Device + OS: Windows 11 workstation, TypeScript source and tests
- What happened: `nightcap-web/src/room.ts`, `runtime.ts`, `worker.ts`,
  `connector.ts`, and `ui.ts` implement a generic session/event renderer.
  Their tests cover the older `nightcap-v1` and generic arrival/clue shape,
  not Couch Race's six beats, interrogation, claims, contradictions, or
  Leverage. The rehearsal script does not launch this package.
- What you expected: The active rehearsal renderer is verified against the
  Couch Race session shape before being used for the hardware run.
- Severity: P1
- Repro steps:
  1. Run `rg -n "nightcap-v1|arrival|clue|nightcap-couch-race-v1" nightcap-web/src`.
  2. Read the `make rehearsal` dashboard launch path.
  3. Compare both with `docs/design/authoring/couch-race-systems-map.md`.
- Screenshot or video link: N/A
- Root cause: Renderer verification followed the pre-pivot generic format;
  the Couch Race renderer integration was never completed.
- Fix: Not expanded in this session. The supported rehearsal path uses the
  dashboard thin slice fixed above, and Couch-specific renderer completion is
  not required to test one action-to-beat transition.
- Verification: Dashboard build passes. No claim is made that `nightcap-web`
  renders full Couch Race content.
- Triage destination: M5 hardening follow-up, tracked only in #264.
- New issue link: None. Per scope, tracked in #264.

## Real-device verification gate

- Required walkthrough: shared TV opens the display URL, two phones join with
  the same code, display shows two players, `make rehearsal-start` returns an
  active session, both phones submit one action, and the display reports the
  next beat.
- Current result: Founder confirmed that a live two-player rehearsal can join,
  start, and transition through the authored beats. The focused automated
  validation also passes: 84 tests, dashboard TypeScript, Ruff, and enforced
  pre-commit checks.
- Close condition for #264: Satisfied by the founder confirmation recorded in
  GitHub issue #264 on 2026-08-01. Detailed device and session metadata was not
  supplied in the confirmation; future rehearsals should continue recording
  those details when available.
