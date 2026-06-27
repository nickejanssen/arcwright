# Nightcap Rehearsal Lobby Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a bare-bones lobby experience — shared display (TV/screen) + player phone join flow — sufficient for the June 29 Nightcap Rehearsal 1.

**Architecture:** Python backend gains two new public endpoints (lobby state + lobby-join) and a new `join_code` column on sessions. The React dashboard gains three screens routed by URL: `/display/<session_id>` (shared TV display), `/join` (player phone), and `/waiting` (post-join confirmation). No Firebase auth is used for the lobby — all lobby endpoints are public. Vite proxies `/v1/*` to port 8000 so there are no CORS issues in dev or via cloudflared tunnel.

**Tech Stack:** Python 3.11+ / FastAPI / SQLAlchemy async / Alembic on the backend. React 18 / TypeScript / Vite 8 / plain fetch + CSS on the frontend. No React Router (URL parsed directly). No additional npm packages beyond what is already installed.

**User decisions (already made):**
- "Build a bare-bones dashboard by tomorrow." — scope is lobby only, not full game UI.
- "Users see Nightcap running on the tv or computer. They scan a QR code or go to a link on the screen and use a code to join. As people join, their character shows up on the screen. Some music is playing. On players' phones they see 'You're in! We are waiting on everyone else to join.'"
- Rehearsal date is June 29, 2026.
- Firebase auth not required for Rehearsal 1.

---

## File Structure

**New files:**
- `migrations/versions/0004_add_lobby_fields.py` — Alembic migration: `join_code` on sessions, `display_name` on session_participants
- `api/routers/lobby.py` — public lobby endpoints (GET lobby state, POST lobby-join)
- `dashboard/index.html` — Vite HTML entry
- `dashboard/src/main.tsx` — React DOM root
- `dashboard/src/App.tsx` — URL-based router (display / join / waiting)
- `dashboard/src/api/lobby.ts` — fetch wrappers for lobby endpoints
- `dashboard/src/screens/DisplayScreen.tsx` — shared TV display
- `dashboard/src/screens/JoinScreen.tsx` — player phone join form
- `dashboard/src/screens/WaitingScreen.tsx` — post-join confirmation
- `dashboard/src/index.css` — dark theme CSS variables

**Modified files:**
- `engine/db/orm.py` — add `join_code: Mapped[Optional[str]]` to Session, `display_name: Mapped[Optional[str]]` to SessionParticipant
- `engine/session/models.py` — add `join_code: Optional[str] = None` to Session pydantic
- `engine/session/service.py` — generate join_code in `create_session`; add `lobby_join` method
- `api/schemas/__init__.py` — add `LobbyStateResponse`, `LobbyJoinRequest`, `LobbyJoinResponse`
- `api/main.py` — register lobby router; add CORS middleware
- `dashboard/vite.config.ts` — add proxy config for `/v1` → `http://localhost:8000`

---

### Task 1: DB schema + Alembic migration

**Goal:** Add `join_code` to sessions and `display_name` to session_participants, with ORM + pydantic updates so the service layer can use them.

**Files:**
- Create: `migrations/versions/0004_add_lobby_fields.py`
- Modify: `engine/db/orm.py` (Session class line ~414, SessionParticipant class line ~473)
- Modify: `engine/session/models.py` (Session pydantic line ~57)
- Modify: `engine/session/service.py` (`create_session` around line 101, `_orm_session_to_pydantic` around line 494)

**Acceptance Criteria:**
- [ ] `alembic upgrade head` runs without error against the live Postgres container
- [ ] `alembic downgrade -1` reverses the migration without error
- [ ] `Session.join_code` is accessible on the ORM object after `create_session`
- [ ] `SessionParticipant.display_name` is nullable Text in the DB

**Verify:** `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` → no errors

**Steps:**

- [ ] **Step 1: Add `join_code` to `Session` ORM class in `engine/db/orm.py`**

  In `engine/db/orm.py`, find the `Session` class (line ~414). After the existing `player_count` column, add:

  ```python
  join_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True, unique=True)
  ```

  The full Session class mapped columns block becomes (relevant excerpt only — add after `player_count`):
  ```python
  player_count: Mapped[int] = mapped_column(Integer, nullable=False)
  join_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True, unique=True)
  ```

- [ ] **Step 2: Add `display_name` to `SessionParticipant` ORM class in `engine/db/orm.py`**

  In `engine/db/orm.py`, find the `SessionParticipant` class (line ~473). After `is_ai_controlled`, add:

  ```python
  display_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  ```

- [ ] **Step 3: Add `join_code` to `Session` pydantic model in `engine/session/models.py`**

  In `engine/session/models.py`, update the `Session` class (line ~57):

  ```python
  class Session(BaseModel):
      session_id: UUID
      arc_id: str
      status: SessionStatus
      host_account_id: UUID
      created_at: datetime
      started_at: Optional[datetime] = None
      completed_at: Optional[datetime] = None
      current_beat_id: str
      quality_tier: QualityTier
      player_count: int
      join_code: Optional[str] = None
  ```

