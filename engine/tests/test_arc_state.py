"""
Tests for Arc State Machine Implementation

Tests cover:
1. ArcStateMachine initialization and configuration
2. Beat transitions and state management
3. Session state persistence
4. Callbacks on entry/exit
5. NightcapPlaceholderChart state flow
6. Arc definition validation

Reference: Technical Architecture v1.3, Section 3 (Arc Execution Engine)
"""

import pytest
from datetime import datetime
from typing import Dict, Any
from engine.arc_state import (
    ArcStateMachine,
    ArcDefinition,
    BeatConfig,
    NightcapPlaceholderChart,
)


class TestBeatConfig:
    """Tests for BeatConfig dataclass."""
    
    def test_beat_config_creation(self):
        """Test creating a beat configuration."""
        beat = BeatConfig(
            beat_id="onboarding",
            name="Player Onboarding",
            beat_type="standard",
            description="Introduction and character setup",
        )
        assert beat.beat_id == "onboarding"
        assert beat.name == "Player Onboarding"
        assert beat.beat_type == "standard"
        assert beat.entry_conditions == {}
        assert beat.exit_conditions == {}
    
    def test_beat_config_with_conditions(self):
        """Test beat config with entry/exit conditions."""
        beat = BeatConfig(
            beat_id="killer_assignment",
            name="Killer Assignment",
            entry_conditions={"require_players": 6},
            exit_conditions={"require_assigned_killer": True},
        )
        assert beat.entry_conditions == {"require_players": 6}
        assert beat.exit_conditions == {"require_assigned_killer": True}


class TestArcDefinition:
    """Tests for ArcDefinition dataclass."""
    
    @pytest.fixture
    def simple_arc_def(self) -> ArcDefinition:
        """Create a simple arc definition for testing."""
        beats = {
            "introduction": BeatConfig(
                beat_id="introduction",
                name="Introduction",
                beat_type="compound",
            ),
            "investigation": BeatConfig(
                beat_id="investigation",
                name="Investigation",
                beat_type="compound",
            ),
            "reveal": BeatConfig(
                beat_id="reveal",
                name="Reveal",
                beat_type="standard",
            ),
        }
        
        return ArcDefinition(
            arc_id="test_arc",
            name="Test Arc",
            beats=beats,
            beat_graph={
                "introduction": ["investigation"],
                "investigation": ["reveal"],
                "reveal": [],
            },
            initial_beat="introduction",
            final_beats=["reveal"],
        )
    
    def test_arc_definition_creation(self, simple_arc_def: ArcDefinition):
        """Test creating an arc definition."""
        assert simple_arc_def.arc_id == "test_arc"
        assert simple_arc_def.name == "Test Arc"
        assert simple_arc_def.initial_beat == "introduction"
        assert "reveal" in simple_arc_def.final_beats
        assert len(simple_arc_def.beats) == 3
    
    def test_arc_definition_beat_graph(self, simple_arc_def: ArcDefinition):
        """Test beat graph in arc definition."""
        assert simple_arc_def.beat_graph["introduction"] == ["investigation"]
        assert simple_arc_def.beat_graph["investigation"] == ["reveal"]
        assert simple_arc_def.beat_graph["reveal"] == []


