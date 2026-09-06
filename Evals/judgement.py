"""
L2 evaluation checks using an LLM-as-a-judge.

This layer evaluates whether the agent recorded the required information
in its final decision. It is intentionally separate from deterministic
checks in checks.py.
"""

from __future__ import annotations

import json
from typing import Any

from src.schemas import FinalDecision
from src.backends.base import ModelBackend


JUDGE_SYSTEM_PROMPT = """
You are an evaluation judge for a health-insurance claims agent.

Your task is to determine whether the agent's FINAL DECISION RECORD
contains every piece of information required by the evaluation criteria.

Important rules:

1. Evaluate what the agent actually recorded in the final decision.
2. Do NOT give credit merely because information appears in the tool trace.
3. The agent may express the requirement using different wording.
   Judge semantic equivalence, not exact string matching.
4. Do not infer information that the agent did not record.
5. Each requirement must be evaluated independently.
6. A requirement passes only if the final decision clearly communicates
   the required information.
7. Return exactly one JSON object. Do not include markdown or explanation
   outside the JSON object.

Required output format:

{
  "passed": true,
  "checks": [
    {
      "requirement": "...",
      "passed": true,
      "reason": "..."
    }
  ]
}

"passed" must be true only when ALL individual checks pass.
"""


def build_judge_input(
    *,
    case_id: str,
    requirements: list[str],
    final_decision: FinalDecision,
) -> list[dict[str, str]]:
    """
    Build the messages sent to the LLM judge.

    Only the final decision is treated as evidence of what was recorded.
    """

    final_record = {
        "decision": final_decision.decision,
        "trigger": final_decision.trigger,
        "missing": final_decision.missing,
        "escalate_to": final_decision.escalate_to,
        "line_dispositions": final_decision.line_dispositions,
        "approved_total": final_decision.approved_total,
        "refused_total": final_decision.refused_total,
        "evidence": final_decision.evidence,
    }

    user_payload = {
        "case_id": case_id,
        "requirements": requirements,
        "final_decision": final_record,
    }

    return [
        {
            "role": "system",
            "content": JUDGE_SYSTEM_PROMPT.strip(),
        },
        {
            "role": "user",
            "content": json.dumps(user_payload, indent=2),
        },
    ]


def _parse_judge_response(text: str) -> dict[str, Any]:
    """Parse and validate the judge's JSON response."""

    cleaned = text.strip()

    # Allow the judge to accidentally return a fenced JSON block.
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"JUDGE_INVALID_JSON: {exc}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError("JUDGE_INVALID_OUTPUT: expected JSON object")

    if "passed" not in result:
        raise ValueError("JUDGE_INVALID_OUTPUT: missing 'passed'")

    if "checks" not in result:
        raise ValueError("JUDGE_INVALID_OUTPUT: missing 'checks'")

    if not isinstance(result["passed"], bool):
        raise ValueError("JUDGE_INVALID_OUTPUT: 'passed' must be boolean")

    if not isinstance(result["checks"], list):
        raise ValueError("JUDGE_INVALID_OUTPUT: 'checks' must be a list")

    for check in result["checks"]:
        if not isinstance(check, dict):
            raise ValueError(
                "JUDGE_INVALID_OUTPUT: each check must be an object"
            )

        required_fields = {"requirement", "passed", "reason"}

        if not required_fields.issubset(check):
            raise ValueError(
                "JUDGE_INVALID_OUTPUT: check missing required fields"
            )

        if not isinstance(check["passed"], bool):
            raise ValueError(
                "JUDGE_INVALID_OUTPUT: check 'passed' must be boolean"
            )

    return result


def judge_must_record(
    *,
    case_id: str,
    requirements: list[str],
    final_decision: FinalDecision,
    backend: ModelBackend,
    model: str,
) -> dict[str, Any]:
    """
    Run the L2 LLM judge against the agent's final decision.

    Returns a structured judgement result.
    """

    if not requirements:
        return {
            "status": "not_required",
            "passed": True,
            "checks": [],
            "judge_model": model,
        }

    messages = build_judge_input(
        case_id=case_id,
        requirements=requirements,
        final_decision=final_decision,
    )

    response = backend.generate(
        messages,
        model=model,
        temperature=0.0,
    )

    try:
        result = _parse_judge_response(response.text)
    except ValueError as exc:
        return {
            "status": "error",
            "passed": False,
            "checks": [],
            "judge_model": model,
            "error": str(exc),
            "tokens_in": response.tokens_in,
            "tokens_out": response.tokens_out,
            "cost_usd": response.cost_usd,
        }

    # Protect against a judge incorrectly returning passed=true
    # while one of the individual requirements failed.
    all_checks_passed = all(
        check["passed"]
        for check in result["checks"]
    )

    # Also make sure every requested requirement was actually judged.
    judged_requirements = {
        check["requirement"]
        for check in result["checks"]
    }

    all_requirements_judged = all(
        requirement in judged_requirements
        for requirement in requirements
    )

    passed = (
        result["passed"]
        and all_checks_passed
        and all_requirements_judged
    )

    return {
        "status": "completed",
        "passed": passed,
        "checks": result["checks"],
        "judge_model": model,
        "tokens_in": response.tokens_in,
        "tokens_out": response.tokens_out,
        "cost_usd": response.cost_usd,
    }
