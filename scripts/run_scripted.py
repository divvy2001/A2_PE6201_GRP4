"""Run one deterministic end-to-end smoke test for Problem A tools."""

from __future__ import annotations

import json

from src.agent.loop import run_agent
from src.backends.scripted import ScriptedBackend
from src.schemas import GuardConfig
from src.tools.problem_a import TOOLS


def main() -> None:
    """Run one scripted tool call followed by a safe final escalation."""
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
                            "procedure_code": "47120",
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
                            "procedure_code": "47120",
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
                "reasoning_summary": "Record the gated local escalation decision.",
                "actions": [
                    {
                        "call_id": "t07-c01",
                        "tool": "issue_decision_letter",
                        "args": {
                            "case_id": "CLM-8842",
                            "decision_record": {
                                "decision": "escalate",
                                "trigger": "SCRIPTED_READ_ONLY_TOOL_CHAIN",
                                "missing": None,
                                "escalate_to": "manual_review",
                                "line_dispositions": [],
                                "approved_total": 0,
                                "refused_total": 0,
                                "evidence": [
                                    "Completed the scripted read-only Problem A tool chain."
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
                    "decision": "escalate",
                    "trigger": "SCRIPTED_READ_ONLY_TOOL_CHAIN",
                    "missing": None,
                    "escalate_to": "manual_review",
                    "line_dispositions": [],
                    "approved_total": 0,
                    "refused_total": 0,
                    "evidence": [
                        "Completed the scripted read-only Problem A tool chain."
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
        tool_registry=TOOLS,
        prompt_version="v2",
        operator_approved=True,
    )

    print("Status:", result.status)
    print("Run ID:", result.run_id)
    print("Tool calls:", result.tool_calls)
    print("Final decision:", result.final.decision if result.final else None)
    print("Error:", result.error)

    for item in result.tool_trace:
        print(json.dumps(item, indent=2))


if __name__ == "__main__":
    main()