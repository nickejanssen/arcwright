"""Deterministic runtime plugin for the social-truth-bluff mechanic.

Tell Me Something True is a pure social opener. This plugin owns phase state,
deadlines, spotlight order, votes, reveals, scoring, and neutral signals.
It never releases or withholds a clue during normal completion.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any
from uuid import UUID

from engine.db.orm import MiniGameSubmission
from engine.events.models import AudienceTarget, EventCategory
from engine.mini_games.resolver import ResolvedMiniGameSnapshot
from engine.mini_games.runtime import (
    MechanicEventDirective,
    MechanicProgress,
    MechanicSyntheticSubmission,
)

MECHANIC_TYPE = "social-truth-bluff"
INPUT_WINDOW_SECONDS = 45
VOTE_WINDOW_SECONDS = 15


class SocialTruthBluffPlugin:
    mechanic_type: str = MECHANIC_TYPE

    def validate_payload(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise ValueError("payload must be a JSON object")
        action = payload.get("action")
        if action == "input":
            statement_text = payload.get("statement_text")
            declared_truth = payload.get("declared_truth")
            if not isinstance(statement_text, str) or not statement_text.strip():
                raise ValueError("input submissions require a non-empty statement_text")
            if not isinstance(declared_truth, bool):
                raise ValueError("input submissions require boolean declared_truth")
            return
        if action == "vote":
            target = payload.get("target_character_id")
            vote = payload.get("vote")
            if not isinstance(target, str) or not target:
                raise ValueError("vote submissions require target_character_id")
            if vote not in {"truth", "lie"}:
                raise ValueError("vote submissions require vote=truth or vote=lie")
            return
        if action == "presence":
            connected = payload.get("connected")
            if not isinstance(connected, bool):
                raise ValueError("presence submissions require boolean connected")
            return
        raise ValueError("unsupported social-truth-bluff action")

    def is_threshold_met(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> bool:
        return False

    def score(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> dict[str, Any]:
        input_map = self._input_submissions(submissions)
        participant_ids = set(input_map)
        spotlight_order = self._spotlight_order(snapshot, submissions, input_map)
        reveals = self._reveal_records(submissions, spotlight_order)
        scores: dict[str, int] = {str(pid): 0 for pid in participant_ids}
        deflection_map: dict[str, dict[str, int]] = {
            str(pid): {} for pid in participant_ids
        }
        vote_attempts: dict[str, int] = {str(pid): 0 for pid in participant_ids}
        vote_correct: dict[str, int] = {str(pid): 0 for pid in participant_ids}

        for reveal in reveals:
            target_id = reveal["target_character_id"]
            target_key = str(target_id)
            declared_truth = reveal["declared_truth"]
            votes: dict[str, str] = reveal["votes"]
            for voter_key, vote in votes.items():
                vote_attempts[voter_key] = vote_attempts.get(voter_key, 0) + 1
                if vote == "lie":
                    per_target = deflection_map.setdefault(voter_key, {})
                    per_target[target_key] = per_target.get(target_key, 0) + 1
                is_correct = (declared_truth and vote == "truth") or (
                    (not declared_truth) and vote == "lie"
                )
                if is_correct:
                    vote_correct[voter_key] = vote_correct.get(voter_key, 0) + 1
                    scores[voter_key] = scores.get(voter_key, 0) + 1
                elif not declared_truth and vote == "truth":
                    scores[target_key] = scores.get(target_key, 0) + 1

        truth_accuracy_rate: dict[str, float] = {}
        lie_success_rate: dict[str, float] = {}
        for participant_id, submission in input_map.items():
            key = str(participant_id)
            reveal: dict[str, Any] | None = next(
                (
                    item
                    for item in reveals
                    if item["target_character_id"] == participant_id
                ),
                None,
            )
            if reveal is None:
                truth_accuracy_rate[key] = 0.0
                lie_success_rate[key] = 0.0
                continue
            non_abstaining = len(reveal["votes"])
            if submission["declared_truth"]:
                correct_truth_votes = sum(
                    1 for vote in reveal["votes"].values() if vote == "truth"
                )
                truth_accuracy_rate[key] = (
                    correct_truth_votes / non_abstaining if non_abstaining else 0.0
                )
                lie_success_rate[key] = 0.0
            else:
                fooled_votes = sum(
                    1 for vote in reveal["votes"].values() if vote == "truth"
                )
                lie_success_rate[key] = (
                    fooled_votes / non_abstaining if non_abstaining else 0.0
                )
                truth_accuracy_rate[key] = 0.0

        vote_consistency = {
            participant_key: (
                vote_correct.get(participant_key, 0) / attempts if attempts else 0.0
            )
            for participant_key, attempts in vote_attempts.items()
        }

        all_truth_round = bool(input_map) and all(
            item["declared_truth"] for item in input_map.values()
        )
        all_lie_round = bool(input_map) and all(
            not item["declared_truth"] for item in input_map.values()
        )

        outcome: dict[str, Any] = {
            "scores": scores,
            "score": scores,
            "participation-recorded": {
                str(participant_id): True for participant_id in participant_ids
            },
            "truth-accuracy-rate": truth_accuracy_rate,
            "lie-success-rate": lie_success_rate,
            "vote-consistency": vote_consistency,
            "deflection-tendency": {
                participant_key: sum(targets.values())
                for participant_key, targets in deflection_map.items()
            },
            "all-truth-round": all_truth_round,
            "round-resolved": True,
            "all-lie-round": all_lie_round,
            "runtime_signals": {
                "deflection_tendency": deflection_map,
            },
            "reveals": [
                {
                    "target_character_id": str(item["target_character_id"]),
                    "declared_truth": item["declared_truth"],
                    "statement_text": item["statement_text"],
                    "vote_breakdown": item["vote_breakdown"],
                    "abstaining_character_ids": [
                        str(char_id) for char_id in item["abstaining_character_ids"]
                    ],
                }
                for item in reveals
            ],
            "spotlight_order": [str(character_id) for character_id in spotlight_order],
        }
        return outcome

    def initialize_state(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        *,
        participants: list[tuple[UUID, UUID]],
        now: datetime,
    ) -> MechanicProgress:
        phase_event = MechanicEventDirective(
            category=EventCategory.state_transition,
            event_type="tmst_phase_started",
            target_audience=AudienceTarget.all,
            payload={
                "phase": "input",
                "deadline": (now + timedelta(seconds=INPUT_WINDOW_SECONDS)).isoformat(),
                "participant_count": len(participants),
            },
        )
        prompt_events = tuple(
            MechanicEventDirective(
                category=EventCategory.input_request,
                event_type="tmst_private_prompt_ready",
                target_audience=AudienceTarget.specific_player,
                target_player_id=participant_id,
                payload={"phase": "input"},
            )
            for _character_id, participant_id in participants
        )
        return MechanicProgress(
            state={
                "phase": "input",
                "presence": {str(char_id): True for char_id, _ in participants},
                "input_closed": False,
                "current_spotlight_index": 0,
                "spotlight_order": [],
            },
            deadline=now + timedelta(seconds=INPUT_WINDOW_SECONDS),
            events=(phase_event, *prompt_events),
        )

    def on_submission(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        *,
        state: dict[str, Any],
        participants: list[tuple[UUID, UUID]],
        submission: MiniGameSubmission,
        accepted_submissions: list[MiniGameSubmission],
        now: datetime,
    ) -> MechanicProgress:
        action = submission.payload.get("action")
        next_state = dict(state)
        presence = dict(next_state.get("presence", {}))
        if action == "presence":
            presence[str(submission.character_id)] = bool(
                submission.payload.get("connected")
            )
            next_state["presence"] = presence
            if next_state.get("phase") == "spotlight" and not submission.payload.get(
                "connected"
            ):
                return self._advance_skips(
                    snapshot, next_state, participants, accepted_submissions, now
                )
            return MechanicProgress(state=next_state)

        if action == "input":
            if next_state.get("phase") != "input":
                raise ValueError(
                    "input submissions are only accepted during input phase"
                )
            if self._has_prior_action(
                accepted_submissions[:-1], submission.character_id, "input"
            ):
                raise ValueError("input already submitted for this participant")
            all_inputs = self._input_submissions(accepted_submissions)
            if len(all_inputs) == len(participants):
                return self._start_spotlight_phase(
                    snapshot,
                    next_state,
                    participants,
                    accepted_submissions,
                    now,
                )
            return MechanicProgress(state=next_state)

        if action == "vote":
            if next_state.get("phase") != "spotlight":
                raise ValueError(
                    "vote submissions are only accepted during spotlight phase"
                )
            current_target = self._current_target(next_state, participants)
            submitted_target = UUID(str(submission.payload["target_character_id"]))
            if current_target is None or submitted_target != current_target:
                raise ValueError("vote target does not match the current spotlight")
            if submission.character_id == current_target:
                raise ValueError(
                    "spotlighted player may not vote on their own statement"
                )
            if not presence.get(str(submission.character_id), True):
                raise ValueError("disconnected players cannot vote")
            if self._has_prior_vote(
                accepted_submissions[:-1],
                submission.character_id,
                submitted_target,
            ):
                raise ValueError("vote already submitted for this spotlight")
            eligible_voters = self._eligible_voters(
                current_target,
                participants,
                presence,
            )
            current_votes = self._votes_for_target(accepted_submissions, current_target)
            if len(current_votes) >= len(eligible_voters):
                return self._resolve_current_spotlight(
                    snapshot,
                    next_state,
                    participants,
                    accepted_submissions,
                    now,
                )
            return MechanicProgress(state=next_state)

        raise ValueError("unsupported social-truth-bluff action")

    def on_deadline_expired(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        *,
        state: dict[str, Any],
        participants: list[tuple[UUID, UUID]],
        accepted_submissions: list[MiniGameSubmission],
        now: datetime,
    ) -> MechanicProgress:
        phase = state.get("phase")
        if phase == "input":
            auto_submissions = list(accepted_submissions)
            synthetic_submissions: list[MechanicSyntheticSubmission] = []
            submitted = self._input_submissions(accepted_submissions)
            for char_id, _participant_id in participants:
                if char_id in submitted:
                    continue
                synthetic = self._synthetic_submission(
                    char_id,
                    {
                        "action": "input",
                        "statement_text": "",
                        "declared_truth": True,
                        "auto_submitted": True,
                    },
                )
                auto_submissions.append(synthetic)
                synthetic_submissions.append(
                    MechanicSyntheticSubmission(
                        submission_id=synthetic.submission_id,
                        character_id=synthetic.character_id,
                        payload=synthetic.payload,
                        submitted_at=synthetic.submitted_at,
                    )
                )
            progress = self._start_spotlight_phase(
                snapshot,
                dict(state),
                participants,
                auto_submissions,
                now,
            )
            return MechanicProgress(
                state=progress.state,
                deadline=progress.deadline,
                finalize_status=progress.finalize_status,
                events=progress.events,
                synthetic_submissions=tuple(synthetic_submissions),
            )
        if phase == "spotlight":
            return self._resolve_current_spotlight(
                snapshot,
                dict(state),
                participants,
                accepted_submissions,
                now,
            )
        return MechanicProgress(state=dict(state), finalize_status="completed")

    def _start_spotlight_phase(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        state: dict[str, Any],
        participants: list[tuple[UUID, UUID]],
        submissions: list[MiniGameSubmission],
        now: datetime,
    ) -> MechanicProgress:
        input_map = self._input_submissions(submissions)
        seed = self._seed(snapshot)
        spotlight_order = sorted(
            input_map,
            key=lambda char_id: sha256(f"{seed}:{char_id}".encode("utf-8")).hexdigest(),
        )
        state["phase"] = "spotlight"
        state["input_closed"] = True
        state["spotlight_order"] = [str(char_id) for char_id in spotlight_order]
        state["current_spotlight_index"] = 0
        return self._advance_skips(snapshot, state, participants, submissions, now)

    def _advance_skips(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        state: dict[str, Any],
        participants: list[tuple[UUID, UUID]],
        submissions: list[MiniGameSubmission],
        now: datetime,
    ) -> MechanicProgress:
        events: list[MechanicEventDirective] = []
        presence = dict(state.get("presence", {}))
        order = [UUID(value) for value in state.get("spotlight_order", [])]
        index = int(state.get("current_spotlight_index", 0))
        while index < len(order) and not presence.get(str(order[index]), True):
            skipped_id = order[index]
            events.append(
                MechanicEventDirective(
                    category=EventCategory.state_transition,
                    event_type="tmst_spotlight_skipped",
                    target_audience=AudienceTarget.all,
                    payload={
                        "target_character_id": str(skipped_id),
                        "reason": "disconnected",
                    },
                )
            )
            index += 1
        state["current_spotlight_index"] = index
        if index >= len(order):
            return self._scoreboard_progress(snapshot, submissions, now, events, state)
        target = order[index]
        eligible_voter_ids = [
            str(char_id)
            for char_id in self._eligible_voters(target, participants, presence)
        ]
        events.append(
            MechanicEventDirective(
                category=EventCategory.state_transition,
                event_type="tmst_spotlight_started",
                target_audience=AudienceTarget.all,
                payload={
                    "phase": "spotlight",
                    "target_character_id": str(target),
                    "eligible_voter_ids": eligible_voter_ids,
                    "deadline": (
                        now + timedelta(seconds=VOTE_WINDOW_SECONDS)
                    ).isoformat(),
                },
            )
        )
        return MechanicProgress(
            state=state,
            deadline=now + timedelta(seconds=VOTE_WINDOW_SECONDS),
            events=tuple(events),
        )

    def _resolve_current_spotlight(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        state: dict[str, Any],
        participants: list[tuple[UUID, UUID]],
        submissions: list[MiniGameSubmission],
        now: datetime,
    ) -> MechanicProgress:
        target = self._current_target(state, participants)
        if target is None:
            return self._scoreboard_progress(snapshot, submissions, now, [], state)
        input_map = self._input_submissions(submissions)
        input_submission = input_map[target]
        votes = self._votes_for_target(submissions, target)
        presence = dict(state.get("presence", {}))
        eligible_voters = self._eligible_voters(target, participants, presence)
        abstaining_ids = [
            char_id for char_id in eligible_voters if str(char_id) not in votes
        ]
        vote_breakdown = {
            "truth": sum(1 for vote in votes.values() if vote == "truth"),
            "lie": sum(1 for vote in votes.values() if vote == "lie"),
            "abstain": len(abstaining_ids),
        }
        reveal_event = MechanicEventDirective(
            category=EventCategory.state_transition,
            event_type="tmst_reveal_resolved",
            target_audience=AudienceTarget.all,
            payload={
                "phase": "reveal",
                "target_character_id": str(target),
                "declared_truth": input_submission["declared_truth"],
                "statement_text": input_submission["statement_text"],
                "vote_breakdown": vote_breakdown,
                "abstaining_character_ids": [
                    str(char_id) for char_id in abstaining_ids
                ],
            },
        )
        state["current_spotlight_index"] = (
            int(state.get("current_spotlight_index", 0)) + 1
        )
        next_progress = self._advance_skips(
            snapshot,
            state,
            participants,
            submissions,
            now,
        )
        return MechanicProgress(
            state=next_progress.state,
            deadline=next_progress.deadline,
            finalize_status=next_progress.finalize_status,
            events=(reveal_event, *next_progress.events),
        )

    def _scoreboard_progress(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
        now: datetime,
        prior_events: list[MechanicEventDirective],
        state: dict[str, Any],
    ) -> MechanicProgress:
        outcome = self.score(
            snapshot=snapshot,
            submissions=submissions,
        )
        scoreboard_event = MechanicEventDirective(
            category=EventCategory.state_transition,
            event_type="tmst_scoreboard_ready",
            target_audience=AudienceTarget.all,
            payload={
                "phase": "scoreboard",
                "scores": outcome["scores"],
                "all_truth_round": outcome["all-truth-round"],
                "all_lie_round": outcome["all-lie-round"],
                "deflection_tendency": outcome["runtime_signals"][
                    "deflection_tendency"
                ],
            },
        )
        state["phase"] = "scoreboard"
        return MechanicProgress(
            state=state,
            deadline=now,
            finalize_status="completed",
            events=tuple([*prior_events, scoreboard_event]),
        )

    @staticmethod
    def _seed(snapshot: ResolvedMiniGameSnapshot) -> str:
        resolved_seed = snapshot.resolved_content.get("run_seed")
        if isinstance(resolved_seed, str) and resolved_seed:
            return resolved_seed
        return snapshot.game_id

    @staticmethod
    def _input_submissions(
        submissions: list[MiniGameSubmission],
    ) -> dict[UUID, dict[str, Any]]:
        result: dict[UUID, dict[str, Any]] = {}
        for submission in submissions:
            if submission.payload.get("action") != "input":
                continue
            result[submission.character_id] = {
                "statement_text": str(submission.payload.get("statement_text", "")),
                "declared_truth": bool(submission.payload.get("declared_truth")),
            }
        return result

    @staticmethod
    def _votes_for_target(
        submissions: list[MiniGameSubmission],
        target_character_id: UUID,
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        for submission in submissions:
            if submission.payload.get("action") != "vote":
                continue
            if (
                UUID(str(submission.payload.get("target_character_id")))
                != target_character_id
            ):
                continue
            result[str(submission.character_id)] = str(submission.payload["vote"])
        return result

    def _reveal_records(
        self,
        submissions: list[MiniGameSubmission],
        spotlight_order: list[UUID],
    ) -> list[dict[str, Any]]:
        input_map = self._input_submissions(submissions)
        presence = self._presence_map(submissions)
        results: list[dict[str, Any]] = []
        for target in spotlight_order:
            votes = self._votes_for_target(submissions, target)
            abstaining_ids = [
                char_id
                for char_id in spotlight_order
                if char_id != target
                and presence.get(str(char_id), True)
                and str(char_id) not in votes
            ]
            vote_breakdown = {
                "truth": sum(1 for vote in votes.values() if vote == "truth"),
                "lie": sum(1 for vote in votes.values() if vote == "lie"),
                "abstain": len(abstaining_ids),
            }
            results.append(
                {
                    "target_character_id": target,
                    "declared_truth": input_map[target]["declared_truth"],
                    "statement_text": input_map[target]["statement_text"],
                    "votes": votes,
                    "vote_breakdown": vote_breakdown,
                    "abstaining_character_ids": abstaining_ids,
                }
            )
        return results

    @staticmethod
    def _presence_map(submissions: list[MiniGameSubmission]) -> dict[str, bool]:
        presence: dict[str, bool] = defaultdict(lambda: True)
        for submission in submissions:
            if submission.payload.get("action") != "presence":
                continue
            presence[str(submission.character_id)] = bool(
                submission.payload.get("connected")
            )
        return dict(presence)

    def _spotlight_order(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
        input_map: dict[UUID, dict[str, Any]],
    ) -> list[UUID]:
        presence = self._presence_map(submissions)
        seed = self._seed(snapshot)
        ordered = sorted(
            input_map,
            key=lambda char_id: sha256(f"{seed}:{char_id}".encode("utf-8")).hexdigest(),
        )
        return [char_id for char_id in ordered if presence.get(str(char_id), True)]

    @staticmethod
    def _eligible_voters(
        target_character_id: UUID,
        participants: list[tuple[UUID, UUID]],
        presence: dict[str, bool],
    ) -> list[UUID]:
        return [
            char_id
            for char_id, _participant_id in participants
            if char_id != target_character_id and presence.get(str(char_id), True)
        ]

    @staticmethod
    def _has_prior_action(
        submissions: list[MiniGameSubmission],
        character_id: UUID,
        action: str,
    ) -> bool:
        return any(
            submission.character_id == character_id
            and submission.payload.get("action") == action
            for submission in submissions
        )

    @staticmethod
    def _has_prior_vote(
        submissions: list[MiniGameSubmission],
        character_id: UUID,
        target_character_id: UUID,
    ) -> bool:
        return any(
            submission.character_id == character_id
            and submission.payload.get("action") == "vote"
            and UUID(str(submission.payload.get("target_character_id")))
            == target_character_id
            for submission in submissions
        )

    @staticmethod
    def _synthetic_submission(
        character_id: UUID,
        payload: dict[str, Any],
    ) -> MiniGameSubmission:
        return MiniGameSubmission(
            submission_id=f"synthetic-{character_id}",
            run_id=UUID(int=0),
            character_id=character_id,
            submitted_at=datetime.now(tz=timezone.utc),
            payload=payload,
            is_accepted=True,
        )

    @staticmethod
    def _current_target(
        state: dict[str, Any],
        participants: list[tuple[UUID, UUID]],
    ) -> UUID | None:
        order = [UUID(value) for value in state.get("spotlight_order", [])]
        index = int(state.get("current_spotlight_index", 0))
        if index >= len(order):
            return None
        return order[index]
