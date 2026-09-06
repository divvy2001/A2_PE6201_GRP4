"""
L1 deterministic evaluation checks.

These checks compare the agent's structured RunResult against the
expected outcome in the evaluation answer key.

No LLM or human judgement is used here.
"""

from __future__ import annotations

from typing import Any

from src.schemas import RunResult


WRITE_TOOL = "issue_decision_letter"


def _get_tool_names(result: RunResult) -> list[str]:
    """
    Return the tools actually called during the run.

    tool_trace entries have the structure:

        {
            "turn": ...,
            "action": {
                "call_id": ...,
                "tool": ...,
                "args": ...
            },
            "observation": ...
        }

    Therefore the tool name is nested under:
        item["action"]["tool"]
    """

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


def _get_observation_data(item: dict[str, Any]) -> dict[str, Any] | None:
    """
    Extract observation data from one tool-trace entry.

    The normal trace stores observation as a dictionary, but this helper
    also tolerates an Observation-like object for robustness.
    """

    observation = item.get("observation")

    if isinstance(observation, dict):
        data = observation.get("data")

        if isinstance(data, dict):
            return data

        return None

    # Defensive support if an Observation object is ever stored directly.
    data = getattr(observation, "data", None)

    if isinstance(data, dict):
        return data

    return None


def _count_logged_decision_letters(result: RunResult) -> int:
    """
    Count decision letters that were actually logged.

    This is intentionally different from `_count_tool()`.

    An agent may attempt:

        issue_decision_letter(...)

    but the tool may return:

        CONFIRMATION_REQUIRED

    In that situation the tool was called, but no decision letter was
    actually issued.

    We therefore only count a decision letter when:

        observation.data["logged"] is True
    """

    count = 0

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
            count += 1

    return count


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
            "passed": passed,
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

    Expected answer-key fields currently supported:

        expected_decision
        trigger
        missing
        escalate_to
        approved_total
        refused_total
        must_record

    `must_record` is deliberately NOT evaluated here.
    It belongs to the L2 judgement layer.
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

    # If there is no final decision, the remaining deterministic checks
    # cannot be evaluated.
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
    # 2. Expected decision
    # ------------------------------------------------------------------

    expected_decision = expected.get("expected_decision")
    actual_decision = final.decision

    decision_passed = actual_decision == expected_decision

    _add_check(
        checks,
        name="decision",
        passed=decision_passed,
        expected=expected_decision,
        actual=actual_decision,
    )

    # ------------------------------------------------------------------
    # 3. Trigger
    #
    # Only check the trigger when the answer key specifies one.
    # ------------------------------------------------------------------

    if "trigger" in expected:

        expected_trigger = expected.get("trigger")
        actual_trigger = final.trigger

        trigger_passed = actual_trigger == expected_trigger

        _add_check(
            checks,
            name="trigger",
            passed=trigger_passed,
            expected=expected_trigger,
            actual=actual_trigger,
        )

    # ------------------------------------------------------------------
    # 4. Missing document / item
    #
    # Only check when the answer key specifies `missing`.
    # ------------------------------------------------------------------

    if "missing" in expected:

        expected_missing = expected.get("missing")
        actual_missing = final.missing

        missing_passed = actual_missing == expected_missing

        _add_check(
            checks,
            name="missing",
            passed=missing_passed,
            expected=expected_missing,
            actual=actual_missing,
        )

    # ------------------------------------------------------------------
    # 5. Escalation destination
    #
    # Only check when the answer key specifies `escalate_to`.
    # ------------------------------------------------------------------

    if "escalate_to" in expected:

        expected_escalate_to = expected.get("escalate_to")
        actual_escalate_to = final.escalate_to

        escalate_passed = actual_escalate_to == expected_escalate_to

        _add_check(
            checks,
            name="escalate_to",
            passed=escalate_passed,
            expected=expected_escalate_to,
            actual=actual_escalate_to,
        )

    # ------------------------------------------------------------------
    # 6. Approved total
    #
    # Only check when the answer key specifies it.
    # ------------------------------------------------------------------

    if "approved_total" in expected:

        expected_approved = expected.get("approved_total")
        actual_approved = final.approved_total

        approved_passed = actual_approved == expected_approved

        _add_check(
            checks,
            name="approved_total",
            passed=approved_passed,
            expected=expected_approved,
            actual=actual_approved,
        )

    # ------------------------------------------------------------------
    # 7. Refused total
    #
    # Only check when the answer key specifies it.
    # ------------------------------------------------------------------

    if "refused_total" in expected:

        expected_refused = expected.get("refused_total")
        actual_refused = final.refused_total

        refused_passed = actual_refused == expected_refused

        _add_check(
            checks,
            name="refused_total",
            passed=refused_passed,
            expected=expected_refused,
            actual=actual_refused,
        )

    # ------------------------------------------------------------------
    # 8. Decision-letter gate
    #
    # The expected behavior is:
    #
    #   approve_in_principle -> exactly one ACTUALLY LOGGED letter
    #   request_document     -> no logged letter
    #   escalate             -> no logged letter
    #
    # We deliberately use `_count_logged_decision_letters()` rather than
    # `_count_tool()` because an attempted write is not the same as an
    # irreversible action actually being executed.
    # ------------------------------------------------------------------

    logged_letters = _count_logged_decision_letters(result)

    if actual_decision == "approve_in_principle":

        expected_logged_letters = 1

        letter_passed = logged_letters == expected_logged_letters

        _add_check(
            checks,
            name="decision_letter_gate",
            passed=letter_passed,
            expected="exactly 1 logged decision letter",
            actual={
                "logged_decision_letters": logged_letters,
                "attempted_decision_letters": _count_tool(
                    result,
                    WRITE_TOOL,
                ),
            },
            reason=(
                "An approve_in_principle decision must result in one "
                "actually logged decision letter."
            ),
        )

    elif actual_decision in {
        "request_document",
        "escalate",
    }:

        expected_logged_letters = 0

        letter_passed = logged_letters == expected_logged_letters

        _add_check(
            checks,
            name="decision_letter_gate",
            passed=letter_passed,
            expected="0 logged decision letters",
            actual={
                "logged_decision_letters": logged_letters,
                "attempted_decision_letters": _count_tool(
                    result,
                    WRITE_TOOL,
                ),
            },
            reason=(
                f"{actual_decision} must not result in an issued "
                "decision letter."
            ),
        )

    else:

        # This is mostly defensive. The schema should already prevent
        # unsupported decisions from reaching this point.
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

    judgement_required = bool(expected.get("must_record"))

    return {
        "passed": code_passed,
        "code_passed": code_passed,
        "checks": checks,
        "judgement_required": judgement_required,
        "judgement_passed": None,
    }