- [ ] **Step 4: Update `_orm_session_to_pydantic` in `engine/session/service.py`**

  Find `_orm_session_to_pydantic` at line ~494. Update:

  ```python
  def _orm_session_to_pydantic(orm: OrmSession) -> Session:
      return Session(
          session_id=orm.session_id,
          arc_id=orm.arc_id,
          status=SessionStatus(orm.status),
          host_account_id=orm.host_account_id,
          created_at=orm.created_at,
          started_at=orm.started_at,
          completed_at=orm.completed_at,
          current_beat_id=orm.current_beat_id,
          quality_tier=QualityTier(orm.quality_tier),
          player_count=orm.player_count,
          join_code=orm.join_code,
      )
  ```

- [ ] **Step 5: Generate join_code in `create_session` in `engine/session/service.py`**

  Add import at the top of the file (near existing `import secrets`):
  ```python
  import random
  import string
  ```

  Add a module-level helper after the existing `_DEFAULT_INITIAL_BEAT_ID` constant:
  ```python
  def _generate_join_code() -> str:
      return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
  ```

  In `create_session`, update the `OrmSession(...)` constructor call (around line 101) to include `join_code`:
  ```python
  orm_session = OrmSession(
      session_id=uuid4(),
      arc_id=arc_id,
      status=SessionStatus.created.value,
      host_account_id=host_account_id,
      created_at=datetime.now(tz=timezone.utc),
      current_beat_id=_DEFAULT_INITIAL_BEAT_ID,
      quality_tier=quality_tier.value,
      player_count=0,
      join_code=_generate_join_code(),
  )
  ```

- [ ] **Step 6: Write the Alembic migration**

  Create `migrations/versions/0004_add_lobby_fields.py`:

  ```python
  """add_lobby_fields

  Revision ID: 0004_add_lobby_fields
  Revises: 0003_add_mini_game_tables
  Create Date: 2026-06-27

  Adds join_code to sessions and display_name to session_participants
  for the Nightcap rehearsal lobby (Rehearsal 1, AW-231).
  """

  import sqlalchemy as sa
  from alembic import op

  revision = "0004_add_lobby_fields"
  down_revision = "0003_add_mini_game_tables"
  branch_labels = None
  depends_on = None


  def upgrade() -> None:
      op.add_column(
          "sessions",
          sa.Column("join_code", sa.Text(), nullable=True),
      )
      op.create_unique_constraint(
          "uq_sessions_join_code", "sessions", ["join_code"]
      )
      op.add_column(
          "session_participants",
          sa.Column("display_name", sa.Text(), nullable=True),
      )


  def downgrade() -> None:
      op.drop_column("session_participants", "display_name")
      op.drop_constraint("uq_sessions_join_code", "sessions", type_="unique")
      op.drop_column("sessions", "join_code")
  ```

- [ ] **Step 7: Run the migration**

  ```powershell
  alembic upgrade head
  ```

  Expected output: lines like `Running upgrade 0003_add_mini_game_tables -> 0004_add_lobby_fields` with no tracebacks.

  Verify downgrade works:
  ```powershell
  alembic downgrade -1
  alembic upgrade head
  ```

  Both should complete without error.

- [ ] **Step 8: Commit**

  ```powershell
  git add engine/db/orm.py engine/session/models.py engine/session/service.py migrations/versions/0004_add_lobby_fields.py
  git commit -m "feat(lobby): add join_code to sessions and display_name to participants"
  ```

---

### Task 2: Lobby API endpoints

**Goal:** Expose two public (no auth) endpoints — `GET /v1/sessions/{id}/lobby` for the display to poll, and `POST /v1/lobby-join` for players to join by name + code — plus update `api/main.py` with CORS and the new router.

**Files:**
- Create: `api/routers/lobby.py`
- Modify: `api/schemas/__init__.py` (add 3 new schema classes at end of file)
- Modify: `api/main.py` (add CORS, register lobby router)

**Acceptance Criteria:**
- [ ] `GET /v1/sessions/{id}/lobby` returns `{join_code, status, player_count, players}` without any auth header
- [ ] `POST /v1/lobby-join` with `{"name": "Alice", "join_code": "ABC123"}` returns `{participant_id, session_id, display_name}` and increments `player_count` on the session
- [ ] `POST /v1/lobby-join` with wrong join_code returns HTTP 404
- [ ] `curl.exe http://localhost:8000/v1/sessions/<id>/lobby` works from PowerShell after uvicorn restart

**Verify:** With uvicorn running: `curl.exe -s http://localhost:8000/v1/sessions/<session-id>/lobby` → JSON with `join_code` field

**Steps:**

- [ ] **Step 1: Add lobby schemas to `api/schemas/__init__.py`**

  Append to the end of `api/schemas/__init__.py`:

  ```python
  class LobbyPlayerEntry(BaseModel):
      participant_id: UUID
      display_name: Optional[str] = None


  class LobbyStateResponse(BaseModel):
      session_id: UUID
      join_code: Optional[str]
      status: str
      player_count: int
      players: list[LobbyPlayerEntry]


  class LobbyJoinRequest(BaseModel):
      name: str = Field(min_length=1, max_length=64)
      join_code: str = Field(min_length=1, max_length=8)


  class LobbyJoinResponse(BaseModel):
      participant_id: UUID
      session_id: UUID
      display_name: str
  ```

