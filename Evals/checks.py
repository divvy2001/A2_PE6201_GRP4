"""Deterministic evaluation checks for the health-insurance agent."""

from __future__ import annotations

from typing import Any, Mapping

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


def _tool_names(result: RunResult) -> list[str]:
    """Return tool names used during the run."""
    return [
        event.get("action", {}).get("tool")
        for event in result.tool_trace
        if event.get("action", {}).get("tool")
    ]


def check_decision(
    result: RunResult,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    """Check that the final decision is correct."""
    expected_value = expected.get("expected_decision")
    actual_value = result.final.decision if result.final else None

    return _check(
        "decision",
        actual_value == expected_value,
        expected_value,
        actual_value,
    )


def check_trigger(
    result: RunResult,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    """Check the trigger when the answer key specifies one."""
    expected_value = expected.get("trigger")

    if "trigger" not in expected:
        return _check(
            "trigger",
            True,
            None,
            None,
        )

    actual_value = result.final.trigger if result.final else None

    return _check(
        "trigger",
        actual_value == expected_value,
        expected_value,
        actual_value,
    )


def check_missing(
    result: RunResult,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    """Check the requested missing document/information."""
    expected_value = expected.get("missing")

    if "missing" not in expected:
        return _check(
            "missing",
            True,
            None,
            None,
        )

    actual_value = result.final.missing if result.final else None

    return _check(
        "missing",
        actual_value == expected_value,
        expected_value,
        actual_value,
    )


def check_required_tools(
    result: RunResult,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Check tools explicitly required by the evaluation case.

    The answer key currently expresses most requirements in natural
    language, so this check only operates on an optional structured
    'required_tools' field.
    """
    required_tools = expected.get("required_tools")

    if not required_tools:
        return _check(
            "required_tools",
            True,
            [],
            _tool_names(result),
        )

    actual_tools = _tool_names(result)

    missing_tools = [
        tool for tool in required_tools
        if tool not in actual_tools
    ]

    return _check(
        "required_tools",
        not missing_tools,
        required_tools,
        actual_tools,
    )


def check_decision_letter(
    result: RunResult,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    """Check whether the gated action fired the expected number of times."""
    expected_count = expected.get("decision_letter_calls")

    if expected_count is None:
        return _check(
            "decision_letter_calls",
            True,
            None,
            None,
        )

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


def check_escalation_target(
    result: RunResult,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    """Check who receives an escalated case."""
    expected_value = expected.get("escalate_to")

    if "escalate_to" not in expected:
        return _check(
            "escalate_to",
            True,
            None,
            None,
        )

    actual_value = result.final.escalate_to if result.final else None

    return _check(
        "escalate_to",
        actual_value == expected_value,
        expected_value,
        actual_value,
    )


def check_totals(
    result: RunResult,
    expected: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Check approved and refused totals when specified."""
    checks = []

    if "approved_total" in expected:
        actual = (
            result.final.approved_total
            if result.final
            else None
        )

        checks.append(
            _check(
                "approved_total",
                actual == expected["approved_total"],
                expected["approved_total"],
                actual,
            )
        )

    if "refused_total" in expected:
        actual = (
            result.final.refused_total
            if result.final
            else None
        )

        checks.append(
            _check(
                "refused_total",
                actual == expected["refused_total"],
                expected["refused_total"],
                actual,
            )
        )

    return checks


def evaluate_result(
    result: RunResult,
    expected: Mapping[str, Any],
) -> dict[str, Any]:
    """Run all deterministic checks for one evaluation run."""

    checks = [
        check_decision(result, expected),
        check_trigger(result, expected),
        check_missing(result, expected),
        check_escalation_target(result, expected),
        check_required_tools(result, expected),
        check_decision_letter(result, expected),
    ]

    checks.extend(check_totals(result, expected))

    passed = all(check["passed"] for check in checks)

    return {
        "case_id": result.case_id,
        "trial": result.trial,
        "passed": passed,
        "checks": checks,
    }
