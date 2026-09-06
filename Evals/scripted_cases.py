import json

SCRIPTED_CASES: dict[str, list[str]] = {
    "CLM-8842": [
        json.dumps({
            "type": "action_block",
            "reasoning_summary": "Load the claim first.",
            "actions": [{
                "call_id": "t01-c01",
                "tool": "get_claim",
                "args": {"case_id": "CLM-8842"},
            }],
        }),
        json.dumps({
            "type": "action_block",
            "reasoning_summary": "Run independent policy, coverage, and hospital checks in parallel.",
            "actions": [
                {"call_id": "t02-c01", "tool": "lookup_policy", "args": {"member_id": "M-2214"}},
                {"call_id": "t02-c02", "tool": "check_coverage", "args": {
                    "member_id": "M-2214", "procedure_code": "47120",
                    "attached_documents": ["itemised_bill", "discharge_summary"],
                }},
                {"call_id": "t02-c03", "tool": "check_coverage", "args": {
                    "member_id": "M-2214", "procedure_code": "31255",
                    "attached_documents": ["itemised_bill", "discharge_summary"],
                }},
                {"call_id": "t02-c04", "tool": "check_coverage", "args": {
                    "member_id": "M-2214", "procedure_code": "62480",
                    "attached_documents": ["itemised_bill", "discharge_summary"],
                }},
                {"call_id": "t02-c05", "tool": "get_hospital_status", "args": {"hospital_id": "H-114"}},
            ],
        }),
        json.dumps({
            "type": "action_block",
            "reasoning_summary": "Coverage requires preauthorisation for 62480, so check it.",
            "actions": [{
                "call_id": "t03-c01",
                "tool": "get_preauthorisation",
                "args": {
                    "member_id": "M-2214",
                    "procedure_code": "62480",
                    "date_of_service": "2026-09-02",
                },
            }],
        }),
        json.dumps({
            "type": "action_block",
            "reasoning_summary": "All required facts are resolved; issue the gated decision letter.",
            "actions": [{
                "call_id": "t04-c01",
                "tool": "issue_decision_letter",
                "args": {
                    "case_id": "CLM-8842",
                    "decision_record": {
                        "decision": "approve_in_principle",
                        "trigger": None,
                        "missing": None,
                        "escalate_to": None,
                        "line_dispositions": [
                            {"procedure_code": "47120", "disposition": "approved", "amount": 1400},
                            {"procedure_code": "62480", "disposition": "approved", "amount": 780,
                             "preauthorisation_id": "PA-5521"},
                            {"procedure_code": "31255", "disposition": "refused", "amount": 300,
                             "reason": "EX-14 cosmetic dermatology"},
                        ],
                        "approved_total": 2180,
                        "refused_total": 300,
                        "evidence": ["PA-5521", "EX-14 cosmetic dermatology"],
                    },
                },
            }],
        }),
        json.dumps({
            "type": "final",
            "final": {
                "decision": "approve_in_principle",
                "trigger": None,
                "missing": None,
                "escalate_to": None,
                "line_dispositions": [
                    {"procedure_code": "47120", "disposition": "approved", "amount": 1400},
                    {"procedure_code": "62480", "disposition": "approved", "amount": 780,
                     "preauthorisation_id": "PA-5521"},
                    {"procedure_code": "31255", "disposition": "refused", "amount": 300,
                     "reason": "EX-14 cosmetic dermatology"},
                ],
                "approved_total": 2180,
                "refused_total": 300,
                "evidence": ["PA-5521", "EX-14 cosmetic dermatology"],
            },
        }),
    ]
}