- [ ] **Step 2: Add `lobby_join` service method to `engine/session/service.py`**

  Add the following imports at the top of `engine/session/service.py` (after the existing imports, the `Character` ORM class needs to be imported):

  ```python
  from engine.db.orm import (
      Account,
      ArcBeatState,
      Character,
      Event,
  )
  ```

  (Check first: if `Character` is already imported, skip adding it.)

  Then add a new method to the `SessionService` class, after `validate_join_token`:

  ```python
  async def lobby_join(
      self,
      db: AsyncSession,
      *,
      join_code: str,
      display_name: str,
  ) -> SessionParticipant:
      """Find a session by join_code and add a named player.

      Returns the new SessionParticipant. Raises SessionNotFoundError if
      no session matches the code, or SessionStateError if the session is
      in a terminal state.
      """
      result = await db.execute(
          select(OrmSession).where(OrmSession.join_code == join_code)
      )
      orm = result.scalars().first()
      if orm is None:
          raise SessionNotFoundError(f"No session with join_code {join_code!r}")
      if orm.status in (
          SessionStatus.completed.value,
          SessionStatus.abandoned.value,
      ):
          raise SessionStateError(
              f"Cannot join session in status {orm.status!r}"
          )

      # Create a placeholder character row to satisfy the FK constraint.
      character = Character(behavior_profile={})
      db.add(character)
      await db.flush()

      participant = OrmParticipant(
          participant_id=uuid4(),
          session_id=orm.session_id,
          character_id=character.character_id,
          join_token=secrets.token_urlsafe(32),
          surface_type="player",
          is_ai_controlled=False,
          display_name=display_name,
      )
      db.add(participant)
      orm.player_count += 1
      await db.flush()
      return _orm_participant_to_pydantic(participant)
  ```

  Also update `_orm_participant_to_pydantic` to include `display_name` so it doesn't crash when the new field exists on the ORM object:

  ```python
  def _orm_participant_to_pydantic(orm: OrmParticipant) -> SessionParticipant:
      return SessionParticipant(
          participant_id=orm.participant_id,
          session_id=orm.session_id,
          character_id=orm.character_id,
          account_id=orm.account_id,
          join_token=orm.join_token,
          surface_type=orm.surface_type,
          is_ai_controlled=orm.is_ai_controlled,
      )
  ```

  (The `display_name` field is on the ORM but not the pydantic `SessionParticipant` model — the lobby router uses the raw ORM participant. No pydantic model change needed here.)

- [ ] **Step 3: Create `api/routers/lobby.py`**

  ```python
  """Public lobby endpoints for the Nightcap rehearsal lobby.

  No auth required — these are public endpoints for the display screen
  and player phones. Production auth is deferred to M5 (AW-269).
  """

  from __future__ import annotations

  from uuid import UUID

  from fastapi import APIRouter, HTTPException
  from sqlalchemy import select
  from sqlalchemy.ext.asyncio import AsyncSession
  from fastapi import Depends

  from api.schemas import (
      LobbyJoinRequest,
      LobbyJoinResponse,
      LobbyPlayerEntry,
      LobbyStateResponse,
  )
  from engine.db import get_async_session
  from engine.db.orm import Session as OrmSession, SessionParticipant as OrmParticipant
  from engine.session.service import (
      SessionNotFoundError,
      SessionStateError,
      _session_service,
  )

  router = APIRouter(tags=["lobby"])


  @router.get("/sessions/{session_id}/lobby", response_model=LobbyStateResponse)
  async def get_lobby_state(
      session_id: UUID,
      db: AsyncSession = Depends(get_async_session),
  ) -> LobbyStateResponse:
      """Return the current lobby state for the shared display."""
      orm = await db.get(OrmSession, session_id)
      if orm is None:
          raise HTTPException(status_code=404, detail="Session not found")

      result = await db.execute(
          select(OrmParticipant).where(
              OrmParticipant.session_id == session_id,
              OrmParticipant.surface_type == "player",
          )
      )
      participants = result.scalars().all()

      return LobbyStateResponse(
          session_id=session_id,
          join_code=orm.join_code,
          status=orm.status,
          player_count=orm.player_count,
          players=[
              LobbyPlayerEntry(
                  participant_id=p.participant_id,
                  display_name=p.display_name,
              )
              for p in participants
          ],
      )


  @router.post("/lobby-join", response_model=LobbyJoinResponse, status_code=201)
  async def lobby_join(
      body: LobbyJoinRequest,
      db: AsyncSession = Depends(get_async_session),
  ) -> LobbyJoinResponse:
      """Join a session by name and join_code. Public endpoint."""
      try:
          participant = await _session_service.lobby_join(
              db,
              join_code=body.join_code.upper(),
              display_name=body.name,
          )
      except SessionNotFoundError:
          raise HTTPException(status_code=404, detail="Invalid join code")
      except SessionStateError as exc:
          raise HTTPException(status_code=409, detail=str(exc))

      return LobbyJoinResponse(
          participant_id=participant.participant_id,
          session_id=participant.session_id,
          display_name=body.name,
      )
  ```