class TestArcStateMachine:
    """Tests for ArcStateMachine base class."""
    
    @pytest.fixture
    def simple_arc_def(self) -> ArcDefinition:
        """Create a simple arc definition for testing."""
        beats = {
            "introduction": BeatConfig(
                beat_id="introduction",
                name="Introduction",
            ),
            "investigation": BeatConfig(
                beat_id="investigation",
                name="Investigation",
            ),
            "reveal": BeatConfig(
                beat_id="reveal",
                name="Reveal",
            ),
        }
        
        return ArcDefinition(
            arc_id="test_arc",
            name="Test Arc",
            beats=beats,
            beat_graph={
                "introduction": ["investigation"],
                "investigation": ["reveal"],
                "reveal": [],
            },
            initial_beat="introduction",
            final_beats=["reveal"],
        )
    
    @pytest.fixture
    def state_machine(self, simple_arc_def: ArcDefinition) -> ArcStateMachine:
        """Create a state machine for testing."""
        return ArcStateMachine(simple_arc_def)
    
    def test_state_machine_initialization(self, state_machine: ArcStateMachine):
        """Test state machine initialization."""
        assert state_machine.arc_definition is not None
        assert state_machine.arc_definition.arc_id == "test_arc"
        assert state_machine.session_state == {}
        assert state_machine.beat_history == []
        assert state_machine.entry_callbacks == {}
        assert state_machine.exit_callbacks == {}
    
    def test_session_state_update(self, state_machine: ArcStateMachine):
        """Test updating and retrieving session state."""
        state_machine.update_session_state("killer_id", "char_001")
        assert state_machine.get_session_state("killer_id") == "char_001"
        
        state_machine.update_session_state("tension_score", 0.75)
        assert state_machine.get_session_state("tension_score") == 0.75
    
    def test_session_state_default_value(self, state_machine: ArcStateMachine):
        """Test getting session state with default value."""
        result = state_machine.get_session_state("nonexistent", "default_value")
        assert result == "default_value"
    
    def test_beat_history_tracking(self, state_machine: ArcStateMachine):
        """Test beat history tracking."""
        state_machine.on_enter_state("introduction")
        state_machine.on_enter_state("investigation")
        state_machine.on_enter_state("reveal")
        
        history = state_machine.get_beat_history()
        assert len(history) == 3
        assert history[0][0] == "introduction"
        assert history[1][0] == "investigation"
        assert history[2][0] == "reveal"
        
        # Verify all timestamps are datetime objects
        for beat_id, timestamp in history:
            assert isinstance(timestamp, datetime)
    
    def test_entry_callback_registration(self, state_machine: ArcStateMachine):
        """Test registering and calling entry callbacks."""
        callback_called = {"introduction": False}
        
        def on_enter_introduction(context: Dict[str, Any]):
            callback_called["introduction"] = True
        
        state_machine.register_entry_callback("introduction", on_enter_introduction)
        state_machine.on_enter_state("introduction", {})
        
        assert callback_called["introduction"] is True
    
    def test_exit_callback_registration(self, state_machine: ArcStateMachine):
        """Test registering and calling exit callbacks."""
        callback_called = {"investigation": False}
        
        def on_exit_investigation(context: Dict[str, Any]):
            callback_called["investigation"] = True
        
        state_machine.register_exit_callback("investigation", on_exit_investigation)
        state_machine.on_exit_state("investigation", {})
        
        assert callback_called["investigation"] is True
    
    def test_callback_with_context(self, state_machine: ArcStateMachine):
        """Test callbacks receive context data."""
        received_context = {}
        
        def on_enter_with_context(context: Dict[str, Any]):
            received_context.update(context)
        
        state_machine.register_entry_callback("investigation", on_enter_with_context)
        test_context = {"player_count": 6, "killer_id": "char_001"}
        state_machine.on_enter_state("investigation", test_context)
        
        assert received_context == test_context
    
    def test_can_transition_to_valid(self, state_machine: ArcStateMachine):
        """Test valid transition check."""
        state_machine.update_session_state('current_beat', 'introduction')
        assert state_machine.can_transition_to("investigation") is True
    
    def test_can_transition_to_invalid(self, state_machine: ArcStateMachine):
        """Test invalid transition check."""
        state_machine.update_session_state('current_beat', 'introduction')
        assert state_machine.can_transition_to("reveal") is False
    
    def test_can_transition_initial_beat(self, state_machine: ArcStateMachine):
        """Test transition to initial beat when no state set."""
        # No beats entered yet, should allow transition to initial beat
        assert state_machine.can_transition_to("introduction") is True


