"""Run one deterministic end-to-end smoke test for Problem A tools."""

from __future__ import annotations

import json

from src.agent.loop import run_agent
from src.agent.prompt_loader import load_prompt
from src.backends.scripted import ScriptedBackend
from src.schemas import GuardConfig
from src.tools.versioned import get_versioned_tool_registry


def main() -> None:
    """Exercise all seven tools through the loop using the v2 contract."""
    prompt_version = "v2"
    tool_registry = get_versioned_tool_registry(prompt_version)

    responses = [
        json.dumps(
            {
                "type": "action_block",
                "reasoning_summary": "Retrieve the claim facts first.",
                "actions": [
                    {
                        "call_id": "t01-c01",
                        "tool": "get_claim",
                        "args": {"case_id": "CLM-8842"},
                    }
                ],
            }
        ),
        json.dumps(
            {
                "type": "action_block",
                "reasoning_summary": "Retrieve the member policy.",
                "actions": [
                    {
                        "call_id": "t02-c01",
                        "tool": "lookup_policy",
                        "args": {"member_id": "M-2214"},
                    }
                ],
            }
        ),
        json.dumps(
            {
                "type": "action_block",
                "reasoning_summary": "Check the treatment hospital.",
                "actions": [
                    {
                        "call_id": "t03-c01",
                        "tool": "get_hospital_status",
                        "args": {"hospital_id": "H-114"},
                    }
                ],
            }
        ),
        json.dumps(
            {
                "type": "action_block",
                "reasoning_summary": "Check coverage for one claimed procedure.",
                "actions": [
                    {
                        "call_id": "t04-c01",
                        "tool": "check_coverage",
                        "args": {
                            "member_id": "M-2214",
                            "procedure_code": "62480",
                            "attached_documents": [
                                "itemised_bill",
                                "discharge_summary",
                            ],
                        },
                    }
                ],
            }
        ),
        json.dumps(
            {
                "type": "action_block",
                "reasoning_summary": "Check pre-authorisation evidence.",
                "actions": [
                    {
                        "call_id": "t05-c01",
                        "tool": "get_preauthorisation",
                        "args": {
                            "member_id": "M-2214",
                            "procedure_code": "62480",
                            "date_of_service": "2026-09-02",
                        },
                    }
                ],
            }
        ),
        json.dumps(
            {
                "type": "action_block",
                "reasoning_summary": "Check for a matching prior claim.",
                "actions": [
                    {
                        "call_id": "t06-c01",
                        "tool": "check_duplicate_claim",
                        "args": {
                            "member_id": "M-2214",
                            "hospital_id": "H-114",
                            "date_of_service": "2026-09-02",
                            "lines": [
                                {"code": "47120", "amount": 1400},
                                {"code": "62480", "amount": 780},
                                {"code": "31255", "amount": 300},
                            ],
                        },
                    }
                ],
            }
        ),
        json.dumps(
            {
                "type": "action_block",
                "reasoning_summary": "Record the completed in-principle decision.",
                "actions": [
                    {
                        "call_id": "t07-c01",
                        "tool": "issue_decision_letter",
                        "args": {
                            "case_id": "CLM-8842",
                            "decision_record": {
                                "decision": "approve_in_principle",
                                "trigger": None,
                                "missing": None,
                                "escalate_to": None,
                                "line_dispositions": [
                                    {
                                        "code": "47120",
                                        "amount": 1400,
                                        "outcome": "covered",
                                        "reason": "covered procedure",
                                        "evidence": ["coverage and policy checks"],
                                    },
                                    {
                                        "code": "62480",
                                        "amount": 780,
                                        "outcome": "covered",
                                        "reason": "valid pre-authorisation",
                                        "evidence": ["PA-5521"],
                                    },
                                    {
                                        "code": "31255",
                                        "amount": 300,
                                        "outcome": "refused",
                                        "reason": "EX-14 cosmetic dermatology exclusion",
                                        "evidence": ["EX-14"],
                                    },
                                ],
                                "approved_total": 2180,
                                "refused_total": 300,
                                "evidence": [
                                    "Policy, coverage, pre-authorisation, hospital and duplicate checks completed."
                                ],
                            },
                        },
                    }
                ],
            }
        ),

        json.dumps(
            {
                "type": "final",
                "final": {
                    "decision": "approve_in_principle",
                    "trigger": None,
                    "missing": None,
                    "escalate_to": None,
                    "line_dispositions": [
                        {
                            "code": "47120",
                            "amount": 1400,
                            "outcome": "covered",
                            "reason": "covered procedure",
                            "evidence": ["coverage and policy checks"],
                        },
                        {
                            "code": "62480",
                            "amount": 780,
                            "outcome": "covered",
                            "reason": "valid pre-authorisation",
                            "evidence": ["PA-5521"],
                        },
                        {
                            "code": "31255",
                            "amount": 300,
                            "outcome": "refused",
                            "reason": "EX-14 cosmetic dermatology exclusion",
                            "evidence": ["EX-14"],
                        },
                    ],
                    "approved_total": 2180,
                    "refused_total": 300,
                    "evidence": [
                        "Policy, coverage, pre-authorisation, hospital and duplicate checks completed."
                    ],
                },
            }
        ),
    ]

    result = run_agent(
        case_id="CLM-8842",
        backend=ScriptedBackend(responses),
        model="scripted",
        parallel_tools=False,
        autonomy="confirm",
        max_steps=8,
        budget_usd=0.0,
        guard_config=GuardConfig(),
        tool_registry=tool_registry,
        prompt_version=prompt_version,
        system_prompt=load_prompt(prompt_version),
        operator_approved=True,
    )

    called_tools = {
        item["action"]["tool"]
        for item in result.tool_trace
    }
    expected_tools = set(tool_registry)
    write_observations = [
        item["observation"]
        for item in result.tool_trace
        if item["action"]["tool"] == "issue_decision_letter"
    ]

    if result.status != "completed" or result.final is None:
        raise RuntimeError(f"Smoke test did not complete: {result.error}")
    if called_tools != expected_tools:
        raise RuntimeError(
            f"Smoke test tool coverage mismatch: {called_tools} != {expected_tools}"
        )
    if result.final.decision != "approve_in_principle":
        raise RuntimeError("Smoke test produced the wrong final decision")
    if not write_observations or write_observations[0]["data"].get("logged") is not True:
        raise RuntimeError("Smoke test did not verify the gated JSONL write")

    print("Status:", result.status)
    print("Run ID:", result.run_id)
    print("Tool calls:", result.tool_calls)
    print("Final decision:", result.final.decision if result.final else None)
    print("Error:", result.error)

    for item in result.tool_trace:
        print(json.dumps(item, indent=2))


if __name__ == "__main__":
    main()
