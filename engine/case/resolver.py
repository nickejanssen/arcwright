"""Deterministic case resolver.

Given (arc_definition, seed, participant_count) → a fully-resolved case
where the culprit, victim, cast, evidence chain, and authorized lies
have all been chosen from the arc's authored skeletons + generative
taxonomy tables.

Determinism model
-----------------
Every random choice in this module goes through a single
``random.Random(seed)`` instance so the same seed always produces the
same case for the same arc.

Fairness
--------
The resolver asserts ``solvability_check`` and
``lie_falsifiability_check`` before returning; both must pass. Failure
raises ``CaseInvariantError`` with the failing invariant name and
enough seed/skeleton context to reproduce.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from engine.arc.models import ArcDefinition
from engine.case.errors import CaseInvariantError, CaseResolutionError
from engine.case.invariants import (
    lie_falsifiability_check,
    solvability_check,
)
from engine.case.loader import (
    CaseResolutionConfig,
    Taxonomy,
    load_case_resolution_config,
    load_skeletons,
    load_taxonomy,
)
from engine.case.models import (
    AuthorizedFalsehood,
    CaseSkeleton,
    CastMember,
    EvidenceEntry,
    ResolvedCase,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

_SUSPECT_ROLES = ("intimate", "deflector", "observer", "obvious_suspect")
_SUSPECT_NAME_POOL = (
    "Ashford",
    "Bellamy",
    "Corvax",
    "Delacourt",
    "Estève",
    "Fairholme",
    "Grantham",
    "Halloway",
    "Ito",
    "Jansen",
    "Kent",
    "Lorimer",
)


def resolve(
    arc_definition: ArcDefinition,
    seed: int,
    participant_count: int,
    *,
    config_path: Path | None = None,
) -> ResolvedCase:
    if participant_count < 2 or participant_count > 8:
        raise CaseResolutionError(
            f"participant_count must be 2..8, got {participant_count}"
        )

    cfg = load_case_resolution_config(
        config_path or _default_config_path(arc_definition)
    )
    skeletons = load_skeletons(REPO_ROOT / cfg.skeleton_directory)
    taxonomy = load_taxonomy(REPO_ROOT / cfg.taxonomy_directory)

    rng = random.Random(seed)

    skeleton = _pick_skeleton(rng, skeletons)
    cast_size = _resolve_cast_size(cfg, skeleton, participant_count)
    cast = _resolve_cast(rng, cast_size)
    culprit = cast[0]
    victim = _resolve_victim(rng)

    evidence = _resolve_evidence(rng, skeleton, cast, taxonomy, culprit)
    lies = _resolve_lies(rng, skeleton, cast, culprit, evidence, taxonomy)

    case = ResolvedCase(
        case_id=_build_case_id(arc_definition.arc_id, seed),
        arc_id=arc_definition.arc_id,
        seed=seed,
        skeleton_id=skeleton.skeleton_id,
        cast=[*cast, victim],
        culprit_id=culprit.member_id,
        evidence=evidence,
        falsehoods=lies,
        reveal_shape=skeleton.reveal_shape,
    )

    ok, detail = solvability_check(case)
    if not ok:
        raise CaseInvariantError(
            f"solvability failed for seed={seed} skeleton={skeleton.skeleton_id}: {detail}"
        )
    ok, detail = lie_falsifiability_check(case)
    if not ok:
        raise CaseInvariantError(
            f"lie_falsifiability failed for seed={seed} skeleton={skeleton.skeleton_id}: {detail}"
        )
    return case


def _default_config_path(arc: ArcDefinition) -> Path:
    return REPO_ROOT / "nightcap" / "case_resolution_config.json"


def _pick_skeleton(
    rng: random.Random, skeletons: dict[str, CaseSkeleton]
) -> CaseSkeleton:
    return skeletons[rng.choice(sorted(skeletons.keys()))]


def _resolve_cast_size(
    cfg: CaseResolutionConfig,
    skeleton: CaseSkeleton,
    participant_count: int,
) -> int:
    if skeleton.cast_size_override is not None:
        return skeleton.cast_size_override
    key = str(participant_count)
    if key not in cfg.cast_size_by_player_count:
        raise CaseResolutionError(
            f"no cast size configured for participant_count={participant_count}"
        )
    return cfg.cast_size_by_player_count[key]


def _resolve_cast(rng: random.Random, cast_size: int) -> list[CastMember]:
    names = list(_SUSPECT_NAME_POOL)
    rng.shuffle(names)
    picked = names[:cast_size]
    culprit_index = rng.randrange(cast_size)
    cast: list[CastMember] = []
    for i, name in enumerate(picked):
        role_tag = _SUSPECT_ROLES[i % len(_SUSPECT_ROLES)]
        cast.append(
            CastMember(
                member_id=f"s{i + 1}",
                display_name=name,
                role="suspect",
                is_culprit=(i == culprit_index),
                tags=[role_tag],
            )
        )
    # Rotate so the culprit is index 0 for easier resolver code.
    if culprit_index != 0:
        cast[0], cast[culprit_index] = cast[culprit_index], cast[0]
    return cast


def _resolve_victim(rng: random.Random) -> CastMember:
    return CastMember(
        member_id="v1",
        display_name=rng.choice(("Marcus", "Vivien", "Alexei", "Iris", "Rosalind")),
        role="victim",
    )


def _resolve_evidence(
    rng: random.Random,
    skeleton: CaseSkeleton,
    cast: list[CastMember],
    taxonomy: Taxonomy,
    culprit: CastMember,
) -> list[EvidenceEntry]:
    stages = skeleton.clue_chain_pattern["stages"]
    evidence: list[EvidenceEntry] = []
    other_suspects = [
        m.member_id
        for m in cast
        if m.member_id != culprit.member_id and m.role == "suspect"
    ]
    for i, stage in enumerate(stages):
        # Every stage-derived clue points toward the culprit; the last
        # stage narrows to the culprit exclusively (see solvability_check).
        points_toward = [culprit.member_id]
        points_away_from: list[str] = []
        if i == 0 and len(other_suspects) >= 1:
            # First-stage: broad; some other suspects also implicated (uncertainty).
            points_toward = [
                culprit.member_id,
                *rng.sample(other_suspects, min(2, len(other_suspects))),
            ]
        text = _fabricate_evidence_text(rng, stage, taxonomy)
        evidence.append(
            EvidenceEntry(
                evidence_id=f"e{i + 1}",
                evidence_type=stage.get("kind", "trace"),
                text=text,
                points_toward=points_toward,
                points_away_from=points_away_from,
                delivery="group" if i % 2 == 0 else "private",
                delivery_target=None,
                truth_value="genuine",
            )
        )
    return evidence


def _fabricate_evidence_text(
    rng: random.Random,
    stage: dict[str, Any],
    taxonomy: Taxonomy,
) -> str:
    # Placeholder generative text — will be replaced by the wrapper voice
    # library integration in AW-268. For now, use the stage prompt +
    # a small taxonomic flourish so unit tests can distinguish seeds.
    prompt = stage.get("prompt", "evidence detail")
    flourish = ""
    if taxonomy.method_families:
        family = rng.choice(taxonomy.method_families)
        traces = family.get("traces", [])
        if traces:
            flourish = f" ({rng.choice(traces)})"
    return f"{prompt}{flourish}"


def _resolve_lies(
    rng: random.Random,
    skeleton: CaseSkeleton,
    cast: list[CastMember],
    culprit: CastMember,
    evidence: list[EvidenceEntry],
    taxonomy: Taxonomy,
) -> list[AuthorizedFalsehood]:
    lies: list[AuthorizedFalsehood] = []
    non_culprit_suspects = [
        m for m in cast if m.role == "suspect" and m.member_id != culprit.member_id
    ]
    for i, member in enumerate(non_culprit_suspects):
        role_tag = member.tags[0] if member.tags else "deflector"
        topics = skeleton.lie_shapes_by_role.get(role_tag, ["location"])
        topic = rng.choice(topics)
        # Every lie is contradicted by the first genuine evidence entry
        # for now — the invariant only requires non-empty contradicted_by
        # and the solver (Task 7) will apply per-topic reasoning.
        contradicted_by = [evidence[0].evidence_id] if evidence else []
        lies.append(
            AuthorizedFalsehood(
                falsehood_id=f"l{i + 1}",
                speaker_id=member.member_id,
                topic=topic,
                claim_text=_fabricate_lie_text(rng, topic, taxonomy),
                contradicted_by=contradicted_by,
            )
        )
    # The culprit also lies — about location, contradicted by the last stage clue.
    culprit_lie = AuthorizedFalsehood(
        falsehood_id=f"l{len(non_culprit_suspects) + 1}",
        speaker_id=culprit.member_id,
        topic="location",
        claim_text=_fabricate_lie_text(rng, "location", taxonomy),
        contradicted_by=[evidence[-1].evidence_id] if evidence else [],
    )
    lies.append(culprit_lie)
    return lies


def _fabricate_lie_text(
    rng: random.Random,
    topic: str,
    taxonomy: Taxonomy,
) -> str:
    return {
        "location": "I was somewhere else at the time in question.",
        "relationship": "I barely knew them.",
        "observation": "I didn't see anything unusual.",
        "possession": "I had nothing to do with that item.",
    }.get(topic, "You are mistaken about that.")


def _build_case_id(arc_id: str, seed: int) -> str:
    return f"{arc_id}::case::{seed}"
