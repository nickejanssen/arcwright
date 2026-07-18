"""Deterministic case resolver.

Given (arc_definition, seed, participant_ids), produce a fully-resolved
case where the culprit, victim, cast, case-truth fact graph, evidence
chain, and authorized lies have all been chosen from the arc's authored
skeletons plus generative taxonomy tables.

Determinism model
------------------
Every random choice in this module goes through a single
``random.Random(seed)`` instance so the same seed always produces the
same case for the same arc and the same participant list.

Arc independence
-----------------
This module never hardcodes a path into any single arc's content. The
case-resolution config (skeleton directory, taxonomy directory, cast
size table) is located through ``resolve_case_resolution_config_path``,
an arc-agnostic prefix-match registry (mirrors ``engine/arc/registry.py``),
and the loaded config's own ``arc_id_prefix`` is validated against the
arc actually being resolved, even when a caller supplies an explicit
``config_path`` override. No claim text, role value, or content string
is embedded in this module: everything player-facing is drawn from the
arc's taxonomy tables (see ``engine/case/README.md``).

Fairness
--------
The resolver asserts ``solvability_check`` and ``lie_falsifiability_check``
before returning; both must pass. Failure raises ``CaseInvariantError``
with the failing invariant name and enough seed and skeleton context to
reproduce. These are the resolver's own internal-consistency checks.
The independent, non-circular proof that a human player can actually
solve the case from delivered information lives in
``engine/case/solver.py``, which does not read this module's
``points_toward``/``points_away_from`` bookkeeping fields at all.
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
    resolve_case_resolution_config_path,
)
from engine.case.models import (
    AuthorizedFalsehood,
    CaseFact,
    CaseSkeleton,
    CastMember,
    EvidenceEntry,
    ResolvedCase,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASE_RESOLUTION_REGISTRY_PATH = (
    REPO_ROOT / "config" / "case_resolution_registry.json"
)


def resolve(
    arc_definition: ArcDefinition,
    seed: int,
    participant_ids: list[str],
    *,
    config_path: Path | None = None,
    forced_skeleton_id: str | None = None,
) -> ResolvedCase:
    """Resolve a case. ``forced_skeleton_id`` is a test-only override:
    when set, skip the seeded skeleton pick and use this skeleton_id
    exactly. Lets test suites exercise an exact, documented number of
    seeds per skeleton instead of relying on the seeded pick's
    distribution to land close to a target count by chance."""
    participant_count = len(participant_ids)
    if participant_count < 2 or participant_count > 8:
        raise CaseResolutionError(
            f"participant_ids must contain 2..8 entries, got {participant_count}"
        )
    if len(set(participant_ids)) != participant_count:
        raise CaseResolutionError("participant_ids must not contain duplicates")

    cfg = load_case_resolution_config(
        config_path or _default_config_path(arc_definition)
    )
    if not arc_definition.arc_id.startswith(cfg.arc_id_prefix):
        raise CaseResolutionError(
            f"case-resolution config arc_id_prefix={cfg.arc_id_prefix!r} "
            f"does not match arc_id={arc_definition.arc_id!r}; refusing to "
            "resolve another arc's content against this arc"
        )
    skeletons = load_skeletons(REPO_ROOT / cfg.skeleton_directory)
    taxonomy = load_taxonomy(REPO_ROOT / cfg.taxonomy_directory)

    rng = random.Random(seed)

    if forced_skeleton_id is not None:
        if forced_skeleton_id not in skeletons:
            raise CaseResolutionError(
                f"forced_skeleton_id={forced_skeleton_id!r} not found; "
                f"known skeleton ids: {sorted(skeletons.keys())}"
            )
        skeleton = skeletons[forced_skeleton_id]
    else:
        skeleton = _pick_skeleton(rng, skeletons)
    cast_size = _resolve_cast_size(cfg, skeleton, participant_count)
    cast = _resolve_cast(rng, cast_size, taxonomy)
    culprit = cast[0]
    victim = _resolve_victim(rng, taxonomy)
    full_cast = [*cast, victim]

    method_family = _find_method_family(taxonomy, skeleton.method_family_id)
    descriptor, trace = _pick_method_descriptor_and_trace(rng, method_family)

    facts = _resolve_facts(rng, cast, culprit, victim, taxonomy, descriptor)
    evidence = _resolve_evidence(
        rng, skeleton, cast, culprit, participant_ids, descriptor, trace
    )
    lies, contradiction_evidence = _resolve_lies(rng, skeleton, cast, culprit, taxonomy)
    evidence = evidence + contradiction_evidence

    case = ResolvedCase(
        case_id=_build_case_id(arc_definition.arc_id, seed),
        arc_id=arc_definition.arc_id,
        seed=seed,
        skeleton_id=skeleton.skeleton_id,
        cast=full_cast,
        culprit_id=culprit.member_id,
        evidence=evidence,
        falsehoods=lies,
        facts=facts,
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
    return resolve_case_resolution_config_path(
        arc.arc_id, DEFAULT_CASE_RESOLUTION_REGISTRY_PATH
    )


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


def _resolve_cast(
    rng: random.Random, cast_size: int, taxonomy: Taxonomy
) -> list[CastMember]:
    if cast_size > len(taxonomy.suspect_names):
        raise CaseResolutionError(
            f"cast_size={cast_size} exceeds suspect name pool size "
            f"({len(taxonomy.suspect_names)})"
        )
    names = list(taxonomy.suspect_names)
    rng.shuffle(names)
    picked = names[:cast_size]
    culprit_index = rng.randrange(cast_size)
    cast: list[CastMember] = []
    for i, name in enumerate(picked):
        role_tag = taxonomy.suspect_roles[i % len(taxonomy.suspect_roles)]
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


def _resolve_victim(rng: random.Random, taxonomy: Taxonomy) -> CastMember:
    return CastMember(
        member_id="v1",
        display_name=rng.choice(taxonomy.victim_names),
        role="victim",
    )


def _find_method_family(taxonomy: Taxonomy, method_family_id: str) -> dict[str, Any]:
    for family in taxonomy.method_families:
        if family.get("family_id") == method_family_id:
            return family
    raise CaseResolutionError(
        f"method_family_id={method_family_id!r} not found in taxonomy"
    )


def _pick_method_descriptor_and_trace(
    rng: random.Random, method_family: dict[str, Any]
) -> tuple[str, str]:
    # Descriptor pool key varies by family shape: vessels, objects, or
    # locations. Try each in a fixed order so descriptor choice stays
    # deterministic for a given rng draw regardless of which key is present.
    for key in ("vessels", "objects", "locations"):
        pool = method_family.get(key)
        if pool:
            descriptor = rng.choice(pool)
            traces = method_family.get("traces", [])
            trace = rng.choice(traces) if traces else "an unexplained mark"
            return descriptor, trace
    raise CaseResolutionError(
        f"method family {method_family.get('family_id')!r} has no "
        "vessels, objects, or locations pool"
    )


def _resolve_facts(
    rng: random.Random,
    suspects: list[CastMember],
    culprit: CastMember,
    victim: CastMember,
    taxonomy: Taxonomy,
    descriptor: str,
) -> list[CaseFact]:
    facts: list[CaseFact] = []

    motive_family = rng.choice(taxonomy.motive_families)
    motive_narrative = rng.choice(
        motive_family.get("narratives", ["a private grievance"])
    )
    facts.append(
        CaseFact(
            fact_id="fact_method",
            predicate="method",
            subject_id=culprit.member_id,
            value=descriptor,
            known_by=[culprit.member_id],
        )
    )
    facts.append(
        CaseFact(
            fact_id="fact_motive",
            predicate="motive",
            subject_id=culprit.member_id,
            object_id=victim.member_id,
            value=motive_narrative,
            known_by=[culprit.member_id],
        )
    )

    secret_pool = list(taxonomy.secrets)
    relationship_pool = list(taxonomy.relationships)
    rng.shuffle(secret_pool)
    rng.shuffle(relationship_pool)
    secrets_by_member: dict[str, str] = {}
    for i, member in enumerate(suspects):
        secret_text = secret_pool[i % len(secret_pool)]
        relationship_text = relationship_pool[i % len(relationship_pool)]
        secrets_by_member[member.member_id] = secret_text
        facts.append(
            CaseFact(
                fact_id=f"fact_secret_{member.member_id}",
                predicate="secret",
                subject_id=member.member_id,
                value=secret_text,
                known_by=[member.member_id],
            )
        )
        facts.append(
            CaseFact(
                fact_id=f"fact_relationship_{member.member_id}",
                predicate="relationship",
                subject_id=member.member_id,
                object_id=victim.member_id,
                value=relationship_text,
                known_by=[member.member_id],
            )
        )

    non_culprit = [m for m in suspects if m.member_id != culprit.member_id]
    twist_subject = rng.choice(non_culprit) if non_culprit else culprit
    twist_secret = secrets_by_member[twist_subject.member_id]
    facts.append(
        CaseFact(
            fact_id="fact_twist",
            predicate="twist",
            subject_id=twist_subject.member_id,
            value=f"{twist_subject.display_name} {twist_secret}.",
            known_by=[],
        )
    )
    return facts


def _resolve_evidence(
    rng: random.Random,
    skeleton: CaseSkeleton,
    cast: list[CastMember],
    culprit: CastMember,
    participant_ids: list[str],
    descriptor: str,
    trace: str,
) -> list[EvidenceEntry]:
    stages = skeleton.clue_chain_pattern["stages"]
    evidence: list[EvidenceEntry] = []
    other_suspects = [
        m.member_id
        for m in cast
        if m.member_id != culprit.member_id and m.role == "suspect"
    ]
    for i, stage in enumerate(stages):
        prompt = stage.get("prompt", "evidence detail")
        if i == 0:
            # Broad, vague first clue: names the descriptor and trace but
            # not a suspect, matching the archetype's "not yet narrowed"
            # opening stage. Some other suspects share the implication.
            points_toward = [culprit.member_id]
            if other_suspects:
                points_toward = [
                    culprit.member_id,
                    *rng.sample(other_suspects, min(2, len(other_suspects))),
                ]
            text = f"{prompt} ({trace} on the {descriptor})."
        else:
            # Narrowing stages name the culprit specifically, so a
            # player (or the text-driven solver) reading the card can
            # actually make progress without any out-of-band label.
            points_toward = [culprit.member_id]
            text = f"{prompt} The {descriptor} traces back to {culprit.display_name}."
        points_away_from: list[str] = []
        delivery = "group" if i % 2 == 0 else "private"
        delivery_target = rng.choice(participant_ids) if delivery == "private" else None
        evidence.append(
            EvidenceEntry(
                evidence_id=f"e{i + 1}",
                evidence_type=stage.get("kind", "trace"),
                text=text,
                points_toward=points_toward,
                points_away_from=points_away_from,
                delivery=delivery,
                delivery_target=delivery_target,
                truth_value="genuine",
            )
        )
    return evidence


def _resolve_lies(
    rng: random.Random,
    skeleton: CaseSkeleton,
    cast: list[CastMember],
    culprit: CastMember,
    taxonomy: Taxonomy,
) -> tuple[list[AuthorizedFalsehood], list[EvidenceEntry]]:
    lies: list[AuthorizedFalsehood] = []
    contradiction_evidence: list[EvidenceEntry] = []
    liars = [m for m in cast if m.role == "suspect"]
    for i, member in enumerate(liars):
        if member.member_id == culprit.member_id:
            role_tag = "culprit"
            topics = ["location"]
        else:
            role_tag = member.tags[0] if member.tags else "deflector"
            topics = skeleton.lie_shapes_by_role.get(role_tag, ["location"])
        topic = rng.choice(topics)
        topic_entry = _find_lie_topic(taxonomy, topic)
        claim_text = rng.choice(
            topic_entry.get("claim_templates", ["You are mistaken about that."])
        )
        contradiction_templates = topic_entry.get(
            "contradiction_templates", ["This claim does not hold up."]
        )
        contradiction_template = rng.choice(contradiction_templates)
        contradiction_text = contradiction_template.format(speaker=member.display_name)
        contradiction_evidence_id = f"contra_{member.member_id}_{i}"

        contradiction_evidence.append(
            EvidenceEntry(
                evidence_id=contradiction_evidence_id,
                evidence_type=topic_entry.get("evidence_type", "testimony"),
                text=contradiction_text,
                points_toward=[],
                points_away_from=[],
                delivery="group",
                delivery_target=None,
                truth_value="genuine",
            )
        )
        lies.append(
            AuthorizedFalsehood(
                falsehood_id=f"l{i + 1}",
                speaker_id=member.member_id,
                topic=topic,
                claim_text=claim_text,
                contradicted_by=[contradiction_evidence_id],
            )
        )
    return lies, contradiction_evidence


def _find_lie_topic(taxonomy: Taxonomy, topic_id: str) -> dict[str, Any]:
    for entry in taxonomy.lie_topics:
        if entry.get("topic_id") == topic_id:
            return entry
    raise CaseResolutionError(f"lie topic_id={topic_id!r} not found in taxonomy")


def _build_case_id(arc_id: str, seed: int) -> str:
    return f"{arc_id}::case::{seed}"
