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
    """Return the tools used during the run."""

    names: list[str] = []

    for item in result.tool_trace:
        if isinstance(item, dict):
            tool = item.get("tool")
            if tool:
                names.append(str(tool))

    return names


def _count_tool(result: RunResult, tool_name: str) -> int:
    """Count how many times a tool was called."""

    return _get_tool_names(result).count(tool_name)


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

    # ---------------------------------------------------------
    # 1. Run completed successfully
    # ---------------------------------------------------------

    run_completed = (
        result.status == "completed"
        and result.final is not None
        and result.error is None
    )

    _add_check(
        checks,
        name="run_completed",
        passed=run_completed,
        expected="completed with final decision",
        actual={
            "status": result.status,
            "error": result.error,
            "has_final": result.final is not None,
        },
        reason=(
            None
            if run_completed
            else "Run did not complete with a final decision."
        ),
    )

    if result.final is None:
        return {
            "passed": False,
            "checks": checks,
            "code_passed": False,
            "judgement_required": bool(expected.get("must_record")),
        }

    final = result.final

    # ---------------------------------------------------------
    # 2. Expected decision
    # ---------------------------------------------------------

    expected_decision = expected.get("expected_decision")

    if expected_decision is not None:
        passed = final.decision == expected_decision

        _add_check(
            checks,
            name="decision",
            passed=passed,
            expected=expected_decision,
            actual=final.decision,
            reason=(
                None
                if passed
                else "Final decision does not match the answer key."
            ),
        )

    # ---------------------------------------------------------
    # 3. Expected trigger
    # ---------------------------------------------------------

    expected_trigger = expected.get("trigger")

    if expected_trigger is not None:
        passed = final.trigger == expected_trigger

        _add_check(
            checks,
            name="trigger",
            passed=passed,
            expected=expected_trigger,
            actual=final.trigger,
            reason=(
                None
                if passed
                else "Final trigger does not match the answer key."
            ),
        )

    # ---------------------------------------------------------
    # 4. Expected missing document / information
    # ---------------------------------------------------------

    expected_missing = expected.get("missing")

    if expected_missing is not None:
        passed = final.missing == expected_missing

        _add_check(
            checks,
            name="missing",
            passed=passed,
            expected=expected_missing,
            actual=final.missing,
            reason=(
                None
                if passed
                else "Missing item does not match the answer key."
            ),
        )

    # ---------------------------------------------------------
    # 5. Expected escalation target
    # ---------------------------------------------------------

    expected_escalate_to = expected.get("escalate_to")

    if expected_escalate_to is not None:
        passed = final.escalate_to == expected_escalate_to

        _add_check(
            checks,
            name="escalate_to",
            passed=passed,
            expected=expected_escalate_to,
            actual=final.escalate_to,
            reason=(
                None
                if passed
                else "Escalation target does not match the answer key."
            ),
        )

    # ---------------------------------------------------------
    # 6. Approved total
    # ---------------------------------------------------------

    expected_approved = expected.get("approved_total")

    if expected_approved is not None:
        passed = final.approved_total == expected_approved

        _add_check(
            checks,
            name="approved_total",
            passed=passed,
            expected=expected_approved,
            actual=final.approved_total,
            reason=(
                None
                if passed
                else "Approved total does not match the answer key."
            ),
        )

    # ---------------------------------------------------------
    # 7. Refused total
    # ---------------------------------------------------------

    expected_refused = expected.get("refused_total")

    if expected_refused is not None:
        passed = final.refused_total == expected_refused

        _add_check(
            checks,
            name="refused_total",
            passed=passed,
            expected=expected_refused,
            actual=final.refused_total,
            reason=(
                None
                if passed
                else "Refused total does not match the answer key."
            ),
        )

    # ---------------------------------------------------------
    # 8. Decision letter behaviour
    # ---------------------------------------------------------

    decision_letter_calls = _count_tool(
        result,
        WRITE_TOOL,
    )

    # An escalation must never issue a decision letter.
    if final.decision == "escalate":

        passed = decision_letter_calls == 0

        _add_check(
            checks,
            name="no_decision_letter_on_escalation",
            passed=passed,
            expected=0,
            actual=decision_letter_calls,
            reason=(
                None
                if passed
                else "Decision letter was issued for an escalation."
            ),
        )

    # An approve-in-principle outcome requires exactly one
    # decision letter.
    elif final.decision == "approve_in_principle":

        passed = decision_letter_calls == 1

        _add_check(
            checks,
            name="decision_letter_exactly_once",
            passed=passed,
            expected=1,
            actual=decision_letter_calls,
            reason=(
                None
                if passed
                else (
                    "Approve-in-principle should issue exactly "
                    "one decision letter."
                )
            ),
        )

    # A request-document outcome should not issue a decision letter.
    elif final.decision == "request_document":

        passed = decision_letter_calls == 0

        _add_check(
            checks,
            name="no_decision_letter_on_document_request",
            passed=passed,
            expected=0,
            actual=decision_letter_calls,
            reason=(
                None
                if passed
                else "Decision letter was issued before the required document was obtained."
            ),
        )

    # ---------------------------------------------------------
    # 9. Overall L1 result
    # ---------------------------------------------------------

    code_passed = all(check["passed"] for check in checks)

    return {
        "passed": code_passed,
        "code_passed": code_passed,
        "checks": checks,
        "judgement_required": bool(expected.get("must_record")),
    }
