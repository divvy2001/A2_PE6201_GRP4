"""
L1 deterministic evaluation checks for Problem A.

These checks compare the agent's structured RunResult against the
expected outcome in expected_outcomes_A.json.

No LLM or human judgement is used here.

Code checks cover fixed, machine-checkable fields such as:
- final decision
- escalation trigger
- missing item
- escalation destination
- approved/refused totals
- gated decision-letter behavior

Semantic/prose requirements in `must_record` are intentionally left
to the L2 judgement layer.
"""

from __future__ import annotations

from typing import Any

from src.schemas import RunResult


WRITE_TOOL = "issue_decision_letter"


def _get_tool_names(result: RunResult) -> list[str]:
    """Return the tools actually called during the run."""

    names: list[str] = []

    for item in result.tool_trace:
        if not isinstance(item, dict):
            continue

        action = item.get("action")

        if not isinstance(action, dict):
            continue

        tool = action.get("tool")

        if tool:
            names.append(str(tool))

    return names


def _count_tool(result: RunResult, tool_name: str) -> int:
    """Count how many times a particular tool was called."""

    return _get_tool_names(result).count(tool_name)


def _get_observation_data(
    item: dict[str, Any],
) -> dict[str, Any] | None:
    """Return the observation data from one tool-trace entry."""

    observation = item.get("observation")

    if isinstance(observation, dict):
        data = observation.get("data")

        if isinstance(data, dict):
            return data

        return None

    # Defensive support for an Observation-like object.
    data = getattr(observation, "data", None)

    if isinstance(data, dict):
        return data

    return None


def _get_logged_decision_letters(
    result: RunResult,
) -> list[dict[str, Any]]:
    """
    Return decision-letter observations that were actually logged.

    Calling issue_decision_letter is NOT sufficient.

    For example:

        issue_decision_letter
            -> logged=False
            -> gate_result=CONFIRMATION_REQUIRED

    means the gated action was attempted but not executed.

    Only observations with logged=True count as executed writes.
    """

    logged: list[dict[str, Any]] = []

    for item in result.tool_trace:
        if not isinstance(item, dict):
            continue

        action = item.get("action")

        if not isinstance(action, dict):
            continue

        if action.get("tool") != WRITE_TOOL:
            continue

        data = _get_observation_data(item)

        if isinstance(data, dict) and data.get("logged") is True:
            logged.append(data)

    return logged


def _count_logged_decision_letters(result: RunResult) -> int:
    """Count decision letters that were actually logged."""

    return len(_get_logged_decision_letters(result))


def _add_check(
    checks: list[dict[str, Any]],
    name: str,
    passed: bool,
    expected: Any = None,
    actual: Any = None,
    reason: str | None = None,
) -> None:
    """Append one deterministic check result."""

    checks.append(
        {
            "name": name,
            "passed": bool(passed),
            "expected": expected,
            "actual": actual,
            "reason": reason,
        }
    )


