from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from unittest import mock

import pytest

from ops.billing_guard import main

CLOUDSQL_BUDGET_ID = "937d66a3-d08c-424a-a0c3-e469c3e1c36f"
CLOUDRUN_BUDGET_ID = "e24a2acf-ca1a-47c5-973f-1336eb64cd18"


def _envelope(
    payload: dict | None,
    valid_json: bool = True,
    valid_base64: bool = True,
    billing_account_id: str | None = "010472-A5F484-E66D1D",
    budget_id: str | None = CLOUDSQL_BUDGET_ID,
) -> dict:
    if payload is None:
        return {"message": {}}
    if not valid_json:
        data = base64.b64encode(b"not json").decode()
    elif not valid_base64:
        data = "not-valid-base64!!!"
    else:
        data = base64.b64encode(json.dumps(payload).encode()).decode()
    attributes = {}
    if billing_account_id is not None:
        attributes["billingAccountId"] = billing_account_id
    if budget_id is not None:
        attributes["budgetId"] = budget_id
    return {"message": {"data": data, "attributes": attributes}}


# billingAccountId and budgetId are real Cloud Billing notification Pub/Sub
# message *attributes*, not part of the data payload — see _envelope's
# billing_account_id / budget_id parameters.
VALID_PAYLOAD = {
    "budgetDisplayName": "rehearsal2-cloudsql",
    "costAmount": 9.0,
    "budgetAmount": 10.0,
    "currencyCode": "USD",
}


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv(
        "ALLOWED_BUDGET_IDS", f"{CLOUDSQL_BUDGET_ID},{CLOUDRUN_BUDGET_ID}"
    )
    monkeypatch.setenv("EXPECTED_BILLING_ACCOUNT_ID", "010472-A5F484-E66D1D")
    monkeypatch.setenv("BILLING_GUARD_DRY_RUN", "true")


def test_target_project_never_equals_identity_project():
    assert main.TARGET_PROJECT_ID != main.FORBIDDEN_PROJECT_ID


def test_assert_invariants_passes_by_default():
    main._assert_invariants()


def test_parse_notification_rejects_missing_message():
    with pytest.raises(main.InvalidNotification):
        main.parse_notification({})


def test_parse_notification_rejects_invalid_base64():
    with pytest.raises(main.InvalidNotification):
        main.parse_notification(_envelope(VALID_PAYLOAD, valid_base64=False))


def test_parse_notification_rejects_invalid_json():
    with pytest.raises(main.InvalidNotification):
        main.parse_notification(_envelope(VALID_PAYLOAD, valid_json=False))


def test_parse_notification_rejects_missing_fields():
    with pytest.raises(main.InvalidNotification):
        main.parse_notification(_envelope({"budgetDisplayName": "x"}))


def test_parse_notification_accepts_valid_payload():
    notification = main.parse_notification(_envelope(VALID_PAYLOAD))
    assert notification.budget_display_name == "rehearsal2-cloudsql"
    assert notification.cost_amount == 9.0


@pytest.mark.parametrize("bad_cost", ["NaN", "Infinity", "-Infinity"])
def test_parse_notification_rejects_non_finite_cost_amount(bad_cost):
    """NaN/Infinity comparisons are always False, so a non-finite
    costAmount would otherwise sail past every numeric guard in
    should_trigger_shutdown (never triggering, but also never being
    rejected as malformed) instead of being refused up front."""
    with pytest.raises(main.InvalidNotification):
        main.parse_notification(_envelope({**VALID_PAYLOAD, "costAmount": bad_cost}))


@pytest.mark.parametrize("bad_budget", ["NaN", "Infinity", "-Infinity"])
def test_parse_notification_rejects_non_finite_budget_amount(bad_budget):
    with pytest.raises(main.InvalidNotification):
        main.parse_notification(
            _envelope({**VALID_PAYLOAD, "budgetAmount": bad_budget})
        )


def test_parse_notification_rejects_negative_cost_amount():
    with pytest.raises(main.InvalidNotification):
        main.parse_notification(_envelope({**VALID_PAYLOAD, "costAmount": -1.0}))


def test_should_trigger_shutdown_rejects_unrecognized_budget_id():
    notification = main.parse_notification(
        _envelope(
            {**VALID_PAYLOAD, "budgetDisplayName": "some-other-budget"},
            budget_id="00000000-0000-0000-0000-000000000000",
        )
    )
    assert main.should_trigger_shutdown(notification) is False


def test_should_trigger_shutdown_rejects_display_name_collision_with_wrong_id():
    """A budgetDisplayName that matches the allowlist's expected name is not
    enough — the display name is mutable and can collide across budgets.
    Only the immutable budget_id authorizes shutdown."""
    notification = main.parse_notification(
        _envelope(
            VALID_PAYLOAD,  # budgetDisplayName: "rehearsal2-cloudsql"
            budget_id="00000000-0000-0000-0000-000000000000",
        )
    )
    assert main.should_trigger_shutdown(notification) is False


def test_should_trigger_shutdown_rejects_wrong_billing_account():
    notification = main.parse_notification(
        _envelope(VALID_PAYLOAD, billing_account_id="999999-WRONG-ACCOUNT")
    )
    assert main.should_trigger_shutdown(notification) is False


def test_parse_notification_rejects_missing_billing_account_attribute():
    with pytest.raises(main.InvalidNotification):
        main.parse_notification(_envelope(VALID_PAYLOAD, billing_account_id=None))


