"""Deterministic checks for health-insurance agent evaluation."""

from __future__ import annotations

from typing import Any

from src.schemas import RunResult


def _check(
    name: str,
    passed: bool,
    expected: Any,
    actual: Any,
) -> dict[str, Any]:
    """Create a standard result for one evaluation check."""
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
    """Check that the agent reached the expected decision."""

    expected_decision = expected.get("decision")
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
    """Check that the agent used the expected routing trigger."""

    expected_trigger = expected.get("trigger")
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
    """Check the exact missing item for request-document cases."""

    expected_missing = expected.get("missing")
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
    """Check who the claim should be escalated to."""

    expected_target = expected.get("escalate_to")
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
    """Check the total amount approved in principle."""

    expected_total = expected.get("approved_total")
    actual_total = result.final.approved_total if result.final else None

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
    """Check the total amount refused."""

    expected_total = expected.get("refused_total")
    actual_total = result.final.refused_total if result.final else None

    return _check(
        "refused_total",
        actual_total == expected_total,
        expected_total,
        actual_total,
    )


def check_gated_action(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    """Check whether the gated decision-letter action fired as expected."""

    expected_count = expected.get("decision_letter_calls", 0)

    actual_count = sum(
        1
        for event in result.tool_trace
        if event.get("action", {}).get("tool") == "issue_decision_letter"
    )

    return _check(
        "decision_letter_calls",
        actual_count == expected_count,
        expected_count,
        actual_count,
    )


def evaluate_result(
    result: RunResult,
    expected: dict[str, Any],
) -> dict[str, Any]:
    """Run all applicable deterministic checks for one case."""

    checks = [
        check_decision(result, expected),
        check_trigger(result, expected),
    ]

    if "missing" in expected:
        checks.append(check_missing(result, expected))

    if "escalate_to" in expected:
        checks.append(check_escalation_target(result, expected))

    if "approved_total" in expected:
        checks.append(check_approved_total(result, expected))

    if "refused_total" in expected:
        checks.append(check_refused_total(result, expected))

    if "decision_letter_calls" in expected:
        checks.append(check_gated_action(result, expected))

    passed = all(check["passed"] for check in checks)

    return {
        "case_id": result.case_id,
        "passed": passed,
        "checks": checks,
    }