- [ ] **Step 4: Register lobby router and add CORS in `api/main.py`**

  Replace the full content of `api/main.py` with:

  ```python
  """Arcwright REST API — FastAPI application entry point.

  Architecture: docs/architecture/09-developer-api.md §9.2.
  """

  from __future__ import annotations

  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  from fastapi.responses import JSONResponse

  from api.routers import characters, costs, events, knowledge, mini_games, sessions
  from api.routers import lobby


  def create_app() -> FastAPI:
      application = FastAPI(title="Arcwright API", version="0.1.0")

      application.add_middleware(
          CORSMiddleware,
          allow_origins=["*"],
          allow_methods=["*"],
          allow_headers=["*"],
      )

      @application.get("/health")
      async def health() -> JSONResponse:
          return JSONResponse({"status": "ok"})

      application.include_router(sessions.router, prefix="/v1")
      application.include_router(events.router, prefix="/v1")
      application.include_router(characters.router, prefix="/v1")
      application.include_router(knowledge.router, prefix="/v1")
      application.include_router(costs.router, prefix="/v1")
      application.include_router(mini_games.router, prefix="/v1")
      application.include_router(lobby.router, prefix="/v1")
      return application


  app = create_app()
  ```

- [ ] **Step 5: Restart uvicorn and smoke-test**

  In Terminal 3 (uvicorn), press Ctrl+C to stop, then restart:
  ```powershell
  uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
  ```

  Create a test session (replace `<api-key>` with value of `ARCWRIGHT_API_KEY` from `.env` — or set it first if missing):
  ```powershell
  # If ARCWRIGHT_API_KEY is not set in .env, add a line: ARCWRIGHT_API_KEY=rehearsal-dev-key
  # Then restart uvicorn.

  curl.exe -s -X POST http://localhost:8000/v1/sessions `
    -H "Content-Type: application/json" `
    -H "X-Api-Key: <value-of-ARCWRIGHT_API_KEY-from-env>" `
    -d '{"arc_id": "nightcap"}'
  ```

  Note the `session_id` from the response. Then:
  ```powershell
  curl.exe -s http://localhost:8000/v1/sessions/<session-id>/lobby
  ```
  Expected: `{"session_id":"...","join_code":"ABC123","status":"created","player_count":0,"players":[]}`

  Test lobby-join:
  ```powershell
  curl.exe -s -X POST http://localhost:8000/v1/lobby-join `
    -H "Content-Type: application/json" `
    -d '{"name": "Alice", "join_code": "ABC123"}'
  ```
  Expected: `{"participant_id":"...","session_id":"...","display_name":"Alice"}`

  Then poll lobby again — `player_count` should be 1 and `players` should include Alice.

- [ ] **Step 6: Add `ARCWRIGHT_API_KEY` to `.env` if missing**

  Open `.env` at repo root. If `ARCWRIGHT_API_KEY` is missing, add:
  ```
  ARCWRIGHT_API_KEY=rehearsal-dev-key
  ```
  Restart uvicorn after saving.

- [ ] **Step 7: Commit**

  ```powershell
  git add api/routers/lobby.py api/schemas/__init__.py api/main.py engine/session/service.py
  git commit -m "feat(lobby): public lobby state and lobby-join endpoints"
  ```

---

### Task 3: Dashboard scaffold

**Goal:** Create the Vite entry files (index.html, main.tsx), a URL-based router in App.tsx, the Vite proxy config, and the API client module — so all three screens can be imported and routed correctly.

**Files:**
- Create: `dashboard/index.html`
- Create: `dashboard/src/main.tsx`
- Create: `dashboard/src/App.tsx`
- Create: `dashboard/src/index.css`
- Create: `dashboard/src/api/lobby.ts`
- Modify: `dashboard/vite.config.ts`

**Acceptance Criteria:**
- [ ] `npm run dev` in `dashboard/` starts without error
- [ ] `http://localhost:5173/` renders text (not a blank page or 404)
- [ ] `http://localhost:5173/display/test-id` renders different text than `/`
- [ ] `npm run typecheck` passes with 0 errors

**Verify:** `npm run typecheck` → `Found 0 errors.`

**Steps:**

- [ ] **Step 1: Update `dashboard/vite.config.ts` to add the API proxy**

  Replace the content of `dashboard/vite.config.ts`:

  ```typescript
  import { defineConfig } from "vite";
  import react from "@vitejs/plugin-react";

  export default defineConfig({
    plugins: [react()],
    server: {
      proxy: {
        "/v1": {
          target: "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
  });
  ```

- [ ] **Step 2: Create `dashboard/index.html`**

  ```html
  <!doctype html>
  <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Nightcap</title>
    </head>
    <body>
      <div id="root"></div>
      <script type="module" src="/src/main.tsx"></script>
    </body>
  </html>
  ```

- [ ] **Step 3: Create `dashboard/src/index.css`**

  ```css
  :root {
    --bg: #0a0a0f;
    --surface: #13131a;
    --border: #2a2a3a;
    --accent: #c8a96e;
    --accent-dim: #7a6540;
    --text: #e8e4dc;
    --text-muted: #8a8070;
    --red: #c84a4a;
    --code-size: clamp(3rem, 8vw, 7rem);
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  html, body, #root {
    width: 100%;
    height: 100%;
    background: var(--bg);
    color: var(--text);
    font-family: "Georgia", serif;
  }

  button {
    cursor: pointer;
    font-family: inherit;
  }

  input {
    font-family: inherit;
  }
  ```

