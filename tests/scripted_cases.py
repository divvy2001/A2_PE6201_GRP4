"""
Scripted backend demonstration: Complete agent run for CLM-8842

This script simulates a complete agent loop run using a scripted backend that
mimics what a real LLM would return. It processes claim CLM-8842 (the worked
example from the assignment) and walks through the expected decision path.

CLM-8842 Decision Path:
- Member M-2214 (Tan Wei Ling) has policy POL-3310 (Shield Plus)
- 3 lines: 47120 ($1400), 62480 ($780), 31255 ($300)
- Line 47120: appendicectomy, no preauth required, approved
- Line 62480: spinal fusion, preauth required, PA-5521 valid and applies
- Line 31255: cosmetic dermabrasion, excluded under EX-14, refused
- Result: approve_in_principle with 2 approved lines, 1 refused
- Expected: approved_total=2180, refused_total=300
"""

import json
import sys
from pathlib import Path

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.loop import run_agent
from src.schemas import GuardConfig, ModelResponse
from src.tools.problem_a import TOOLS


class ScriptedBackendCLM8842:
    """Deterministic scripted responses for the CLM-8842 worked example."""

    name = "scripted-clm8842"

    def __init__(self):
        self.turn = 0
        self.responses = [
            # Turn 1: Read the claim.
            {
                "type": "action_block",
                "reasoning_summary": "Read the claim to identify the member, hospital, date, and claim lines.",
                "actions": [
                    {
                        "call_id": "t01-c01",
                        "tool": "get_claim",
                        "args": {"case_id": "CLM-8842"},
                    }
                ],
            },

            # Turn 2: Independent reads after get_claim.
            {
                "type": "action_block",
                "reasoning_summary": "Check the policy, coverage for all claim lines, and hospital status in parallel.",
                "actions": [
                    {
                        "call_id": "t02-c01",
                        "tool": "lookup_policy",
                        "args": {"policy_id": "POL-3310"},
                    },
                    {
                        "call_id": "t02-c02",
                        "tool": "check_coverage",
                        "args": {"procedure_code": "47120"},
                    },
                    {
                        "call_id": "t02-c03",
                        "tool": "check_coverage",
                        "args": {"procedure_code": "62480"},
                    },
                    {
                        "call_id": "t02-c04",
                        "tool": "check_coverage",
                        "args": {"procedure_code": "31255"},
                    },
                    {
                        "call_id": "t02-c05",
                        "tool": "get_hospital_status",
                        "args": {"hospital_id": "H-114"},
                    },
                ],
            },

            # Turn 3: Preauthorisation depends on the coverage result for 62480.
            {
                "type": "action_block",
                "reasoning_summary": "62480 requires preauthorisation, so retrieve the applicable preauthorisation before deciding.",
                "actions": [
                    {
                        "call_id": "t03-c01",
                        "tool": "get_preauthorisation",
                        "args": {
                            "member_id": "M-2214",
                            "procedure_code": "62480",
                            "date_of_service": "2026-09-02",
                        },
                    }
                ],
            },

            # Turn 4: Final recorded decision.
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
                            "description": "Laparoscopic appendicectomy",
                            "amount": 1400,
                            "status": "approved",
                        },
                        {
                            "code": "62480",
                            "description": "Lumbar spinal fusion",
                            "amount": 780,
                            "status": "approved",
                            "preauth_id": "PA-5521",
                        },
                        {
                            "code": "31255",
                            "description": "Cosmetic dermabrasion",
                            "amount": 300,
                            "status": "refused",
                            "reason": "EX-14 cosmetic dermatology",
                        },
                    ],
                    "approved_total": 2180,
                    "refused_total": 300,
                    "evidence": [
                        "CLM-8842",
                        "M-2214 policy POL-3310 active",
                        "H-114 is panel hospital",
                        "PA-5521 valid 2026-08-01 to 2026-10-31 covers 62480",
                        "31255 excluded under EX-14",
                    ],
                },
            },
        ]

    def generate(self, messages, *, model, temperature=0.0):
        """Return the next deterministic scripted response."""
        if self.turn >= len(self.responses):
            raise RuntimeError("SCRIPTED_BACKEND_EXHAUSTED: no response remaining")
        response_data = self.responses[self.turn]
        self.turn += 1
        return ModelResponse(
            text=json.dumps(response_data),
            tokens_in=150,
            tokens_out=100,
            model=model,
            latency_ms=50.0,
            cost_usd=0.002,
        )