def test_should_trigger_shutdown_rejects_below_threshold():
    low = main.parse_notification(_envelope({**VALID_PAYLOAD, "costAmount": 5.0}))
    assert main.should_trigger_shutdown(low) is False


def test_should_trigger_shutdown_accepts_at_threshold():
    notification = main.parse_notification(
        _envelope({**VALID_PAYLOAD, "costAmount": 8.0})
    )
    assert main.should_trigger_shutdown(notification) is True


def test_should_trigger_shutdown_rejects_non_positive_budget():
    notification = main.parse_notification(
        _envelope({**VALID_PAYLOAD, "budgetAmount": 0})
    )
    assert main.should_trigger_shutdown(notification) is False


def test_disable_billing_refuses_non_target_project():
    with pytest.raises(main.GuardMisconfiguredError):
        main._disable_billing("some-other-project")


def test_stop_cloud_sql_refuses_non_target_project():
    with pytest.raises(main.GuardMisconfiguredError):
        main._stop_cloud_sql_instance("some-other-project", main.TARGET_SQL_INSTANCE)


def test_stop_cloud_sql_refuses_non_target_instance():
    with pytest.raises(main.GuardMisconfiguredError):
        main._stop_cloud_sql_instance(main.TARGET_PROJECT_ID, "some-other-instance")


def test_execute_shutdown_dry_run_takes_no_real_action():
    with (
        mock.patch.object(main, "_stop_cloud_sql_instance") as stop_sql,
        mock.patch.object(main, "_disable_billing") as disable_billing,
        mock.patch.object(main, "_is_billing_already_disabled") as billing_disabled,
    ):
        result = main.execute_shutdown(dry_run=True)
    stop_sql.assert_not_called()
    disable_billing.assert_not_called()
    billing_disabled.assert_not_called()
    assert result["dry_run"] is True
    assert "dry_run:would_disable_billing" in result["actions"]


def test_execute_shutdown_is_idempotent_when_already_disabled():
    """Billing-disable is skipped once already disabled, but Cloud SQL stop
    is still attempted every time — a first-attempt SQL failure must be
    retried on redelivery instead of being silently abandoned once billing
    is off."""
    with (
        mock.patch.object(
            main, "_is_billing_already_disabled", return_value=True
        ) as billing_disabled,
        mock.patch.object(main, "_stop_cloud_sql_instance") as stop_sql,
        mock.patch.object(main, "_disable_billing") as disable_billing,
    ):
        result = main.execute_shutdown(dry_run=False)
    billing_disabled.assert_called_once_with(main.TARGET_PROJECT_ID)
    stop_sql.assert_called_once_with(main.TARGET_PROJECT_ID, main.TARGET_SQL_INSTANCE)
    disable_billing.assert_not_called()
    assert result["actions"] == ["stopped_cloud_sql", "noop:billing_already_disabled"]


def test_execute_shutdown_stops_sql_then_disables_billing():
    with (
        mock.patch.object(main, "_is_billing_already_disabled", return_value=False),
        mock.patch.object(main, "_stop_cloud_sql_instance") as stop_sql,
        mock.patch.object(main, "_disable_billing") as disable_billing,
    ):
        result = main.execute_shutdown(dry_run=False)
    stop_sql.assert_called_once_with(main.TARGET_PROJECT_ID, main.TARGET_SQL_INSTANCE)
    disable_billing.assert_called_once_with(main.TARGET_PROJECT_ID)
    assert result["actions"] == ["stopped_cloud_sql", "disabled_billing"]


def test_execute_shutdown_still_disables_billing_if_sql_stop_fails():
    with (
        mock.patch.object(main, "_is_billing_already_disabled", return_value=False),
        mock.patch.object(
            main, "_stop_cloud_sql_instance", side_effect=RuntimeError("boom")
        ),
        mock.patch.object(main, "_disable_billing") as disable_billing,
    ):
        result = main.execute_shutdown(dry_run=False)
    disable_billing.assert_called_once_with(main.TARGET_PROJECT_ID)
    assert "failed_stop_cloud_sql" in result["actions"]
    assert "disabled_billing" in result["actions"]


@dataclass
class _FakeCloudEvent:
    data: dict


def test_handle_budget_notification_ignores_malformed_message():
    event = _FakeCloudEvent(data={"message": {}})
    result = main.handle_budget_notification(event)
    assert result["action"] == "ignored"


def test_handle_budget_notification_ignores_unrelated_budget():
    event = _FakeCloudEvent(
        data=_envelope(
            {**VALID_PAYLOAD, "budgetDisplayName": "unrelated-budget"},
            budget_id="00000000-0000-0000-0000-000000000000",
        )
    )
    result = main.handle_budget_notification(event)
    assert result["action"] == "ignored"


def test_handle_budget_notification_dry_run_does_not_call_real_apis(monkeypatch):
    monkeypatch.setenv("BILLING_GUARD_DRY_RUN", "true")
    event = _FakeCloudEvent(data=_envelope({**VALID_PAYLOAD, "costAmount": 9.5}))
    with (
        mock.patch.object(main, "_stop_cloud_sql_instance") as stop_sql,
        mock.patch.object(main, "_disable_billing") as disable_billing,
    ):
        result = main.handle_budget_notification(event)
    stop_sql.assert_not_called()
    disable_billing.assert_not_called()
    assert result["dry_run"] is True
