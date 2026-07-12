# Rehearsal Quickstart

> Current version: v1.0
> Last updated: 2026-07-11
> Status: Current
> Canonical path: docs/roadmap/operations/rehearsal-quickstart.md
> Serves: AW-273 (Rehearsal 1 execution) and later rehearsals

## One-time prerequisites

- Docker Desktop installed and running.
- Node.js LTS installed.
- `cloudflared` installed and on your PATH.
- `.env` at the repo root with real `ARCWRIGHT_API_KEY`, `ANTHROPIC_API_KEY`,
  and `GROQ_API_KEY` values. Add `FIREBASE_WEB_API_KEY` too if you want
  `make rehearsal-smoke` to cover the host start call.

## Start the stack

```powershell
make rehearsal
```

Wait for the READY block. It prints:
- `DISPLAY URL (this machine)` for the shared display.
- `PLAYER JOIN URL (phones)` for players.
- `JOIN CODE` for fallback/manual entry.

The command also bootstraps a fresh rehearsal session and saves its details in
`.rehearsal/current-session.json`.

Optional but recommended before players arrive:

```powershell
make rehearsal-smoke
```

Expected: `SMOKE PASS`. If it fails, the failing step and response are printed.

## During the session

1. Open the printed display URL on the shared display.
2. Send the printed player join URL to players' phones.
3. Wait for at least 4 players to appear in the lobby.
4. Start the arc: in a second terminal, run `make rehearsal-start`. (The
   dashboard has no host-start control; this exchanges the host token and
   calls the start endpoint. Requires `FIREBASE_WEB_API_KEY` in `.env`.)
5. Play end-to-end through join, private events, both mini-games, accusation,
   and killer reveal.
6. When something breaks or feels wrong, log the timestamp, who it affected,
   and what happened.

## Wrap-up

1. Copy `blocker-log-template.md` to `rehearsal-1-blocker-log.md` in this
   directory and fill it from your notes.
2. Paste the highlights into the AW-273 GitHub issue.
3. Stop the app stack with Ctrl+C in the rehearsal terminal.
4. Stop Postgres:

```powershell
make rehearsal-stop
```
