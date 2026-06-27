# Rehearsal 1 - Failure Cheat Sheet

When something breaks mid-session, find the closest match below and run
the named recovery. Log a blocker afterward using
[blocker-log-template.md](blocker-log-template.md).

## Player disconnect

The player's tile turns gray on the shared display.

- If the disconnected player is mid-mini-game: their slot times out and
  the game falls back to the authored clue path. The session continues
  without them.
- If they reconnect: the SDK auto-resumes them at the current beat. They
  rejoin in time for the next moment.
- If they cannot reconnect: continue. The accusation phase still works
  with the players who are present (provided the floor of 4 is preserved
  - if you drop below 4, narrate the missing player as "stepped away" and
  proceed solo-mini-game beats only).

Severity if recurring: **P1**.

## Mini-game timeout (no completion within duration)

The shared display shows a time-up state followed by the fallback clue.

- Confirm the fallback clue text appears for every player who needs it.
- If the fallback does NOT appear: the host narrates the reduced clue
  verbally and the session continues. Log **P0** (the delayed-clue
  fallback contract is broken).

## Shared display freeze

The shared display stops updating but player devices keep working.

- Refresh the shared display browser. Session state is server-side and the
  page rejoins at the current beat.
- If refresh does not recover: continue using player devices only. Host
  narrates from a player device temporarily. Log **P0** if the freeze
  persists across reloads.

## Narrator silent (shared-display narrator area is empty)

The shared display shows the layout but the narrator text area is empty.

- Wait 10 seconds. Some narrator generations take that long under load.
- If still empty: host reads a generic version of the current beat ("The
  room is quiet. Someone has to speak first.") and continues. Log **P1**.

## Tunnel dropped

Players can no longer reach the join URL.

- Restart cloudflared in the terminal:
  `cloudflared tunnel --url http://localhost:5173`.
- Note the new `*.trycloudflare.com` URL.
- Send the new URL to players in your group chat.
- Players reload. Session state is preserved server-side. Log **P1**
  (operational pain, not a correctness failure).

## Engine crash

The Docker engine container exits.

- Check: `docker compose ps`.
- Restart: `docker compose up -d`.
- Apply any pending migrations: `alembic upgrade head`.
- The session likely needs to be restarted from the most recent snapshot.
  Players rejoin via the same join URL. **P0** blocker.

## Privacy leak (private content appears on shared display)

The shared display shows text that should have been private to one player
(role, private clue, killer identity before reveal).

- **STOP the session immediately.** Tell players "we hit a bug, give me
  a moment."
- Tear down: `docker compose down`. Stop cloudflared.
- Log **P0**. Do not resume. Re-runs need an engineering fix first.

This failure mode is non-negotiable - the AW-230 privacy contract was
designed to make this impossible. If it happens, it is the highest-
priority M5 blocker.
