"""Pydantic models for arc-definition validation and loading."""

from __future__ import annotations

from enum import Enum
from math import isclose
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from engine.events.models import AudienceTarget, PresentationHints
from engine.interactions.models import InteractionDefinition
from engine.mini_games.models import MiniGameBinding
from engine.resources.models import EffectDefinition
from engine.session.models import QualityTier


class CharacterMode(str, Enum):
    authored = "authored"
    generated = "generated"
    hybrid = "hybrid"


class AestheticMode(str, Enum):
    fixed = "fixed"
    palette = "palette"
    generative = "generative"


class PlayMode(str, Enum):
    imposter = "imposter"
    detective_race = "detective_race"
    cooperative = "cooperative"


class SelectionModelOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    allow_random: bool = False


class AestheticConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    selection_model: Dict[str, SelectionModelOption] = Field(default_factory=dict)
    asset_generation: Dict[str, str] = Field(default_factory=dict)
    ab_test_planned: Optional[str] = None


class PacingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stall_threshold: float = 0.25
    misdirection_threshold: float = 0.80
    premium_threshold: float = 0.85
    # Whether a pacing-injected misdirection creates a mandatory obligation
    # that gates the arc's reveal-readiness condition (spec 0065). Arc-
    # configurable per AW-271; defaults to non-blocking.
    misdirection_obligation_mandatory: bool = False
    w_time: float
    w_action: float
    w_suspicion: float
    w_coverage: float

    @model_validator(mode="after")
    def validate_weight_sum(self) -> "PacingConfig":
        total = self.w_time + self.w_action + self.w_suspicion + self.w_coverage
        if not isclose(total, 1.0, abs_tol=0.000001):
            msg = "pacing weights must sum to 1.0"
            raise ValueError(msg)
        return self


class BeatPacingConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    stall_threshold_seconds: Optional[int] = None
    acceleration_trigger: Optional[str] = None
    misdirection_trigger: Optional[str] = None


class GenerativeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    killer_assignment: bool = False
    character_generation: bool = False
    character_personality_augmentation: bool = False
    aesthetic_generation: bool = False
    clue_content: bool = False
    plot_twist: bool = False
    narrator_dialogue: bool = False


class ContentRailsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prohibited_categories: List[str] = Field(default_factory=list)
    thematic_warnings: List[str] = Field(default_factory=list)
    age_floor: int = 18
    extra_prohibitions: List[str] = Field(default_factory=list)
    """Arc-authored plain-language sentences appended to the L3 policy block.

    Lets an arc tighten its content rules beyond the category list without
    engine code changes. Arc config can only add prohibitions; the platform
    minimum policy and the L1/L2 layers are engine-owned and cannot be
    relaxed from here.
    """
    fictional_frame_terms: List[str] = Field(default_factory=list)
    """Game vocabulary L1 may treat as fictional-frame markers (issue #219).

    Lets an arc register its own title and world words (e.g. a game name)
    so in-fiction player input is not mistaken for real-world harm
    facilitation. L1 admits only guarded single alphabetic tokens and never
    words its harm detectors key on, so this cannot weaken the detectors —
    see engine/safety/l1.py.
    """


class KnowledgeRuleSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    killer_knows_they_did_it: bool = False
    narrator_omniscient: bool = False
    clues_private_until_shared: bool = False


class NarratorConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    _ALLOWED_BEHAVIOR_TRIGGERS = frozenset(
        {
            "beat_transition",
            "clue_release",
            "tension_threshold",
            "player_inaction",
        }
    )

    type: str
    surface: str
    persona_mode: str
    behavior_triggers: List[str] = Field(default_factory=list)
    omniscient: bool
    player_addressable: bool

    @model_validator(mode="after")
    def validate_behavior_triggers(self) -> "NarratorConfig":
        invalid = sorted(
            trigger
            for trigger in self.behavior_triggers
            if trigger not in self._ALLOWED_BEHAVIOR_TRIGGERS
        )
        if invalid:
            msg = f"invalid narrator behavior triggers: {', '.join(invalid)}"
            raise ValueError(msg)
        return self


class PhaseKind(str, Enum):
    """The fixed set of steps a beat may be divided into (spec 0093, Part C).

    The order here is the only order a beat may list them in.
    """

    scene = "scene"
    choices = "choices"
    mini_game = "mini_game"
    bridge = "bridge"
    commit = "commit"
    reveal = "reveal"
    result = "result"
    recap = "recap"


