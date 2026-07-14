"""Idempotent billing guard for the Cloud Rehearsal 2 disposable runtime project.

Deployed as a Pub/Sub-triggered Cloud Function. Cloud Billing budget alerts for
the disposable runtime project publish to a Pub/Sub topic this function
subscribes to. On a message that indicates the runtime project has crossed the
configured stop threshold, the guard disables billing for that project and
stops its Cloud SQL instance.

Design constraints (see docs/superpowers/specs/2026-07-12-cloud-rehearsal-2-cost-isolation-design.md):
  - The target project is a hardcoded constant, never derived from the
    incoming message. This makes it structurally impossible for a malformed
    or spoofed notification to redirect the shutdown at a different project,
    including `arcwright-53ea3`.
  - The guard only acts on messages whose `budgetDisplayName` is in the
    configured allow-list and whose `billingAccountId` matches the expected
    billing account. Anything else is logged and ignored.
  - Shutdown is idempotent: it checks current billing state before acting, so
    redelivered or duplicate Pub/Sub messages are safe no-ops.
  - No secret values are read, logged, or required by this function.
"""

from __future__ import annotations

import base64
import json
import logging
import math
import os
from dataclasses import dataclass

import functions_framework
import googleapiclient.discovery
from google.cloud import billing_v1

logger = logging.getLogger("billing_guard")
logger.setLevel(logging.INFO)

# Hardcoded, not derived from any incoming message. This is the single
# authoritative target of every destructive action this function can take.
TARGET_PROJECT_ID = "arcwright-rehearsal-2"
TARGET_SQL_INSTANCE = "arcwright-rehearsal-db"

# Never allow the target constant above to equal the identity project, even
# if someone edits this file carelessly.
FORBIDDEN_PROJECT_ID = "arcwright-53ea3"

# Stop threshold as a fraction of each service's $10 budget (i.e. $8).
STOP_THRESHOLD_RATIO = 0.8


class GuardMisconfiguredError(RuntimeError):
    """Raised if this module's own safety invariants are violated."""


def _assert_invariants() -> None:
    if TARGET_PROJECT_ID == FORBIDDEN_PROJECT_ID:
        raise GuardMisconfiguredError(
            "billing guard target project must never equal the Firebase identity project"
        )


@dataclass(frozen=True)
class BudgetNotification:
    budget_display_name: str
    budget_id: str
    billing_account_id: str
    cost_amount: float
    budget_amount: float
    currency_code: str


class InvalidNotification(ValueError):
    """The Pub/Sub message is not a usable budget notification."""


def parse_notification(envelope: dict) -> BudgetNotification:
    """Parse and validate a Cloud Billing budget Pub/Sub envelope.

    Real Cloud Billing notifications split the payload across two
    places: identifier fields (billingAccountId, budgetId,
    schemaVersion) are Pub/Sub message *attributes*, while budget
    details (display name, amounts, currency) are in the base64-encoded
    message *data* JSON. See
    https://docs.cloud.google.com/billing/docs/how-to/budgets-programmatic-notifications#notification_format

    Raises InvalidNotification for anything malformed, missing required
    fields, or not shaped like a budget notification. Callers must treat
    InvalidNotification as a safe no-op, not an error to retry.
    """
    message = envelope.get("message") if envelope else None
    if not message or "data" not in message:
        raise InvalidNotification("envelope missing message.data")

    attributes = message.get("attributes") or {}
    billing_account_id = attributes.get("billingAccountId")
    if not billing_account_id:
        raise InvalidNotification("message.attributes missing billingAccountId")
    budget_id = attributes.get("budgetId")
    if not budget_id:
        raise InvalidNotification("message.attributes missing budgetId")

    try:
        raw = base64.b64decode(message["data"]).decode("utf-8")
        payload = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise InvalidNotification(
            f"message.data is not valid base64 JSON: {exc}"
        ) from exc

    required = ("budgetDisplayName", "costAmount", "budgetAmount")
    missing = [field for field in required if field not in payload]
    if missing:
        raise InvalidNotification(f"payload missing required fields: {missing}")

    try:
        cost_amount = float(payload["costAmount"])
        budget_amount = float(payload["budgetAmount"])
    except (TypeError, ValueError) as exc:
        raise InvalidNotification(
            f"payload fields have unexpected types: {exc}"
        ) from exc

    # float() accepts "NaN"/"Infinity" strings and non-finite JSON numbers.
    # A NaN cost or budget would otherwise sail through every numeric guard
    # below (NaN comparisons are always False), reaching execute_shutdown.
    if not (math.isfinite(cost_amount) and math.isfinite(budget_amount)):
        raise InvalidNotification(
            f"non-finite amount: costAmount={cost_amount!r} budgetAmount={budget_amount!r}"
        )
    if cost_amount < 0 or budget_amount < 0:
        raise InvalidNotification(
            f"negative amount: costAmount={cost_amount!r} budgetAmount={budget_amount!r}"
        )

    return BudgetNotification(
        budget_display_name=str(payload["budgetDisplayName"]),
        budget_id=str(budget_id),
        billing_account_id=str(billing_account_id),
        cost_amount=cost_amount,
        budget_amount=budget_amount,
        currency_code=str(payload.get("currencyCode", "USD")),
    )


def _allowed_budget_ids() -> frozenset[str]:
    """Immutable Cloud Billing budget resource IDs this guard may act on.

    Deliberately not budgetDisplayName: display names are mutable and can
    collide with another budget in the same billing account, letting an
    unrelated budget's alert trigger this project's shutdown. budgetId is
    the immutable resource ID assigned at budget creation.
    """
    raw = os.environ.get("ALLOWED_BUDGET_IDS", "")
    return frozenset(name.strip() for name in raw.split(",") if name.strip())