def main():
    """Run the complete agent loop for CLM-8842."""
    
    print("=" * 80)
    print("SCRIPTED AGENT RUN: CLM-8842 (Worked Example)")
    print("=" * 80)
    print()
    
    # Load reference data
    ref_data_dir = Path(__file__).parent.parent / "reference_data" / "data_A"
    with open(ref_data_dir / "claims.json") as f:
        claims = {c["claim_id"]: c for c in json.load(f)}
    with open(ref_data_dir / "expected_outcomes_A.json") as f:
        outcomes = {o["case_id"]: o for o in json.load(f)}
    
    claim = claims["CLM-8842"]
    expected = outcomes["CLM-8842"]
    
    print("CLAIM DETAILS:")
    print(f"  Claim ID:       {claim['claim_id']}")
    print(f"  Member:         {claim['member_id']}")
    print(f"  Hospital:       {claim['hospital_id']}")
    print(f"  Date of Service: {claim['date_of_service']}")
    print(f"  Lines:          {len(claim['lines'])} procedures")
    for line in claim["lines"]:
        print(f"    - {line['code']}: ${line['amount']}")
    print()
    
    print("EXPECTED OUTCOME:")
    print(f"  Decision:       {expected['expected_decision']}")
    print(f"  Family:         {expected['family']}")
    print(f"  Must Record:")
    for item in expected["must_record"]:
        print(f"    - {item}")
    print()
    
    print("-" * 80)
    print("RUNNING AGENT...")
    print("-" * 80)
    print()
    
    # Run the agent with scripted backend
    backend = ScriptedBackendCLM8842()
    result = run_agent(
        "CLM-8842",
        backend=backend,
        model="scripted-demo",
        parallel_tools=True,
        autonomy="confirm",
        max_steps=10,
        budget_usd=0.10,
        guard_config=GuardConfig(),
        tool_registry=TOOLS,
        prompt_version="v2",
        trial=1,
    )
    
    print("RUN RESULT:")
    print(f"  Status:         {result.status}")
    print(f"  Turns:          {result.turns}")
    print(f"  Tool Calls:     {result.tool_calls}")
    print(f"  Mode:           {result.mode}")
    print()
    
    if result.error:
        print(f"  ERROR: {result.error['code']} - {result.error['message']}")
    
    if result.final:
        print("FINAL DECISION:")
        final = result.final
        print(f"  Decision:       {final.decision}")
        print(f"  Approved Total: ${final.approved_total}")
        print(f"  Refused Total:  ${final.refused_total}")
        print(f"  Line Dispositions:")
        for line in final.line_dispositions:
            status_str = f"{line.get('status', 'unknown')}"
            if 'preauth_id' in line:
                status_str += f" (preauth: {line['preauth_id']})"
            if 'reason' in line:
                status_str += f" - {line['reason']}"
            print(f"    {line['code']}: ${line['amount']} - {status_str}")
        print(f"  Evidence ({len(final.evidence)} items):")
        for item in final.evidence:
            print(f"    - {item}")
    
    print()
    print("-" * 80)
    print("TOOL TRACE (Summary):")
    print("-" * 80)
    for i, tool_call in enumerate(result.tool_trace, 1):
        action = tool_call["action"]
        observation = tool_call["observation"]
        status = "✓" if observation["ok"] else "✗"
        print(f"{i}. [{status}] {action['tool']} (call_id: {action['call_id']})")
        if not observation["ok"] and observation["error"]:
            print(f"   Error: {observation['error']['code']} - {observation['error']['message']}")
    
    print()
    print("-" * 80)
    print("FULL TRACE JSON:")
    print("-" * 80)
    trace_data = result.to_dict()
    # Pretty print selected fields
    print(json.dumps({
        "status": trace_data["status"],
        "turns": trace_data["turns"],
        "tool_calls": trace_data["tool_calls"],
        "cost_usd": trace_data["cost_usd"],
        "final": trace_data["final"],
        "error": trace_data["error"],
    }, indent=2))
    
    print()
    print("=" * 80)
    print("VALIDATION AGAINST EXPECTED OUTCOME:")
    print("=" * 80)
    
    if result.final:
        decision_match = result.final.decision == expected["expected_decision"]
        print(f"Decision matches: {decision_match} ({result.final.decision} == {expected['expected_decision']})")
        
        if result.final.decision == "approve_in_principle":
            approved_match = result.final.approved_total == 2180
            refused_match = result.final.refused_total == 300
            print(f"Approved total matches: {approved_match} (${result.final.approved_total} == $2180)")
            print(f"Refused total matches: {refused_match} (${result.final.refused_total} == $300)")
            
            # Check key evidence
            evidence_items = set(result.final.evidence)
            required_evidence = {
                "CLM-8842",
                "M-2214 policy POL-3310 active",
                "H-114 is panel hospital",
                "PA-5521 valid 2026-08-01 to 2026-10-31 covers 62480",
                "31255 excluded under EX-14"
            }
            evidence_subset = required_evidence.issubset(evidence_items)
            print(f"Contains required evidence: {evidence_subset}")
            
            if decision_match and approved_match and refused_match and evidence_subset:
                print()
                print("✓ ALL CHECKS PASSED - CLM-8842 handled correctly!")
            else:
                print()
                print("✗ SOME CHECKS FAILED - Review the output above")
    
    print()


if __name__ == "__main__":
    main()
