"""The once-a-second loop logs failures without flooding or going quiet
(AW-338, spec 0093 Part C).

No database and no real clock: the pass is patched and time is a counter.
"""

from __future__ import annotations

import asyncio
import logging

import pytest

from api import tick_loop


class _Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


async def _run(
    monkeypatch: pytest.MonkeyPatch,
    outcomes: list[bool],
    clock: _Clock,
    step: float,
) -> None:
    """Run the loop once per outcome (True = the pass fails), then stop."""
    queue = list(outcomes)

    async def fake_pass(*_args: object) -> int:
        if queue.pop(0):
            raise RuntimeError("database is down")
        return 0

    async def fake_sleep(_seconds: float) -> None:
        clock.now += step
        if not queue:
            raise asyncio.CancelledError

    monkeypatch.setattr(tick_loop, "tick_active_sessions", fake_pass)
    monkeypatch.setattr(tick_loop, "get_session_factory", lambda: None)
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(tick_loop, "_monotonic", clock)
    with pytest.raises(asyncio.CancelledError):
        await tick_loop.run_tick_loop(0)


def _failures(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.levelno >= logging.ERROR]


class TestFailureLogging:
    @pytest.mark.asyncio
    async def test_the_first_failure_logs_at_once(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        await _run(monkeypatch, [True], _Clock(), 1.0)
        assert len(_failures(caplog)) == 1

    @pytest.mark.asyncio
    async def test_later_failures_inside_the_window_are_counted_not_logged(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        await _run(monkeypatch, [True] * 5, _Clock(), 1.0)
        assert len(_failures(caplog)) == 1

    @pytest.mark.asyncio
    async def test_a_failure_after_the_window_logs_with_the_count_it_skipped(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        await _run(monkeypatch, [True] * 40, _Clock(), 1.0)
        failures = _failures(caplog)
        assert len(failures) == 2
        assert "29 more" in failures[1].getMessage()

    @pytest.mark.asyncio
    async def test_recovery_logs_one_info_line_with_the_failed_pass_count(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        await _run(monkeypatch, [True, True, True, False], _Clock(), 1.0)
        recovered = [r for r in caplog.records if "recovered" in r.getMessage()]
        assert len(recovered) == 1
        assert "3 failed passes" in recovered[0].getMessage()

    @pytest.mark.asyncio
    async def test_a_healthy_loop_logs_nothing(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)
        await _run(monkeypatch, [False] * 3, _Clock(), 1.0)
        assert caplog.records == []