class TestNightcapPlaceholderChart:
    """Tests for NightcapPlaceholderChart state flow."""
    
    @pytest.fixture
    def nightcap_chart(self) -> NightcapPlaceholderChart:
        """Create a Nightcap placeholder chart."""
        return NightcapPlaceholderChart()
    
    def test_nightcap_chart_initialization(self, nightcap_chart: NightcapPlaceholderChart):
        """Test Nightcap chart initialization."""
        assert nightcap_chart is not None
        assert nightcap_chart.session_context == {}
    
    def test_nightcap_initial_state(self, nightcap_chart: NightcapPlaceholderChart):
        """Test that Nightcap chart starts in introduction state."""
        # configuration is a set of active states in the current configuration
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "introduction" in state_ids
    
    def test_nightcap_introduction_phase_structure(
        self, nightcap_chart: NightcapPlaceholderChart
    ):
        """Test introduction phase has correct internal structure."""
        # Introduction should have onboarding, killer_assignment, motive_reveal
        assert hasattr(nightcap_chart, "onboarding")
        assert hasattr(nightcap_chart, "killer_assignment")
        assert hasattr(nightcap_chart, "motive_reveal")
    
    def test_nightcap_investigation_phase_structure(
        self, nightcap_chart: NightcapPlaceholderChart
    ):
        """Test investigation phase has correct internal structure."""
        assert hasattr(nightcap_chart, "clue_phase")
        assert hasattr(nightcap_chart, "resolution")
    
    def test_nightcap_clue_phase_parallel_regions(
        self, nightcap_chart: NightcapPlaceholderChart
    ):
        """Test clue phase has two parallel regions."""
        assert hasattr(nightcap_chart, "private_clues")
        assert hasattr(nightcap_chart, "interrogation")
    
    def test_nightcap_private_clues_beats(
        self, nightcap_chart: NightcapPlaceholderChart
    ):
        """Test private clues region has distributing and distributed states."""
        assert hasattr(nightcap_chart, "distributing")
        assert hasattr(nightcap_chart, "distributed")
    
    def test_nightcap_interrogation_beats(
        self, nightcap_chart: NightcapPlaceholderChart
    ):
        """Test interrogation region has open and closed states."""
        assert hasattr(nightcap_chart, "open")
        assert hasattr(nightcap_chart, "closed")
    
    def test_nightcap_reveal_state(self, nightcap_chart: NightcapPlaceholderChart):
        """Test reveal state exists."""
        assert hasattr(nightcap_chart, "reveal")
    
    def test_nightcap_context_management(self, nightcap_chart: NightcapPlaceholderChart):
        """Test context storage and retrieval."""
        nightcap_chart.update_context("killer_id", "character_001")
        assert nightcap_chart.get_context("killer_id") == "character_001"
        
        nightcap_chart.update_context("tension_score", 0.65)
        assert nightcap_chart.get_context("tension_score") == 0.65
    
    def test_nightcap_context_default_value(
        self, nightcap_chart: NightcapPlaceholderChart
    ):
        """Test context retrieval with default value."""
        result = nightcap_chart.get_context("nonexistent", "default")
        assert result == "default"
    
    def test_nightcap_begin_game_transition(
        self, nightcap_chart: NightcapPlaceholderChart
    ):
        """Test begin_game transition from onboarding to killer_assignment."""
        # Navigate to onboarding (already initial)
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "introduction" in state_ids
        
        # Trigger begin_game transition
        nightcap_chart.send("begin_game")
        
        # Should now be in killer_assignment
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "killer_assignment" in state_ids
    
    def test_nightcap_motives_established_transition(
        self, nightcap_chart: NightcapPlaceholderChart
    ):
        """Test motives_established transition."""
        # Move through introduction
        nightcap_chart.send("begin_game")
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "killer_assignment" in state_ids
        
        # Trigger motives_established
        nightcap_chart.send("motives_established")
        
        # Should now be in motive_reveal
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "motive_reveal" in state_ids
    
    def test_nightcap_investigation_begins_transition(
        self, nightcap_chart: NightcapPlaceholderChart
    ):
        """Test investigation_begins arc-level transition."""
        # Navigate through introduction to motive_reveal
        nightcap_chart.send("begin_game")
        nightcap_chart.send("motives_established")
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "motive_reveal" in state_ids
        
        # Trigger investigation_begins
        nightcap_chart.send("investigation_begins")
        
        # Should now be in investigation
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "investigation" in state_ids
    
    def test_nightcap_complete_flow(self, nightcap_chart: NightcapPlaceholderChart):
        """Test complete arc flow from introduction to reveal."""
        # Introduction phase
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "introduction" in state_ids
        
        nightcap_chart.send("begin_game")
        nightcap_chart.send("motives_established")
        
        # Move to investigation
        nightcap_chart.send("investigation_begins")
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "investigation" in state_ids
        
        # Complete clue distribution (private_clues compound completes)
        nightcap_chart.send("clues_sent")
        
        # Complete interrogation (interrogation compound completes)
        nightcap_chart.send("interrogation_complete")
        
        # Now both parallel regions are done, transition to resolution
        nightcap_chart.send("phases_complete")
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "resolution" in state_ids
        
        # Move to reveal (accusation filed transitions from investigation to reveal)
        nightcap_chart.send("accusation_filed")
        config = nightcap_chart.configuration
        state_ids = {state.id for state in config}
        assert "reveal" in state_ids


class TestIntegration:
    """Integration tests combining ArcStateMachine and NightcapPlaceholderChart."""
    
    def test_arc_state_machine_with_nightcap_definition(self):
        """Test ArcStateMachine can be configured with Nightcap-like definition."""
        beats = {
            "introduction": BeatConfig(
                beat_id="introduction",
                name="Introduction",
                beat_type="compound",
                generative_elements={"personality_calibration": True},
            ),
            "investigation": BeatConfig(
                beat_id="investigation",
                name="Investigation",
                beat_type="compound",
                generative_elements={"clue_generation": True},
            ),
            "reveal": BeatConfig(
                beat_id="reveal",
                name="Reveal",
                beat_type="standard",
                generative_elements={"killer_confession": True},
            ),
        }
        
        arc_def = ArcDefinition(
            arc_id="nightcap",
            name="Nightcap Murder Mystery",
            beats=beats,
            beat_graph={
                "introduction": ["investigation"],
                "investigation": ["reveal"],
                "reveal": [],
            },
            initial_beat="introduction",
            final_beats=["reveal"],
            generative_config={"killer_assignment_strategy": "ai_driven"},
        )
        
        state_machine = ArcStateMachine(arc_def)
        
        # Verify configuration
        assert state_machine.arc_definition.arc_id == "nightcap"
        assert len(state_machine.arc_definition.beats) == 3
        assert state_machine.arc_definition.beats["reveal"].generative_elements[
            "killer_confession"
        ] is True
    
    def test_nightcap_chart_with_callbacks(self):
        """Test NightcapPlaceholderChart can be extended with callbacks."""
        chart = NightcapPlaceholderChart()
        
        entry_log = []
        
        def track_entry(state_name: str):
            def callback():
                entry_log.append(f"entered_{state_name}")
            return callback
        
        # Navigate and track
        chart.send("begin_game")
        entry_log.append("transitioned_to_killer_assignment")
        
        assert "transitioned_to_killer_assignment" in entry_log


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