PHASE_ORDER: tuple[PhaseKind, ...] = tuple(PhaseKind)
_LINE_PHASES = frozenset({PhaseKind.scene, PhaseKind.bridge})
_LINE_AUDIENCES = frozenset(
    {AudienceTarget.all, AudienceTarget.shared_display, AudienceTarget.host_only}
)


class PhaseLine(BaseModel):
    """One written line shown when a scene or bridge phase begins."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    speaker: Optional[str] = None
    hints: PresentationHints = Field(default_factory=PresentationHints)


RecapMeasure = Literal[
    "investigations_used",
    "investigations_left",
    "subjects_looked_into",
    "most_returns_to_one_subject",
    "reviews",
    "times_last_to_ready",
    "mini_games_won",
    "draft_changes",
    "locked_in_time",
    "slots_right",
]
"""What the engine counts for each player from saved records (spec 0094,
Part J). A condition can name only one of these, so no line can be chosen by
anything the engine did not see happen. ``locked_in_time`` is 1 or 0."""

RecapCompare = Literal["highest", "lowest", "equals", "at_least", "at_most"]


class RecapCondition(BaseModel):
    """When a recap line applies. ``highest`` and ``lowest`` hold for the
    players at the top or bottom of the room, and only when the room is not
    level. ``equals``, ``at_least`` and ``at_most`` need a ``value``."""

    model_config = ConfigDict(extra="forbid")

    measure: RecapMeasure
    compare: RecapCompare
    value: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_value(self) -> "RecapCondition":
        needs_value = self.compare in ("equals", "at_least", "at_most")
        if needs_value != (self.value is not None):
            msg = f"compare {self.compare!r} " + (
                "needs a value" if needs_value else "takes no value"
            )
            raise ValueError(msg)
        return self


class RecapLine(BaseModel):
    """One written line and the condition that earns it."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    when: RecapCondition
    hints: PresentationHints = Field(default_factory=PresentationHints)