- [ ] **Step 4: Create `dashboard/src/api/lobby.ts`**

  ```typescript
  const BASE = "/v1";

  export interface LobbyPlayer {
    participant_id: string;
    display_name: string | null;
  }

  export interface LobbyState {
    session_id: string;
    join_code: string | null;
    status: string;
    player_count: number;
    players: LobbyPlayer[];
  }

  export interface LobbyJoinResult {
    participant_id: string;
    session_id: string;
    display_name: string;
  }

  export async function fetchLobbyState(sessionId: string): Promise<LobbyState> {
    const res = await fetch(`${BASE}/sessions/${sessionId}/lobby`);
    if (!res.ok) throw new Error(`Lobby fetch failed: ${res.status}`);
    return res.json() as Promise<LobbyState>;
  }

  export async function joinLobby(
    name: string,
    joinCode: string
  ): Promise<LobbyJoinResult> {
    const res = await fetch(`${BASE}/lobby-join`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, join_code: joinCode.toUpperCase() }),
    });
    if (res.status === 404) throw new Error("Invalid join code. Check the screen and try again.");
    if (!res.ok) throw new Error(`Join failed: ${res.status}`);
    return res.json() as Promise<LobbyJoinResult>;
  }
  ```

- [ ] **Step 5: Create `dashboard/src/App.tsx`**

  The router parses `window.location.pathname` to determine which screen to show. No React Router needed.

  ```typescript
  import { useEffect, useState } from "react";
  import DisplayScreen from "./screens/DisplayScreen";
  import JoinScreen from "./screens/JoinScreen";
  import WaitingScreen from "./screens/WaitingScreen";

  function parseRoute(): { screen: "display" | "join" | "waiting" | "home"; sessionId?: string } {
    const path = window.location.pathname;
    const displayMatch = path.match(/^\/display\/([^/]+)/);
    if (displayMatch) return { screen: "display", sessionId: displayMatch[1] };
    if (path.startsWith("/join")) return { screen: "join" };
    if (path.startsWith("/waiting")) return { screen: "waiting" };
    return { screen: "home" };
  }

  export default function App() {
    const [route] = useState(parseRoute);

    useEffect(() => {
      document.title = "Nightcap";
    }, []);

    if (route.screen === "display" && route.sessionId) {
      return <DisplayScreen sessionId={route.sessionId} />;
    }
    if (route.screen === "join") {
      return <JoinScreen />;
    }
    if (route.screen === "waiting") {
      return <WaitingScreen />;
    }
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
        <p style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
          Navigate to /display/&lt;session-id&gt; or /join
        </p>
      </div>
    );
  }
  ```

- [ ] **Step 6: Create `dashboard/src/main.tsx`**

  ```typescript
  import { StrictMode } from "react";
  import { createRoot } from "react-dom/client";
  import "./index.css";
  import App from "./App";

  const root = document.getElementById("root");
  if (!root) throw new Error("No #root element found");
  createRoot(root).render(
    <StrictMode>
      <App />
    </StrictMode>
  );
  ```

- [ ] **Step 7: Remove `.gitkeep` from `dashboard/src/`**

  ```powershell
  Remove-Item dashboard/src/.gitkeep
  ```