def evaluate_result(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    """
    Run all deterministic L1 checks for one evaluation case.

    Answer-key fields used here:

        expected_decision
        trigger
        missing
        escalate_to
        approved_total
        refused_total

    The `must_record` field is deliberately NOT checked here.
    It belongs to the L2 judgement layer because those requirements
    involve semantic/prose quality.
    """

    checks: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # 1. Run completed successfully
    # ------------------------------------------------------------------

    run_completed = (
        result.status == "completed"
        and result.final is not None
        and result.error is None
    )

    _add_check(
        checks,
        name="run_completed",
        passed=run_completed,
        expected="completed run with final decision and no error",
        actual={
            "status": result.status,
            "has_final": result.final is not None,
            "error": result.error,
        },
    )

    # There is no meaningful final-decision checking without a final.
    if result.final is None:
        return {
            "passed": False,
            "code_passed": False,
            "checks": checks,
            "judgement_required": bool(expected.get("must_record")),
            "judgement_passed": None,
        }

    final = result.final

    # ------------------------------------------------------------------
    # 2. Decision
    # ------------------------------------------------------------------

    expected_decision = expected.get("expected_decision")
    actual_decision = final.decision

    _add_check(
        checks,
        name="decision",
        passed=actual_decision == expected_decision,
        expected=expected_decision,
        actual=actual_decision,
    )

    # ------------------------------------------------------------------
    # 3. Trigger
    #
    # Fixed-list field -> code check.
    # Only check when supplied by the answer key.
    # ------------------------------------------------------------------

    if "trigger" in expected:
        expected_trigger = expected.get("trigger")
        actual_trigger = final.trigger

        _add_check(
            checks,
            name="trigger",
            passed=actual_trigger == expected_trigger,
            expected=expected_trigger,
            actual=actual_trigger,
        )

    # ------------------------------------------------------------------
    # 4. Missing item
    #
    # Fixed required item -> code check.
    # ------------------------------------------------------------------

    if "missing" in expected:
        expected_missing = expected.get("missing")
        actual_missing = final.missing

        _add_check(
            checks,
            name="missing",
            passed=actual_missing == expected_missing,
            expected=expected_missing,
            actual=actual_missing,
        )

    # ------------------------------------------------------------------
    # 5. Escalation destination
    #
    # Fixed-list field -> code check.
    # ------------------------------------------------------------------

    if "escalate_to" in expected:
        expected_escalate_to = expected.get("escalate_to")
        actual_escalate_to = final.escalate_to

        _add_check(
            checks,
            name="escalate_to",
            passed=actual_escalate_to == expected_escalate_to,
            expected=expected_escalate_to,
            actual=actual_escalate_to,
        )

    # ------------------------------------------------------------------
    # 6. Approved total
    # ------------------------------------------------------------------

    if "approved_total" in expected:
        expected_approved = expected.get("approved_total")
        actual_approved = final.approved_total

        _add_check(
            checks,
            name="approved_total",
            passed=actual_approved == expected_approved,
            expected=expected_approved,
            actual=actual_approved,
        )

    # ------------------------------------------------------------------
    # 7. Refused total
    # ------------------------------------------------------------------

    if "refused_total" in expected:
        expected_refused = expected.get("refused_total")
        actual_refused = final.refused_total

        _add_check(
            checks,
            name="refused_total",
            passed=actual_refused == expected_refused,
            expected=expected_refused,
            actual=actual_refused,
        )

    # ------------------------------------------------------------------
    # 8. Gated decision-letter action
    #
    # Problem A has one irreversible/gated action:
    #
    #     issue_decision_letter
    #
    # Expected behavior:
    #
    #     approve_in_principle -> exactly one logged letter
    #     request_document     -> zero logged letters
    #     escalate             -> zero logged letters
    #
    # IMPORTANT:
    #     An attempted call is NOT an executed write.
    #
    # We therefore check `observation.data["logged"]`, not merely
    # whether issue_decision_letter appears in the trace.
    # ------------------------------------------------------------------

    attempted_letters = _count_tool(result, WRITE_TOOL)
    logged_letters = _count_logged_decision_letters(result)

    if actual_decision == "approve_in_principle":

        _add_check(
            checks,
            name="decision_letter_gate",
            passed=logged_letters == 1,
            expected="exactly 1 logged decision letter",
            actual={
                "attempted": attempted_letters,
                "logged": logged_letters,
            },
            reason=(
                "An approved claim must have exactly one executed "
                "decision-letter write."
            ),
        )

    elif actual_decision in {
        "request_document",
        "escalate",
    }:

        _add_check(
            checks,
            name="decision_letter_gate",
            passed=logged_letters == 0,
            expected="0 logged decision letters",
            actual={
                "attempted": attempted_letters,
                "logged": logged_letters,
            },
            reason=(
                f"{actual_decision} must not result in an executed "
                "decision-letter write."
            ),
        )

    else:

        _add_check(
            checks,
            name="decision_letter_gate",
            passed=False,
            expected="supported decision type",
            actual=actual_decision,
            reason="Unknown decision type.",
        )

    # ------------------------------------------------------------------
    # 9. Overall deterministic result
    # ------------------------------------------------------------------

    code_passed = all(
        check["passed"]
        for check in checks
    )

    judgement_required = bool(
        expected.get("must_record")
    )

    return {
        "passed": code_passed,
        "code_passed": code_passed,
        "checks": checks,
        "judgement_required": judgement_required,
        "judgement_passed": None,
    }