def _expected_billing_account() -> str:
    return os.environ.get("EXPECTED_BILLING_ACCOUNT_ID", "")


def should_trigger_shutdown(notification: BudgetNotification) -> bool:
    """Decide whether this notification authorizes a shutdown action.

    Every check here is a precondition. Any single failed check means "do
    not act" — there is no partial-trust path.
    """
    if notification.budget_id not in _allowed_budget_ids():
        logger.info(
            "ignoring notification for unrecognized budget id %r (name %r, not in allow-list)",
            notification.budget_id,
            notification.budget_display_name,
        )
        return False

    expected_account = _expected_billing_account()
    if not expected_account or notification.billing_account_id != expected_account:
        logger.info("ignoring notification for unexpected billing account")
        return False

    if notification.budget_amount <= 0:
        logger.info("ignoring notification with non-positive budget_amount")
        return False

    ratio = notification.cost_amount / notification.budget_amount
    if ratio < STOP_THRESHOLD_RATIO:
        logger.info(
            "budget %r at %.0f%% of target, below %.0f%% stop threshold",
            notification.budget_display_name,
            ratio * 100,
            STOP_THRESHOLD_RATIO * 100,
        )
        return False

    logger.warning(
        "budget %r at %.0f%% of target, at/above stop threshold - shutdown authorized",
        notification.budget_display_name,
        ratio * 100,
    )
    return True


def _is_billing_already_disabled(project_id: str) -> bool:
    client = billing_v1.CloudBillingClient()
    info = client.get_project_billing_info(name=f"projects/{project_id}")
    return not info.billing_enabled


def _disable_billing(project_id: str) -> None:
    _assert_invariants()
    if project_id != TARGET_PROJECT_ID:
        raise GuardMisconfiguredError(
            f"refusing to disable billing for non-target project {project_id!r}"
        )
    client = billing_v1.CloudBillingClient()
    client.update_project_billing_info(
        name=f"projects/{project_id}",
        project_billing_info=billing_v1.ProjectBillingInfo(billing_account_name=""),
    )
    logger.warning("billing disabled for project %s", project_id)


def _stop_cloud_sql_instance(project_id: str, instance_id: str) -> None:
    _assert_invariants()
    if project_id != TARGET_PROJECT_ID or instance_id != TARGET_SQL_INSTANCE:
        raise GuardMisconfiguredError(
            f"refusing to stop non-target Cloud SQL instance {project_id}:{instance_id}"
        )
    sqladmin = googleapiclient.discovery.build(
        "sqladmin", "v1beta4", cache_discovery=False
    )
    body = {"settings": {"activationPolicy": "NEVER"}}
    sqladmin.instances().patch(
        project=project_id, instance=instance_id, body=body
    ).execute()
    logger.warning(
        "Cloud SQL instance %s stopped (activationPolicy=NEVER)", instance_id
    )


def execute_shutdown(dry_run: bool) -> dict:
    """Perform the idempotent shutdown sequence for the hardcoded target project.

    Checks current state before acting so repeated invocations (duplicate
    Pub/Sub delivery) are safe no-ops once the project is already stopped.
    """
    _assert_invariants()
    result = {"project": TARGET_PROJECT_ID, "dry_run": dry_run, "actions": []}

    if dry_run:
        result["actions"].append("dry_run:would_stop_cloud_sql")
        result["actions"].append("dry_run:would_disable_billing")
        return result

    # Cloud SQL stop is attempted on every invocation, independent of
    # whether billing is already disabled: patching an already-stopped
    # instance to activationPolicy=NEVER is a safe no-op, but skipping it
    # entirely once billing is disabled means a first-attempt SQL stop
    # failure is never retried on redelivery — leaving the instance
    # running (and billing) while the handler reports success.
    try:
        _stop_cloud_sql_instance(TARGET_PROJECT_ID, TARGET_SQL_INSTANCE)
        result["actions"].append("stopped_cloud_sql")
    except Exception:  # noqa: BLE001 - log and continue to the billing kill switch regardless
        logger.exception(
            "failed to stop Cloud SQL instance; continuing to billing disable"
        )
        result["actions"].append("failed_stop_cloud_sql")

    if _is_billing_already_disabled(TARGET_PROJECT_ID):
        result["actions"].append("noop:billing_already_disabled")
        return result

    _disable_billing(TARGET_PROJECT_ID)
    result["actions"].append("disabled_billing")
    return result


@functions_framework.cloud_event
def handle_budget_notification(cloud_event) -> dict:
    """Cloud Functions (2nd gen) Pub/Sub entry point.

    `cloud_event.data` is the Pub/Sub push envelope. Any failure to parse or
    validate the message is logged and treated as a no-op — this function
    never raises for malformed or unrelated input, only for its own
    misconfiguration (GuardMisconfiguredError), which should fail loudly.
    """
    _assert_invariants()
    envelope = getattr(cloud_event, "data", None) or {}

    try:
        notification = parse_notification(envelope)
    except InvalidNotification as exc:
        logger.info("ignoring malformed/unrelated Pub/Sub message: %s", exc)
        return {"action": "ignored", "reason": str(exc)}

    if not should_trigger_shutdown(notification):
        return {"action": "ignored", "reason": "below_threshold_or_unrecognized"}

    dry_run = os.environ.get("BILLING_GUARD_DRY_RUN", "true").lower() == "true"
    outcome = execute_shutdown(dry_run=dry_run)
    logger.warning("billing guard outcome: %s", json.dumps(outcome))
    return outcome