- [ ] **Step 8: Run typecheck and dev server**

  ```powershell
  cd dashboard
  npm run typecheck
  ```
  Expected: `Found 0 errors.` (screens don't exist yet, so this may show import errors — that's OK, screens are created in Tasks 4 and 5. If there are only "cannot find module" errors for the screen imports, that's expected and will be fixed by the next tasks.)

  ```powershell
  npm run dev
  ```
  Open `http://localhost:5173/` — should show the "Navigate to /display/..." message rather than a blank page.

- [ ] **Step 9: Commit**

  ```powershell
  git add dashboard/index.html dashboard/src/main.tsx dashboard/src/App.tsx dashboard/src/index.css dashboard/src/api/lobby.ts dashboard/vite.config.ts
  git commit -m "feat(dashboard): scaffold — Vite entry, router, API client, base CSS"
  ```

---

### Task 4: Display screen

**Goal:** Build the shared TV display — join code in large text, QR code, live player list that updates every 2 seconds, dark atmospheric styling.

**Files:**
- Create: `dashboard/src/screens/DisplayScreen.tsx`

**Acceptance Criteria:**
- [ ] Navigating to `http://localhost:5173/display/<valid-session-id>` shows the join code and QR code
- [ ] The player list updates within 3 seconds of a new player joining via `POST /v1/lobby-join`
- [ ] The QR code encodes `${window.location.origin}/join?code=<join_code>`
- [ ] When `player_count` is 0, shows "Waiting for players to arrive..."
- [ ] When players join, their names appear one per line
- [ ] No console errors when running

**Verify:** Open `http://localhost:5173/display/<session-id>` in Chrome — join code visible, QR code image loads, player list updates after joining via curl.

**Steps:**

- [ ] **Step 1: Create `dashboard/src/screens/DisplayScreen.tsx`**

  ```typescript
  import { useEffect, useRef, useState } from "react";
  import { fetchLobbyState, LobbyState } from "../api/lobby";

  interface Props {
    sessionId: string;
  }

  export default function DisplayScreen({ sessionId }: Props) {
    const [lobby, setLobby] = useState<LobbyState | null>(null);
    const [error, setError] = useState<string | null>(null);
    const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

    useEffect(() => {
      async function poll() {
        try {
          const state = await fetchLobbyState(sessionId);
          setLobby(state);
          setError(null);
        } catch (e) {
          setError(e instanceof Error ? e.message : "Connection error");
        }
      }

      poll();
      intervalRef.current = setInterval(poll, 2000);
      return () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
      };
    }, [sessionId]);

    if (error) {
      return (
        <div style={styles.centered}>
          <p style={{ color: "var(--red)", fontSize: "1.2rem" }}>{error}</p>
          <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
            Make sure the engine is running at localhost:8000
          </p>
        </div>
      );
    }

    if (!lobby) {
      return (
        <div style={styles.centered}>
          <p style={{ color: "var(--text-muted)", fontStyle: "italic" }}>Connecting...</p>
        </div>
      );
    }

    const joinUrl = lobby.join_code
      ? `${window.location.origin}/join?code=${lobby.join_code}`
      : null;

    return (
      <div style={styles.root}>
        {/* Header */}
        <div style={styles.header}>
          <span style={styles.brand}>NIGHTCAP</span>
          <span style={styles.tagline}>A Murder Mystery</span>
        </div>

        {/* Main content — two column layout */}
        <div style={styles.main}>
          {/* Left: QR + code */}
          <div style={styles.joinPanel}>
            <p style={styles.joinLabel}>JOIN THE GAME</p>

            {joinUrl && (
              <img
                src={`https://api.qrserver.com/v1/create-qr-code/?size=220x220&bgcolor=0a0a0f&color=c8a96e&data=${encodeURIComponent(joinUrl)}`}
                alt="QR code to join"
                style={styles.qr}
              />
            )}

            {lobby.join_code ? (
              <div style={styles.codeBlock}>
                <p style={styles.codeLabel}>or enter code</p>
                <p style={styles.code}>{lobby.join_code}</p>
              </div>
            ) : (
              <p style={{ color: "var(--text-muted)" }}>No join code yet</p>
            )}

            <p style={styles.urlHint}>
              {window.location.origin}/join
            </p>
          </div>

          {/* Right: player list */}
          <div style={styles.playerPanel}>
            <p style={styles.playerLabel}>
              {lobby.player_count === 0
                ? "Waiting for players to arrive..."
                : `${lobby.player_count} player${lobby.player_count !== 1 ? "s" : ""} in the room`}
            </p>

            <ul style={styles.playerList}>
              {lobby.players.map((p) => (
                <li key={p.participant_id} style={styles.playerItem}>
                  <span style={styles.bullet}>&#x2022;</span>
                  {p.display_name ?? "Anonymous"}
                </li>
              ))}
            </ul>

            {lobby.status === "created" && lobby.player_count >= 4 && (
              <p style={styles.readyHint}>Ready to start — 4+ players in the room</p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div style={styles.footer}>
          <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
            Powered by Arcwright
          </span>
        </div>
      </div>
    );
  }

  const styles: Record<string, React.CSSProperties> = {
    root: {
      display: "flex",
      flexDirection: "column",
      height: "100vh",
      padding: "2rem 3rem",
      background: "var(--bg)",
    },
    centered: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      height: "100vh",
    },
    header: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      marginBottom: "2rem",
    },
    brand: {
      fontSize: "clamp(2.5rem, 5vw, 4.5rem)",
      letterSpacing: "0.3em",
      color: "var(--accent)",
      fontFamily: "'Georgia', serif",
    },
    tagline: {
      fontSize: "1rem",
      letterSpacing: "0.25em",
      color: "var(--text-muted)",
      textTransform: "uppercase",
      marginTop: "0.25rem",
    },
    main: {
      display: "flex",
      flex: 1,
      gap: "4rem",
      alignItems: "flex-start",
      justifyContent: "center",
    },
    joinPanel: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: "1rem",
      minWidth: "260px",
    },
    joinLabel: {
      fontSize: "0.85rem",
      letterSpacing: "0.2em",
      color: "var(--text-muted)",
      textTransform: "uppercase",
    },
    qr: {
      width: 220,
      height: 220,
      borderRadius: "8px",
      border: "2px solid var(--border)",
    },
    codeBlock: {
      textAlign: "center",
    },
    codeLabel: {
      fontSize: "0.75rem",
      color: "var(--text-muted)",
      letterSpacing: "0.1em",
      marginBottom: "0.25rem",
    },
    code: {
      fontSize: "var(--code-size)",
      letterSpacing: "0.2em",
      color: "var(--accent)",
      fontFamily: "'Georgia', serif",
      fontWeight: "bold",
    },
    urlHint: {
      fontSize: "0.85rem",
      color: "var(--text-muted)",
      letterSpacing: "0.05em",
    },
    playerPanel: {
      flex: 1,
      maxWidth: "420px",
      paddingTop: "0.5rem",
    },
    playerLabel: {
      fontSize: "1rem",
      color: "var(--text-muted)",
      letterSpacing: "0.1em",
      marginBottom: "1.5rem",
      textTransform: "uppercase",
    },
    playerList: {
      listStyle: "none",
      display: "flex",
      flexDirection: "column",
      gap: "0.75rem",
    },
    playerItem: {
      display: "flex",
      alignItems: "center",
      gap: "0.75rem",
      fontSize: "1.5rem",
      color: "var(--text)",
      borderBottom: "1px solid var(--border)",
      paddingBottom: "0.5rem",
    },
    bullet: {
      color: "var(--accent)",
      fontSize: "1.2rem",
    },
    readyHint: {
      marginTop: "2rem",
      color: "var(--accent)",
      fontSize: "0.9rem",
      letterSpacing: "0.1em",
    },
    footer: {
      display: "flex",
      justifyContent: "center",
      paddingTop: "1rem",
    },
  };
  ```

- [ ] **Step 2: Verify in browser**

  With `npm run dev` running in the dashboard terminal and uvicorn running:

  1. Create a session via curl (from Task 2 Step 5 above). Note the `session_id` and `join_code`.
  2. Open `http://localhost:5173/display/<session-id>` in Chrome.
  3. Confirm: NIGHTCAP title appears, join code shows in large gold text, QR code image loads.
  4. In another PowerShell, run the lobby-join curl from Task 2 Step 5 with the correct `join_code`.
  5. Within 2-3 seconds, the player name should appear on the display screen.