class RecapFallback(BaseModel):
    """A line for a player no other line fits. It has no condition."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    hints: PresentationHints = Field(default_factory=PresentationHints)


class RecapConfig(BaseModel):
    """The written lines of a ``recap`` phase, in priority order, and the
    fallbacks for a player no line fits (spec 0094, Part J)."""

    model_config = ConfigDict(extra="forbid")

    lines: List[RecapLine] = Field(default_factory=list)
    fallbacks: List[RecapFallback] = Field(min_length=1)


class PhaseDefinition(BaseModel):
    """One step of a beat. ``seconds`` is the authored time limit and is
    required, so no room can wait forever on a phase."""

    model_config = ConfigDict(extra="forbid")

    kind: PhaseKind
    seconds: int = Field(gt=0)
    audience: AudienceTarget = AudienceTarget.shared_display
    lines: List[PhaseLine] = Field(default_factory=list)
    source: Literal["arc", "case_closing"] = "arc"
    """``case_closing`` on a ``scene`` phase takes its lines from the case's
    written ``closing``, so the arc file never holds them."""
    recap: Optional[RecapConfig] = None
    """Required on a ``recap`` phase and allowed nowhere else."""

    @model_validator(mode="after")
    def validate_lines_and_audience(self) -> "PhaseDefinition":
        if self.lines and self.kind not in _LINE_PHASES:
            msg = f"a {self.kind.value} phase cannot carry written lines"
            raise ValueError(msg)
        if self.audience not in _LINE_AUDIENCES:
            msg = "phase lines cannot be addressed to one player"
            raise ValueError(msg)
        if self.source == "case_closing" and (
            self.kind is not PhaseKind.scene or self.lines
        ):
            msg = "source case_closing is for a scene phase with no lines of its own"
            raise ValueError(msg)
        if (self.kind is PhaseKind.recap) != (self.recap is not None):
            msg = "a recap phase needs recap lines, and no other phase may have them"
            raise ValueError(msg)
        return self


class ChoiceConfig(BaseModel):
    """Per-game settings for the choices phase. Values are configuration,
    never constants in code."""

    model_config = ConfigDict(extra="forbid")

    budget: int = Field(default=6, ge=0)
    """Paid choices each participant may make over the whole game."""


class BeatDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    beat_id: str
    beat_name: str
    beat_type: str
    story_circle_step: Union[int, List[int]]
    structural_function: str
    dramatic_purpose: Optional[str] = None
    emotional_target: Optional[str] = None
    information_goal: Optional[str] = None
    tension_target: Optional[float] = None
    character_emphasis: List[str] = Field(default_factory=list)
    authored_content: Optional[Dict[str, Any]] = None
    generative_triggers: List[str] = Field(default_factory=list)
    entry_conditions: List[str] = Field(default_factory=list)
    exit_conditions: List[str] = Field(default_factory=list)
    pacing_config: BeatPacingConfig = Field(default_factory=BeatPacingConfig)
    audience_targets: List[str] = Field(default_factory=list)
    mini_games: Optional[List[MiniGameBinding]] = None
    interaction_ids: List[str] = Field(default_factory=list)
    phases: Optional[List[PhaseDefinition]] = None
    """Ordered steps of this beat. None keeps the old behaviour (spec 0093)."""
    mini_game_pick: Literal["listed", "fitting"] = "listed"
    """How each ``mini_game`` phase of this beat picks its game (AW-344, D-145).
    ``listed``: the Nth phase runs the Nth entry of ``mini_games``. ``fitting``:
    ``mini_games`` is a pool, and each phase runs the first entry, in this order,
    that allows the session's player count and whose mechanic has not been
    started in the session; none left skips the phase."""

    @model_validator(mode="after")
    def validate_phase_order(self) -> "BeatDefinition":
        if self.phases is None:
            return self
        if not self.phases:
            msg = f"beat {self.beat_id} lists phases but none"
            raise ValueError(msg)
        kinds = [phase.kind for phase in self.phases]
        positions = [PHASE_ORDER.index(kind) for kind in kinds]
        distinct = sorted(set(positions))
        if positions != sorted(positions) or any(
            positions.count(position) > 1
            and PHASE_ORDER[position] is not PhaseKind.mini_game
            for position in distinct
        ):
            msg = (
                f"beat {self.beat_id} phases must follow the order "
                f"{', '.join(kind.value for kind in PHASE_ORDER)}, each at most once "
                "(mini_game may repeat, one after another)"
            )
            raise ValueError(msg)
        return self

    @property
    def mini_game_slots(self) -> int:
        """How many mini-games this beat may run: its ``mini_game`` phases."""
        return sum(1 for p in self.phases or [] if p.kind is PhaseKind.mini_game)

    @model_validator(mode="after")
    def validate_binding_has_a_mini_game_phase(self) -> "BeatDefinition":
        """A binding on a phased beat that has no ``mini_game`` phase would
        never run, with no error anywhere. Beats without phases are unchanged."""
        if self.phases is None or not self.mini_games:
            return self
        if not any(phase.kind is PhaseKind.mini_game for phase in self.phases):
            msg = f"beat {self.beat_id} binds a mini-game but has no mini_game phase"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_slots_match_the_listed_mini_games(self) -> "BeatDefinition":
        """With ``listed`` picking, slot N runs the Nth binding. A binding past the
        last slot can never run, so a reward or a switched off release on it would
        be ignored with no error anywhere; a slot with no binding left to run is a
        mistake in the arc file. ``fitting`` picks from the whole list, so it has
        neither problem."""
        if self.mini_game_pick != "listed" or not self.mini_games:
            return self
        slots = self.mini_game_slots
        if slots > len(self.mini_games):
            msg = (
                f"beat {self.beat_id} has {slots} mini_game phases but lists "
                f"{len(self.mini_games)} mini-games; each phase needs one"
            )
            raise ValueError(msg)
        runnable = max(slots, 1)
        for binding in self.mini_games[runnable:]:
            if binding.reward is not None or not binding.release_content:
                shown = (
                    "the first mini-game"
                    if runnable == 1
                    else f"the first {runnable} mini-games"
                )
                msg = (
                    f"beat {self.beat_id} sets a reward or release_content on "
                    f"{binding.binding_id}, but it can never run: only {shown} "
                    f"on a beat {'runs' if runnable == 1 else 'run'}"
                )
                raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_mini_game_binding_ids(self) -> "BeatDefinition":
        if not self.mini_games:
            return self
        binding_ids = [binding.binding_id for binding in self.mini_games]
        if len(binding_ids) != len(set(binding_ids)):
            msg = f"beat {self.beat_id} has duplicate mini-game binding_ids"
            raise ValueError(msg)
        return self


class EmotionalTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    beat_id: str
    target_tension: float = Field(ge=0.0, le=1.0)
    note: Optional[str] = None


class AuthorialIntent(BaseModel):
    """Structured soft authorial logic: theme, tone, and target tension curve.

    Spec 0064 / ADR-0012. This is an authoring input the engine executes
    against — generation context and telemetry comparison only. It never
    drives or overrides deterministic state transitions.
    """

    model_config = ConfigDict(extra="forbid")

    theme: str
    tone: str
    emotional_targets: List[EmotionalTarget] = Field(default_factory=list)

    def target_tension_for(self, beat_id: str) -> Optional[float]:
        for target in self.emotional_targets:
            if target.beat_id == beat_id:
                return target.target_tension
        return None


class ObligationConfig(BaseModel):
    """Authored narrative obligation registered at session start.

    Spec 0065 / ADR-0012. Obligations are durable session state tracked by
    deterministic engine paths only; AI output never creates or resolves
    one. ``resolve_on_beat_entry`` is the deterministic resolution trigger:
    the obligation resolves when the session enters that beat. When None,
    the obligation resolves only through an explicit engine call and is
    otherwise expired at session end.
    """

    model_config = ConfigDict(extra="forbid")

    obligation_key: str
    description: str
    mandatory: bool = False
    resolve_on_beat_entry: Optional[str] = None


class ArcDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    arc_id: str
    name: str
    min_players: int
    max_players: int
    character_mode: CharacterMode
    aesthetic_config: AestheticConfig
    aesthetic_mode: Optional[AestheticMode] = None
    setting_constraint: Optional[str] = None
    arc_structure: str
    play_mode: PlayMode
    narrator: NarratorConfig
    quality_tier_default: QualityTier
    characters: List[Dict[str, Any]] = Field(default_factory=list)
    beats: List[BeatDefinition] = Field(min_length=1)
    interactions: List[InteractionDefinition] = Field(default_factory=list)
    resource_effects: List[EffectDefinition] = Field(default_factory=list)
    beat_graph: Dict[str, List[str]]
    generative_elements: GenerativeConfig
    content_rails: ContentRailsConfig
    knowledge_rules: KnowledgeRuleSet
    pacing_config: PacingConfig
    victim_config: Dict[str, Any] = Field(default_factory=dict)
    kill_config: Dict[str, Any] = Field(default_factory=dict)
    murder_timing_range: List[int] = Field(default_factory=list)
    session_duration_range: List[int] = Field(default_factory=list)
    revelation_step_range: List[int] = Field(default_factory=list)
    tone_config: Dict[str, Any] = Field(default_factory=dict)
    authorial_intent: Optional[AuthorialIntent] = None
    obligations: List[ObligationConfig] = Field(default_factory=list)
    case_file: Optional[str] = None
    """Path, from the repository root, to a written case (spec 0093, Part A)."""
    mini_game_root: Optional[str] = None
    """Folder, from the repository root, holding the mini-game packages this
    arc's beats are bound to (spec 0093, Part E). One folder per game, named by
    its game ID."""
    choice_config: ChoiceConfig = Field(default_factory=ChoiceConfig)

    @property
    def is_phased(self) -> bool:
        """True when beats are divided into phases that move by rule."""
        return any(beat.phases is not None for beat in self.beats)

    @model_validator(mode="after")
    def validate_commit_phase_has_a_case(self) -> "ArcDefinition":
        """A ``commit`` phase asks each player for a theory of the case's
        solution slots, and the closing phases judge those theories, so the
        arc must name a written case. Each closing phase needs the one before
        it earlier in the arc, or the game would start and then never get past
        it: a ``reveal`` or ``result`` needs a ``commit``, a ``recap`` needs a
        ``result``."""
        phases = [phase for beat in self.beats for phase in beat.phases or []]
        kinds = {phase.kind for phase in phases}
        closing = {
            PhaseKind.commit,
            PhaseKind.reveal,
            PhaseKind.result,
            PhaseKind.recap,
        }
        needs_case = bool(kinds & closing) or any(
            phase.source == "case_closing" for phase in phases
        )
        if needs_case and not self.case_file:
            msg = "an arc with a commit or closing phase must name a case_file"
            raise ValueError(msg)
        needs = {
            PhaseKind.reveal: PhaseKind.commit,
            PhaseKind.result: PhaseKind.commit,
            PhaseKind.recap: PhaseKind.result,
        }
        seen: set[PhaseKind] = set()
        for phase in phases:
            before = needs.get(phase.kind)
            if before is not None and before not in seen:
                msg = (
                    f"a {phase.kind.value} phase needs a {before.value} phase before it"
                )
                raise ValueError(msg)
            seen.add(phase.kind)
        return self

    @model_validator(mode="after")
    def validate_phases_on_every_beat_or_none(self) -> "ArcDefinition":
        flags = {beat.phases is not None for beat in self.beats}
        if len(flags) > 1:
            missing = [b.beat_id for b in self.beats if b.phases is None]
            msg = (
                "phases must be listed on every beat or on none; missing on: "
                f"{', '.join(missing)}"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="before")
    @classmethod
    def migrate_legacy_aesthetic_mode(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if "aesthetic_config" not in data and "aesthetic_mode" in data:
            data = dict(data)
            data["aesthetic_config"] = {
                "selection_model": {},
                "asset_generation": {
                    "legacy_mode": data["aesthetic_mode"],
                },
            }
        return data

    @model_validator(mode="after")
    def validate_player_counts(self) -> "ArcDefinition":
        if self.min_players < 1:
            msg = "min_players must be at least 1"
            raise ValueError(msg)
        if self.max_players < 1:
            msg = "max_players must be at least 1"
            raise ValueError(msg)
        if self.min_players > self.max_players:
            msg = "min_players cannot exceed max_players"
            raise ValueError(msg)
        if self.play_mode == PlayMode.imposter and self.min_players < 3:
            msg = "imposter play mode requires at least 3 players"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_authored_characters(self) -> "ArcDefinition":
        if self.character_mode == CharacterMode.authored and not self.characters:
            msg = "authored character mode requires at least one character"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_authorial_intent_targets(self) -> "ArcDefinition":
        if self.authorial_intent is None:
            return self
        beat_ids = {beat.beat_id for beat in self.beats}
        unknown = sorted(
            {
                target.beat_id
                for target in self.authorial_intent.emotional_targets
                if target.beat_id not in beat_ids
            }
        )
        if unknown:
            msg = (
                "authorial_intent.emotional_targets reference unknown beat ids: "
                f"{', '.join(unknown)}"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_obligations(self) -> "ArcDefinition":
        if not self.obligations:
            return self
        keys = [obligation.obligation_key for obligation in self.obligations]
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        if duplicates:
            msg = f"obligations contain duplicate keys: {', '.join(duplicates)}"
            raise ValueError(msg)
        beat_ids = {beat.beat_id for beat in self.beats}
        unknown = sorted(
            {
                obligation.resolve_on_beat_entry
                for obligation in self.obligations
                if obligation.resolve_on_beat_entry is not None
                and obligation.resolve_on_beat_entry not in beat_ids
            }
        )
        if unknown:
            msg = (
                "obligations reference unknown resolve_on_beat_entry beat ids: "
                f"{', '.join(unknown)}"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_beat_graph(self) -> "ArcDefinition":
        beat_ids = {beat.beat_id for beat in self.beats}
        graph_ids = set(self.beat_graph)
        unknown_sources = sorted(graph_ids - beat_ids)
        if unknown_sources:
            msg = f"beat_graph contains unknown beat ids: {', '.join(unknown_sources)}"
            raise ValueError(msg)

        unknown_targets = sorted(
            {
                target
                for targets in self.beat_graph.values()
                for target in targets
                if target not in beat_ids
            }
        )
        if unknown_targets:
            msg = (
                "beat_graph references undefined beat ids: "
                f"{', '.join(unknown_targets)}"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_interactions(self) -> "ArcDefinition":
        interaction_ids = [
            interaction.interaction_id for interaction in self.interactions
        ]
        if len(interaction_ids) != len(set(interaction_ids)):
            msg = "duplicate interaction ids are not allowed"
            raise ValueError(msg)
        known_ids = set(interaction_ids)
        unknown = sorted(
            {
                interaction_id
                for beat in self.beats
                for interaction_id in beat.interaction_ids
                if interaction_id not in known_ids
            }
        )
        if unknown:
            msg = f"beats reference unknown interaction ids: {', '.join(unknown)}"
            raise ValueError(msg)
        return self
