"""Deterministic checks for the health-insurance agent evaluation."""

from __future__ import annotations

from typing import Any

from src.schemas import RunResult


def _check(
    name: str,
    passed: bool,
    expected: Any,
    actual: Any,
) -> dict[str, Any]:
    return {
        "name": name,
        "passed": passed,
        "expected": expected,
        "actual": actual,
    }


def check_decision(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    expected_decision = expected.get("expected_decision")
    actual_decision = result.final.decision if result.final else None

    return _check(
        "decision",
        actual_decision == expected_decision,
        expected_decision,
        actual_decision,
    )


def check_trigger(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    # Trigger is only required for escalation cases.
    if "trigger" not in expected:
        return _check(
            "trigger",
            True,
            None,
            None,
        )

    expected_trigger = expected["trigger"]
    actual_trigger = result.final.trigger if result.final else None

    return _check(
        "trigger",
        actual_trigger == expected_trigger,
        expected_trigger,
        actual_trigger,
    )


def check_missing(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    # Missing is only required for request_document cases.
    if "missing" not in expected:
        return _check(
            "missing",
            True,
            None,
            None,
        )

    expected_missing = expected["missing"]
    actual_missing = result.final.missing if result.final else None

    return _check(
        "missing",
        actual_missing == expected_missing,
        expected_missing,
        actual_missing,
    )


def check_escalation_target(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    if "escalate_to" not in expected:
        return _check(
            "escalate_to",
            True,
            None,
            None,
        )

    expected_target = expected["escalate_to"]
    actual_target = result.final.escalate_to if result.final else None

    return _check(
        "escalate_to",
        actual_target == expected_target,
        expected_target,
        actual_target,
    )


def check_approved_total(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    if "approved_total" not in expected:
        return _check(
            "approved_total",
            True,
            None,
            None,
        )

    expected_total = expected["approved_total"]
    actual_total = (
        result.final.approved_total
        if result.final
        else None
    )

    return _check(
        "approved_total",
        actual_total == expected_total,
        expected_total,
        actual_total,
    )


def check_refused_total(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    if "refused_total" not in expected:
        return _check(
            "refused_total",
            True,
            None,
            None,
        )

    expected_total = expected["refused_total"]
    actual_total = (
        result.final.refused_total
        if result.final
        else None
    )

    return _check(
        "refused_total",
        actual_total == expected_total,
        expected_total,
        actual_total,
    )


def check_run_completed(
    result: RunResult,
) -> dict[str, Any]:
    return _check(
        "run_completed",
        result.status == "completed" and result.final is not None,
        "completed",
        result.status,
    )


def check_decision_letter_calls(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    if "decision_letter_calls" not in expected:
        return _check(
            "decision_letter_calls",
            True,
            None,
            None,
        )

    expected_count = expected["decision_letter_calls"]

    actual_count = sum(
        1
        for event in result.tool_trace
        if event.get("action", {}).get("tool")
        == "issue_decision_letter"
    )

    return _check(
        "decision_letter_calls",
        actual_count == expected_count,
        expected_count,
        actual_count,
    )


def check_no_write_on_escalation(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    """
    Escalation cases should not issue a decision letter.

    This is a deterministic safety/correctness check. The answer key's
    expected_decision is the source of truth.
    """
    if expected.get("expected_decision") != "escalate":
        return _check(
            "no_write_on_escalation",
            True,
            "not applicable",
            "not applicable",
        )

    actual_count = sum(
        1
        for event in result.tool_trace
        if event.get("action", {}).get("tool")
        == "issue_decision_letter"
    )

    return _check(
        "no_write_on_escalation",
        actual_count == 0,
        0,
        actual_count,
    )


def check_must_record_presence(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    """
    Expose the natural-language 'must_record' requirements.

    These are intentionally NOT treated as exact deterministic string
    matches. They are judgement checks and should later be graded by
    a human or a separate judge model.
    """
    requirements = expected.get("must_record", [])

    return {
        "name": "must_record",
        "passed": None,
        "expected": requirements,
        "actual": (
            result.final.to_dict()
            if result.final
            else None
        ),
        "judgement_required": bool(requirements),
    }


def evaluate_result(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    """Run all deterministic checks for one evaluation case."""

    checks = [
        check_run_completed(result),
        check_decision(result, expected),
        check_trigger(result, expected),
        check_missing(result, expected),
        check_escalation_target(result, expected),
        check_approved_total(result, expected),
        check_refused_total(result, expected),
        check_decision_letter_calls(result, expected),
        check_no_write_on_escalation(result, expected),
    ]

    judgement = check_must_record_presence(result, expected)

    code_passed = all(
        check["passed"]
        for check in checks
    )

    return {
        "case_id": result.case_id,
        "code_passed": code_passed,
        "passed": code_passed,
        "checks": checks,
        "judgement": judgement,
    }