- [ ] **Step 3: Commit**

  ```powershell
  git add dashboard/src/screens/DisplayScreen.tsx
  git commit -m "feat(dashboard): display screen — join code, QR, live player list"
  ```

---

### Task 5: Join and waiting screens

**Goal:** Build the player phone experience — a name input form at `/join?code=<code>` that posts to the API, then a "You're in! Waiting for everyone else to join" confirmation screen at `/waiting`.

**Files:**
- Create: `dashboard/src/screens/JoinScreen.tsx`
- Create: `dashboard/src/screens/WaitingScreen.tsx`

**Acceptance Criteria:**
- [ ] On a phone browser, `http://<tunnel>/join?code=ABC123` shows a name input form with the code pre-filled (read-only)
- [ ] Submitting a name calls `POST /v1/lobby-join` and redirects to `/waiting?name=<name>&session_id=<id>`
- [ ] An invalid code shows an inline error message without crashing
- [ ] The waiting screen shows the player's name and "Waiting for everyone else to join."
- [ ] Both screens are legible on a 390px wide mobile viewport

**Verify:** On phone browser via cloudflared tunnel: scan QR → name form appears → submit name → see confirmation screen.

**Steps:**

- [ ] **Step 1: Create `dashboard/src/screens/JoinScreen.tsx`**

  ```typescript
  import { FormEvent, useState } from "react";
  import { joinLobby } from "../api/lobby";

  export default function JoinScreen() {
    const params = new URLSearchParams(window.location.search);
    const codeFromUrl = params.get("code") ?? "";

    const [name, setName] = useState("");
    const [code, setCode] = useState(codeFromUrl.toUpperCase());
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e: FormEvent) {
      e.preventDefault();
      if (!name.trim()) {
        setError("Enter your name to join.");
        return;
      }
      if (!code.trim()) {
        setError("Enter the code shown on the screen.");
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const result = await joinLobby(name.trim(), code.trim());
        const next = `/waiting?name=${encodeURIComponent(result.display_name)}&session_id=${result.session_id}`;
        window.location.href = next;
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong. Try again.");
        setLoading(false);
      }
    }

    return (
      <div style={styles.root}>
        <div style={styles.card}>
          <h1 style={styles.title}>NIGHTCAP</h1>
          <p style={styles.subtitle}>A Murder Mystery</p>

          <form onSubmit={handleSubmit} style={styles.form}>
            <label style={styles.label} htmlFor="name">
              Your name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Jordan"
              maxLength={64}
              disabled={loading}
              style={styles.input}
              autoFocus
              autoComplete="given-name"
            />

            <label style={styles.label} htmlFor="code">
              Join code (from the screen)
            </label>
            <input
              id="code"
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              placeholder="e.g. ABC123"
              maxLength={8}
              disabled={loading}
              style={{ ...styles.input, letterSpacing: "0.3em", textAlign: "center" }}
            />

            {error && (
              <p style={styles.error}>{error}</p>
            )}

            <button type="submit" disabled={loading} style={styles.button}>
              {loading ? "Joining..." : "Join the game"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  const styles: Record<string, React.CSSProperties> = {
    root: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      minHeight: "100vh",
      padding: "1.5rem",
      background: "var(--bg)",
    },
    card: {
      width: "100%",
      maxWidth: "420px",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: "0.5rem",
    },
    title: {
      fontSize: "2.5rem",
      letterSpacing: "0.3em",
      color: "var(--accent)",
      marginBottom: "0",
    },
    subtitle: {
      fontSize: "0.85rem",
      letterSpacing: "0.2em",
      color: "var(--text-muted)",
      textTransform: "uppercase",
      marginBottom: "2rem",
    },
    form: {
      width: "100%",
      display: "flex",
      flexDirection: "column",
      gap: "0.75rem",
    },
    label: {
      fontSize: "0.8rem",
      letterSpacing: "0.1em",
      color: "var(--text-muted)",
      textTransform: "uppercase",
    },
    input: {
      width: "100%",
      padding: "0.9rem 1rem",
      background: "var(--surface)",
      border: "1px solid var(--border)",
      borderRadius: "6px",
      color: "var(--text)",
      fontSize: "1.1rem",
      outline: "none",
    },
    error: {
      color: "var(--red)",
      fontSize: "0.9rem",
      textAlign: "center",
    },
    button: {
      marginTop: "0.5rem",
      padding: "1rem",
      background: "var(--accent)",
      color: "#0a0a0f",
      border: "none",
      borderRadius: "6px",
      fontSize: "1rem",
      fontWeight: "bold",
      letterSpacing: "0.05em",
    },
  };
  ```

