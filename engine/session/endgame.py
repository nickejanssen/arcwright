"""Work out who solved it and who wins (spec 0094, Parts H and I; AW-326).

``resolve_endgame`` reads the locked theories and the standing of every
finished mini-game run from saved rows, runs the pure theory check and the
pure winner rule, and returns the whole result. It saves nothing and sends
nothing: the ``result`` phase (AW-327) calls it once, saves what it returns and
tells the room. It refuses while a commit phase is still going, so no right or
wrong can be read before every theory is locked.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.case.authored import AuthoredCase, TheoryCheck, check_theories
from engine.db.orm import MiniGameRun
from engine.session import commit_phase, phases
from engine.session.commit_phase import CommitRefusal, TheoryState
from engine.session.winner import DecidedBy, Standing, decide_winners

_FINISHED = frozenset({"completed", "timed_out"})


@dataclass(frozen=True)
class PlayerResult:
    participant_id: str
    state: TheoryState
    answers: dict[str, str]
    proof: str | None
    check: TheoryCheck


@dataclass(frozen=True)
class EndgameResult:
    """``players`` is in participant-ID order, which carries no meaning."""

    players: tuple[PlayerResult, ...]
    solvers: tuple[str, ...]
    winners: tuple[str, ...]
    decided_by: DecidedBy


async def finished_standings(db: AsyncSession, session_id: UUID) -> list[Standing]:
    """The standing of every finished run that has one. A cancelled run has no
    standing and counts for nothing."""
    result = await db.execute(
        select(MiniGameRun).where(MiniGameRun.session_id == session_id)
    )
    standings: list[Standing] = []
    for run in result.scalars().all():
        standing: Any = (run.outcome or {}).get("standing")
        if run.status in _FINISHED and isinstance(standing, list):
            standings.append([[str(p) for p in tier] for tier in standing])
    return standings


async def resolve_endgame(
    db: AsyncSession, session_id: UUID, case: AuthoredCase
) -> EndgameResult:
    """The result of the newest commit phase, once it is over."""
    state = await phases.current_phase(db, session_id)
    if (
        state is not None
        and state.phase == "commit"
        and state.status in ("running", "paused")
    ):
        raise CommitRefusal("commit_not_finished", "theories are still being built")
    humans = await phases.human_player_ids(db, session_id)
    entry = await commit_phase.latest_entry(db, session_id)
    if entry is None:
        raise CommitRefusal("no_theories", "no theory phase has been played")
    theories = {
        str(p): await commit_phase.theory_of(db, session_id, p, entry) for p in humans
    }
    checks = check_theories(
        case.solution,
        {
            player: theory.answers if theory.state == "locked" else None
            for player, theory in theories.items()
        },
    )
    solvers = tuple(sorted(p for p, check in checks.items() if check.solved))
    verdict = decide_winners(solvers, await finished_standings(db, session_id))
    return EndgameResult(
        players=tuple(
            PlayerResult(
                participant_id=player,
                state="no_theory" if theory.state == "none" else theory.state,
                answers=theory.answers if theory.state == "locked" else {},
                proof=theory.proof if theory.state == "locked" else None,
                check=checks[player],
            )
            for player, theory in sorted(theories.items())
        ),
        solvers=solvers,
        winners=verdict.winners,
        decided_by=verdict.decided_by,
    )
