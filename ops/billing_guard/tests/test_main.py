from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from unittest import mock

import pytest

from ops.billing_guard import main


def _envelope(
    payload: dict | None, valid_json: bool = True, valid_base64: bool = True
) -> dict:
    if payload is None:
        return {"message": {}}
    if not valid_json:
        data = base64.b64encode(b"not json").decode()
    elif not valid_base64:
        data = "not-valid-base64!!!"
    else:
        data = base64.b64encode(json.dumps(payload).encode()).decode()
    return {"message": {"data": data}}


VALID_PAYLOAD = {
    "budgetDisplayName": "rehearsal2-cloudsql",
    "billingAccountId": "010472-A5F484-E66D1D",
    "costAmount": 9.0,
    "budgetAmount": 10.0,
    "currencyCode": "USD",
}


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv(
        "ALLOWED_BUDGET_NAMES", "rehearsal2-cloudsql,rehearsal2-cloudrun"
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


def test_should_trigger_shutdown_rejects_unrecognized_budget_name():
    notification = main.parse_notification(
        _envelope({**VALID_PAYLOAD, "budgetDisplayName": "some-other-budget"})
    )
    assert main.should_trigger_shutdown(notification) is False


def test_should_trigger_shutdown_rejects_wrong_billing_account():
    notification = main.parse_notification(
        _envelope({**VALID_PAYLOAD, "billingAccountId": "999999-WRONG-ACCOUNT"})
    )
    assert main.should_trigger_shutdown(notification) is False


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
    with (
        mock.patch.object(
            main, "_is_billing_already_disabled", return_value=True
        ) as billing_disabled,
        mock.patch.object(main, "_stop_cloud_sql_instance") as stop_sql,
        mock.patch.object(main, "_disable_billing") as disable_billing,
    ):
        result = main.execute_shutdown(dry_run=False)
    billing_disabled.assert_called_once_with(main.TARGET_PROJECT_ID)
    stop_sql.assert_not_called()
    disable_billing.assert_not_called()
    assert result["actions"] == ["noop:billing_already_disabled"]


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
        data=_envelope({**VALID_PAYLOAD, "budgetDisplayName": "unrelated-budget"})
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