- [ ] **Step 2: Create `dashboard/src/screens/WaitingScreen.tsx`**

  ```typescript
  export default function WaitingScreen() {
    const params = new URLSearchParams(window.location.search);
    const name = params.get("name") ?? "You";

    return (
      <div style={styles.root}>
        <div style={styles.card}>
          <h1 style={styles.title}>NIGHTCAP</h1>
          <p style={styles.subtitle}>A Murder Mystery</p>

          <div style={styles.messageBlock}>
            <p style={styles.greeting}>You're in, {name}.</p>
            <p style={styles.waiting}>Waiting for everyone else to join.</p>
          </div>

          <p style={styles.hint}>Keep this screen open. The game will begin soon.</p>
        </div>
      </div>
    );
  }

  const styles: Record<string, React.CSSProperties> = {
    root: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      minHeight: "100vh",
      padding: "1.5rem",
      background: "var(--bg)",
    },
    card: {
      width: "100%",
      maxWidth: "420px",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: "0.5rem",
      textAlign: "center",
    },
    title: {
      fontSize: "2.5rem",
      letterSpacing: "0.3em",
      color: "var(--accent)",
    },
    subtitle: {
      fontSize: "0.85rem",
      letterSpacing: "0.2em",
      color: "var(--text-muted)",
      textTransform: "uppercase",
      marginBottom: "2.5rem",
    },
    messageBlock: {
      display: "flex",
      flexDirection: "column",
      gap: "1rem",
      marginBottom: "2rem",
    },
    greeting: {
      fontSize: "1.8rem",
      color: "var(--text)",
      lineHeight: 1.3,
    },
    waiting: {
      fontSize: "1.1rem",
      color: "var(--text-muted)",
      fontStyle: "italic",
    },
    hint: {
      fontSize: "0.8rem",
      color: "var(--text-muted)",
      letterSpacing: "0.05em",
    },
  };
  ```

- [ ] **Step 3: Run typecheck**

  ```powershell
  cd dashboard
  npm run typecheck
  ```

  Expected: `Found 0 errors.`

  If you see errors about missing types on the `styles` object (TypeScript can't infer `React.CSSProperties` from a plain object), add this import to the files that need it:
  ```typescript
  import type { CSSProperties } from "react";
  ```
  And change `Record<string, React.CSSProperties>` to `Record<string, CSSProperties>`.

- [ ] **Step 4: End-to-end walkthrough**

  With uvicorn + dashboard running:

  1. Create a session: `curl.exe -s -X POST http://localhost:8000/v1/sessions -H "Content-Type: application/json" -H "X-Api-Key: <your-api-key>" -d '{"arc_id": "nightcap"}'`
  2. Note `session_id` and `join_code` from the response (also visible at `GET /v1/sessions/<id>/lobby`).
  3. Open display: `http://localhost:5173/display/<session-id>`
  4. Open join (simulating phone): `http://localhost:5173/join?code=<join-code>`
  5. Enter a name and submit.
  6. Confirm: waiting screen shows correct name.
  7. Confirm: display screen shows the player's name within 2-3 seconds.

- [ ] **Step 5: Commit**

  ```powershell
  git add dashboard/src/screens/JoinScreen.tsx dashboard/src/screens/WaitingScreen.tsx
  git commit -m "feat(dashboard): join and waiting screens for player phone"
  ```

---

## Self-Review

**Spec coverage check:**

| Requirement | Task |
|---|---|
| Shared display: QR code | Task 4 (DisplayScreen - QR via qrserver API) |
| Shared display: join code in large text | Task 4 (DisplayScreen - `code` style at `--code-size`) |
| Shared display: player names appear as people join | Task 4 (DisplayScreen - polling every 2s) |
| Shared display: music | NOT IMPLEMENTED (see below) |
| Shared display: themed artwork | Partial — dark atmospheric theme in CSS, no art assets |
| Player phone: matching theme | Task 5 (same CSS variables) |
| Player phone: "You're in! Waiting for everyone else" | Task 5 (WaitingScreen) |
| Engine health route | Already done (api/main.py, pre-existing) |

**Music gap:** The spec mentions music playing on the display while waiting. This requires either a local audio file committed to the repo (not appropriate for a music track) or an external URL. For Rehearsal 1, the founder can play music separately (Spotify, phone, laptop speaker). The display screen has no `<audio>` element intentionally — adding one with a hardcoded external URL would be fragile and could break. A follow-up task can add a configurable audio URL to the session config. This gap is called out, not silently omitted.

**Placeholder scan:** No TBDs, TODOs, or "similar to above" references. Every step has exact code.

**Type consistency check:** `LobbyPlayer`, `LobbyState`, `LobbyJoinResult` are defined in `api/lobby.ts` and used consistently across `DisplayScreen.tsx`, `JoinScreen.tsx`, and `App.tsx`. The `fetchLobbyState` function returns `LobbyState` and `joinLobby` returns `LobbyJoinResult` — these match the usage in the screen components.

**Join code casing:** `_generate_join_code()` produces uppercase. `lobby_join` endpoint calls `body.join_code.upper()` before lookup. `JoinScreen` calls `.toUpperCase()` on user input before sending. `joinLobby()` in the API client also calls `.toUpperCase()`. Four consistent checkpoints — case mismatch cannot cause a false 404.

**FK constraint for Character:** `lobby_join` service method creates a `Character` row before creating the `SessionParticipant`, satisfying the FK constraint that `add_player` skips (using a raw `uuid4()` that would violate FK in Postgres). This is correct and intentional.
