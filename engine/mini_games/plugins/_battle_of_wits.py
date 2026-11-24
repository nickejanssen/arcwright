"""Authoritative rules for the timed choice and sorting quiz."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, TypeAdapter, model_validator

from engine.db.orm import MiniGameSubmission
from engine.events.models import AudienceTarget, EventCategory
from engine.mini_games.audience_view import AudienceRule
from engine.mini_games.resolver import ResolvedMiniGameSnapshot
from engine.mini_games.runtime import MechanicEventDirective, MechanicProgress

_QUESTION_POINTS = 4


class _Option(BaseModel):
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)


class _Question(BaseModel):
    kind: Literal["choice", "sort"]
    prompt: str = Field(min_length=1)
    options: list[_Option] = Field(min_length=4, max_length=4)
    answer: list[str]

    @model_validator(mode="after")
    def validate_answer(self) -> _Question:
        options = {option.id for option in self.options}
        if len(options) != _QUESTION_POINTS:
            raise ValueError("question options must have distinct IDs")
        expected = 1 if self.kind == "choice" else _QUESTION_POINTS
        if len(self.answer) != expected or len(set(self.answer) & options) != expected:
            raise ValueError(
                "answer must reference the correct number of distinct options"
            )
        return self


_QUESTIONS = TypeAdapter(list[_Question])


def _points(question: dict[str, Any], payload: dict[str, Any]) -> int:
    answer = question["answer"]
    if question["kind"] == "choice":
        return _QUESTION_POINTS if payload["option_id"] == answer[0] else 0
    return sum(given == correct for given, correct in zip(payload["order"], answer))


def _tiers(scores: dict[str, int]) -> list[list[str]]:
    by_score: dict[int, list[str]] = {}
    for character, value in sorted(scores.items()):
        by_score.setdefault(value, []).append(character)
    return [by_score[value] for value in sorted(by_score, reverse=True)]


class BattleOfWitsPlugin:
    mechanic_type = "battle-of-wits"
    audience_rule = AudienceRule(public_state=("stage",), own_state=("player",))

    def prepare_run(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        *,
        run_id: UUID,
        participants: list[tuple[UUID, UUID]],
    ) -> ResolvedMiniGameSnapshot:
        if not snapshot.min_players <= len(participants) <= snapshot.max_players:
            raise ValueError("Battle of Wits requires 1 to 8 seated players")
        if (
            snapshot.definition_version != "0.1.0"
            or snapshot.resolved_content.get("question_set") != "invented-v1"
        ):
            raise ValueError("unknown Battle of Wits question set")
        questions = _QUESTIONS.validate_python(
            snapshot.resolved_content.get("questions")
        )
        if not questions:
            raise ValueError("Battle of Wits requires at least one question")
        clock = ("choice_seconds", "sort_seconds", "reveal_seconds")
        if any(
            type(snapshot.rules.get(key)) is not int or snapshot.rules[key] <= 0
            for key in clock
        ):
            raise ValueError("Battle of Wits requires positive integer phase times")
        seconds = sum(
            snapshot.rules[f"{question.kind}_seconds"]
            + snapshot.rules["reveal_seconds"]
            for question in questions
        )
        if seconds > snapshot.duration_seconds:
            raise ValueError("Battle of Wits phase times exceed its duration")
        return snapshot.model_copy(
            update={
                "resolved_content": {
                    **snapshot.resolved_content,
                    "run_id": str(run_id),
                    "characters": [str(character) for character, _ in participants],
                    "questions": _QUESTIONS.dump_python(questions, mode="json"),
                }
            }
        )

    def validate_payload(self, payload: dict[str, Any]) -> None:
        if (
            type(payload.get("question_index")) is not int
            or payload["question_index"] < 0
        ):
            raise ValueError("answer requires a non-negative question_index")
        base = {"action", "question_index"}
        action = payload.get("action")
        if action == "choice" and payload.keys() == base | {"option_id"}:
            if isinstance(payload["option_id"], str) and payload["option_id"]:
                return
        if action == "sort" and payload.keys() == base | {"order"}:
            order = payload["order"]
            if (
                isinstance(order, list)
                and len(order) == _QUESTION_POINTS
                and all(isinstance(item, str) and item for item in order)
                and len(set(order)) == _QUESTION_POINTS
            ):
                return
        raise ValueError("answer requires one choice or four distinct sorting options")

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
        questions = snapshot.resolved_content["questions"]
        scores = dict.fromkeys(snapshot.resolved_content["characters"], 0)
        for submission in submissions:
            character = str(submission.character_id)
            answer = submission.payload
            points = _points(questions[answer["question_index"]], answer)
            scores[character] = scores.get(character, 0) + points
        return {"scores": scores}

    def standing(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
        outcome: dict[str, Any],
    ) -> list[list[str]]:
        # The shared runtime adds every remaining seat to the same zero tier.
        return _tiers({key: score for key, score in outcome["scores"].items() if score})

    def initialize_state(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        *,
        participants: list[tuple[UUID, UUID]],
        now: datetime,
    ) -> MechanicProgress:
        scores = self.score(snapshot, [])["scores"]
        return self._open_question(snapshot, 0, scores, participants, now)

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
        stage = state["stage"]
        payload = submission.payload
        if stage["phase"] != "question" or payload["question_index"] != stage["index"]:
            raise ValueError("answer does not match the current question")
        character = str(submission.character_id)
        private = state["player"].get(character)
        if private is None:
            raise ValueError("player was not seated at the start")
        if private["locked"]:
            raise ValueError("answer is already locked")
        options = {option["id"] for option in stage["options"]}
        if payload["action"] != stage["kind"]:
            raise ValueError("answer format does not match the current question")
        if stage["kind"] == "choice":
            option = payload["option_id"]
            if option not in options or option in private.get("disabled", ()):
                raise ValueError("answer option is not available")
        else:
            order = payload["order"]
            pin = private.get("pinned")
            if set(order) != options or (pin and order[pin["position"]] != pin["id"]):
                raise ValueError(
                    "sort order must preserve all options and the pre-placed card"
                )
        return MechanicProgress(
            state={
                **state,
                "player": {**state["player"], character: {**private, "locked": True}},
            },
        )

    def on_deadline_expired(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        *,
        state: dict[str, Any],
        participants: list[tuple[UUID, UUID]],
        accepted_submissions: list[MiniGameSubmission],
        now: datetime,
    ) -> MechanicProgress:
        stage = state["stage"]
        index = stage["index"]
        scores = self.score(snapshot, accepted_submissions)["scores"]
        if stage["phase"] == "reveal":
            if index + 1 == stage["total"]:
                status = "completed" if accepted_submissions else "timed_out"
                return MechanicProgress(finalize_status=status)
            return self._open_question(snapshot, index + 1, scores, participants, now)

        question = snapshot.resolved_content["questions"][index]
        correct = sorted(
            str(submission.character_id)
            for submission in accepted_submissions
            if submission.payload["question_index"] == index
            and _points(question, submission.payload) == _QUESTION_POINTS
        )
        reveal = {
            **stage,
            "phase": "reveal",
            "answer": question["answer"],
            "correct": correct,
            "scores": scores,
            "standing": _tiers(scores),
        }
        deadline = now + timedelta(seconds=snapshot.rules["reveal_seconds"])
        return self._stage_progress(snapshot, reveal, {}, participants, deadline)

    def _open_question(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        index: int,
        scores: dict[str, int],
        participants: list[tuple[UUID, UUID]],
        now: datetime,
    ) -> MechanicProgress:
        questions = snapshot.resolved_content["questions"]
        question = questions[index]
        kind = question["kind"]
        stage = {
            "phase": "question",
            "index": index,
            "total": len(questions),
            "kind": kind,
            "prompt": question["prompt"],
            "options": question["options"],
        }
        players: dict[str, dict[str, Any]] = {
            character: {"locked": False} for character in scores
        }
        tiers = _tiers(scores)
        if len(tiers) > 1:
            for character in tiers[-1]:
                if kind == "choice":
                    players[character]["disabled"] = [
                        option["id"]
                        for option in question["options"]
                        if option["id"] != question["answer"][0]
                    ][:2]
                else:
                    players[character]["pinned"] = {
                        "id": question["answer"][0],
                        "position": 0,
                    }
        deadline = now + timedelta(seconds=snapshot.rules[f"{kind}_seconds"])
        return self._stage_progress(snapshot, stage, players, participants, deadline)

    @staticmethod
    def _stage_progress(
        snapshot: ResolvedMiniGameSnapshot,
        stage: dict[str, Any],
        players: dict[str, Any],
        participants: list[tuple[UUID, UUID]],
        deadline: datetime,
    ) -> MechanicProgress:
        run_id = snapshot.resolved_content["run_id"]
        public = {"run_id": run_id, "stage": stage, "deadline_at": deadline.isoformat()}
        events = [
            MechanicEventDirective(
                EventCategory.state_transition,
                "battle_of_wits_stage",
                audience,
                public,
            )
            for audience in (AudienceTarget.all, AudienceTarget.host_only)
        ]
        events.extend(
            MechanicEventDirective(
                EventCategory.private_delivery,
                "battle_of_wits_player",
                AudienceTarget.specific_player,
                {
                    "run_id": run_id,
                    "index": stage["index"],
                    "player": players[str(character)],
                },
                target_player_id=participant,
            )
            for character, participant in participants
            if str(character) in players
        )
        return MechanicProgress(
            state={"stage": stage, "player": players},
            deadline=deadline,
            events=tuple(events),
        )
