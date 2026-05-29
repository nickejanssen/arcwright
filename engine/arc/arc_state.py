"""
StateChart-based placeholder for the Nightcap reference arc.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from statemachine import State, StateChart

from engine.arc.models import ArcDefinition

logger = logging.getLogger(__name__)


class ArcStateChart(StateChart):
    """Single StateChart-based arc implementation for the scaffold."""

    class introduction(State.Compound, initial=True):
        onboarding = State("Onboarding", initial=True)
        killer_assignment = State("Killer Assignment")
        motive_reveal = State("Motive Reveal", final=True)

        begin_game = onboarding.to(killer_assignment)
        motives_established = killer_assignment.to(motive_reveal)

    class investigation(State.Compound):
        class clue_phase(State.Parallel):
            class private_clues(State.Compound):
                distributing = State("Distributing", initial=True)
                distributed = State("Distributed", final=True)

                clues_sent = distributing.to(distributed)

            class interrogation(State.Compound):
                open = State("Open", initial=True)
                closed = State("Closed", final=True)

                interrogation_complete = open.to(closed)

        resolution = State("Resolution", final=True)

        phases_complete = clue_phase.to(resolution)

    reveal = State("Reveal", final=True)

    investigation_begins = introduction.to(investigation)
    accusation_filed = investigation.to(reveal)

    def __init__(self, arc_definition: Optional[ArcDefinition] = None):
        super().__init__()
        self.arc_definition = arc_definition
        self.session_context: Dict[str, Any] = {}
        logger.info("ArcStateChart initialized")

    def update_context(self, key: str, value: Any) -> None:
        self.session_context[key] = value
        logger.debug("ArcStateChart context updated: %s = %s", key, value)

    def get_context(self, key: str, default: Any = None) -> Any:
        return self.session_context.get(key, default)
