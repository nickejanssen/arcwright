"""
Arc State Machine Implementation

Core state machine for arc execution. Uses python-statemachine StateChart
to represent arc beat graphs: states are beats, transitions are arc progressions,
guards are authored entry and exit conditions.

Reference: Technical Architecture v1.3, Section 3 (Arc Execution Engine)
"""

from enum import Enum
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from statemachine import StateChart, State
import logging

logger = logging.getLogger(__name__)


@dataclass
class BeatConfig:
    """Configuration for a beat within an arc."""
    beat_id: str
    name: str
    beat_type: str = "standard"  # standard, compound, parallel
    description: str = ""
    entry_conditions: Dict[str, Any] = field(default_factory=dict)
    exit_conditions: Dict[str, Any] = field(default_factory=dict)
    generative_elements: Dict[str, Any] = field(default_factory=dict)
    dramatic_tension_target: Optional[float] = None
    
    
@dataclass
class ArcDefinition:
    """Arc definition schema for state machine initialization."""
    arc_id: str
    name: str
    beats: Dict[str, BeatConfig]
    beat_graph: Dict[str, list[str]]  # beat_id -> valid next beat_ids
    initial_beat: str
    final_beats: list[str]
    pacing_config: Dict[str, Any] = field(default_factory=dict)
    generative_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ArcStateMachine:
    """
    Base arc state machine wrapper for StateChart (SCXML-compliant).
    
    Represents the arc's beat graph:
    - States are beats
    - Transitions are arc progressions
    - Guards enforce authored constraints
    
    This wraps StateChart and provides a generic interface that can work
    with any arc definition. Specific arcs can inherit from this or use it directly.
    
    Reference: Technical Architecture v1.3, Section 3.1 (StateChart Architecture)
    """
    
    def __init__(self, arc_definition: ArcDefinition):
        """
        Initialize the arc state machine.
        
        Args:
            arc_definition: ArcDefinition specifying beats, transitions, and constraints
        """
        self.arc_definition = arc_definition
        self.session_state: Dict[str, Any] = {}
        self.beat_history: list[tuple[str, datetime]] = []
        self.entry_callbacks: Dict[str, Callable] = {}
        self.exit_callbacks: Dict[str, Callable] = {}
        
        logger.info(f"ArcStateMachine initialized for arc: {arc_definition.arc_id}")
    
    def on_enter_state(self, beat_id: str, context: Optional[Dict[str, Any]] = None):
        """
        Called when entering a beat state.
        
        Args:
            beat_id: The beat state being entered
            context: Optional context data for the transition
        """
        self.beat_history.append((beat_id, datetime.utcnow()))
        if beat_id in self.entry_callbacks:
            self.entry_callbacks[beat_id](context or {})
        logger.info(f"Entered beat: {beat_id}")
    
    def on_exit_state(self, beat_id: str, context: Optional[Dict[str, Any]] = None):
        """
        Called when exiting a beat state.
        
        Args:
            beat_id: The beat state being exited
            context: Optional context data for the transition
        """
        if beat_id in self.exit_callbacks:
            self.exit_callbacks[beat_id](context or {})
        logger.info(f"Exited beat: {beat_id}")
    
    def register_entry_callback(self, beat_id: str, callback: Callable):
        """Register a callback to be called when entering a beat."""
        self.entry_callbacks[beat_id] = callback
    
    def register_exit_callback(self, beat_id: str, callback: Callable):
        """Register a callback to be called when exiting a beat."""
        self.exit_callbacks[beat_id] = callback
    
    def get_current_beat(self) -> Optional[str]:
        """Get the current beat ID from the session state."""
        return self.get_session_state('current_beat')
    
    def get_beat_history(self) -> list[tuple[str, datetime]]:
        """Get the history of beat transitions."""
        return self.beat_history.copy()
    
    def is_in_beat(self, beat_id: str) -> bool:
        """Check if the state machine is currently in a specific beat."""
        current = self.get_current_beat()
        return current == beat_id if current else False
    
    def can_transition_to(self, target_beat: str) -> bool:
        """
        Check if a transition to target_beat is valid according to arc definition.
        
        This is used to validate transitions before executing them.
        """
        current = self.get_current_beat()
        if not current:
            return target_beat == self.arc_definition.initial_beat
        
        valid_next = self.arc_definition.beat_graph.get(current, [])
        return target_beat in valid_next
    
    def update_session_state(self, key: str, value: Any):
        """Update session state that persists across transitions."""
        self.session_state[key] = value
        logger.debug(f"Session state updated: {key} = {value}")
    
    def get_session_state(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from persistent session state."""
        return self.session_state.get(key, default)


class NightcapPlaceholderChart(StateChart):
    """
    Placeholder Nightcap arc state flow for testing ArcStateMachine.
    
    Implements the basic Nightcap beat structure:
    - introduction (compound): onboarding → killer_assignment → motive_reveal
    - investigation (compound, parallel): clue_phase → resolution
    - reveal (final)
    
    Reference: Technical Architecture v1.3, Section 3.7 (Nightcap Arc Execution Flow)
    """
    
    # Introduction phase (compound state with internal beats)
    class introduction(State.Compound, initial=True):
        """Setup phase: onboarding, killer assignment, motive establishment."""
        
        onboarding = State('Onboarding', initial=True)
        killer_assignment = State('Killer Assignment')
        motive_reveal = State('Motive Reveal', final=True)
        
        # Transitions within introduction
        begin_game = onboarding.to(killer_assignment)
        motives_established = killer_assignment.to(motive_reveal)
    
    # Investigation phase (compound with parallel regions)
    class investigation(State.Compound):
        """Main investigation phase with parallel clue distribution and interrogation."""
        
        class clue_phase(State.Parallel):
            """Parallel regions: private clue distribution + group interrogation."""
            
            class private_clues(State.Compound):
                """Private clue distribution to individual players."""
                distributing = State('Distributing', initial=True)
                distributed = State('Distributed', final=True)
                clues_sent = distributing.to(distributed)
            
            class interrogation(State.Compound):
                """Group interrogation of suspects."""
                open = State('Open', initial=True)
                closed = State('Closed', final=True)
                interrogation_complete = open.to(closed)
        
        resolution = State('Resolution', final=True)
        
        # Transition: both parallel regions complete → investigation complete
        phases_complete = clue_phase.to(resolution)
    
    # Reveal phase (final)
    reveal = State('Reveal', final=True)
    
    # Arc-level transitions
    investigation_begins = introduction.to(investigation)
    accusation_filed = investigation.to(reveal)
    
    def __init__(self):
        """Initialize the placeholder Nightcap chart."""
        super().__init__()
        self.session_context: Dict[str, Any] = {}
        logger.info("NightcapPlaceholderChart initialized")
    
    def update_context(self, key: str, value: Any):
        """Update session context."""
        self.session_context[key] = value
        logger.debug(f"Nightcap context updated: {key} = {value}")
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Retrieve value from session context."""
        return self.session_context.get(key, default)
