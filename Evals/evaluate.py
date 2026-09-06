"""Single entry point for Problem A evaluation.

The evaluator keeps the evaluation logic independent of the model provider.
Only these configuration values need to change for normal runs:

    BACKEND = "scripted" | "live"
    PROMPT_VERSION = "v2" | "v1"
    MODEL = "scripted" | an OpenRouter model id
    AUTONOMY = "act" | "confirm" | "suggest"

The command line can override any of them without editing this file.
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Callable

from src.agent.loop import run_agent
from src.agent.prompt_loader import load_prompt
from src.backends.base import ModelBackend
from src.backends.scripted import ScriptedBackend
from src.schemas import GuardConfig, RunResult
from src.tools.base import ToolHandler
from src.tools.versioned import get_versioned_tool_registry

from Evals.checks import evaluate_result
from Evals.judgement import judge_must_record


# =====================================================================
# SIMPLE RUN CONFIGURATION
# =====================================================================

BACKEND = "scripted"          # "scripted" or "live"
PROMPT_VERSION = "v2"         # "v1" or "v2"
MODEL = "scripted"            # OpenRouter model id when BACKEND="live"
AUTONOMY = "act"              # "suggest", "confirm", or "act"

MAX_STEPS = 12
BUDGET_USD = 1.0
PARALLEL_TOOLS = True
TEMPERATURE = 0.0

# L2 is optional from the CLI. If a case has must_record requirements and no
# judge model/backend is supplied, that L2 check is explicitly marked not_run.
JUDGE_MODEL: str | None = None

DEFAULT_ANSWER_KEY = (
    Path(__file__).resolve().parent.parent
    / "reference_data"
    / "expected_outcomes_A.json"
)
DEFAULT_RESULTS = Path(__file__).resolve().parent / "results.json"


# =====================================================================
# NEGATIVE CASES
# =====================================================================

NEGATIVE_FAMILIES = {
    "preauth_absent",
    "preauth_expired",
    "policy_lapsed",
    "outside_policy_dates",
    "annual_limit_exceeded",
    "duplicate_of_decided_claim",
    "prompt_injection_overt",
    "prompt_injection_imitating_tool_output",
}


# =====================================================================
# DETERMINISTIC SMOKE-TEST TRAJECTORY
# =====================================================================

# The scripted backend is intentionally built into this one entry point.
# More case trajectories can be added here as the scripted cases are finalized.
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


# =====================================================================
# ANSWER KEY
# =====================================================================

def load_answer_key(path: Path = DEFAULT_ANSWER_KEY) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Answer key must contain a JSON list.")

    cases: list[dict[str, Any]] = []
    valid_decisions = {"approve_in_principle", "request_document", "escalate"}

    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Every answer-key entry must be an object.")

        case_id = item.get("case_id")
        expected_decision = item.get("expected_decision")
        if not case_id:
            raise ValueError("Answer-key entry is missing case_id.")
        if expected_decision not in valid_decisions:
            raise ValueError(f"{case_id}: invalid expected_decision {expected_decision!r}")

        family = item.get("family")
        cases.append({
            "case_id": case_id,
            "expected": item,
            "negative": family in NEGATIVE_FAMILIES,
            "family": family,
        })

    return cases


def trial_count(case: dict[str, Any]) -> int:
    return 3 if case["negative"] else 1


# =====================================================================
# BACKENDS
# =====================================================================

BackendFactory = Callable[[], ModelBackend]


def make_backend_factory(
    case_id: str,
    *,
    backend: str,
    model: str,
) -> BackendFactory:
    """Create a fresh backend for each trial."""

    if backend == "scripted":
        if case_id not in SCRIPTED_CASES:
            available = ", ".join(sorted(SCRIPTED_CASES))
            raise ValueError(
                f"No scripted trajectory is defined for {case_id}. "
                f"Available scripted cases: {available}"
            )

        responses = list(SCRIPTED_CASES[case_id])
        return lambda: ScriptedBackend(responses)

    if backend == "live":
        if not os.getenv("OPENROUTER_API_KEY"):
            raise ValueError(
                "OPENROUTER_API_KEY is not set. "
                "Set it in the environment before using --backend live."
            )
        from src.backends.live import LiveBackend
        return lambda: LiveBackend()

    raise ValueError("backend must be 'scripted' or 'live'")


# =====================================================================
# ONE CASE
# =====================================================================

def run_case(
    case: dict[str, Any],
    *,
    model: str,
    backend_factory: BackendFactory,
    judge_backend_factory: BackendFactory | None = None,
    judge_model: str | None = None,
    parallel_tools: bool = PARALLEL_TOOLS,
    autonomy: str = AUTONOMY,
    max_steps: int = MAX_STEPS,
    budget_usd: float = BUDGET_USD,
    prompt_version: str = PROMPT_VERSION,
    temperature: float = TEMPERATURE,
) -> dict[str, Any]:
    case_id = case["case_id"]
    expected = case["expected"]
    system_prompt = load_prompt(prompt_version)
    tool_registry = get_versioned_tool_registry(prompt_version)
    guard_config = GuardConfig()

    trials: list[dict[str, Any]] = []
    total_in = total_out = 0
    total_cost = total_latency = 0.0

    for trial in range(1, trial_count(case) + 1):
        result: RunResult = run_agent(
            case_id,
            backend=backend_factory(),
            model=model,
            parallel_tools=parallel_tools,
            autonomy=autonomy,
            max_steps=max_steps,
            budget_usd=budget_usd,
            guard_config=guard_config,
            tool_registry=tool_registry,
            prompt_version=prompt_version,
            trial=trial,
            system_prompt=system_prompt,
            temperature=temperature,
        )

        l1 = evaluate_result(result, expected)
        l1_passed = bool(l1["code_passed"])

        judgement: dict[str, Any] | None = None
        if expected.get("must_record"):
            if judge_model is None or judge_backend_factory is None:
                judgement = {
                    "status": "not_run",
                    "passed": False,
                    "reason": "must_record is required but no judge model/backend was supplied.",
                }
            elif result.final is None:
                judgement = {
                    "status": "not_run",
                    "passed": False,
                    "reason": "No final decision was produced for L2 judgement.",
                }
            else:
                judgement = judge_must_record(
                    case_id=case_id,
                    requirements=expected["must_record"],
                    final_decision=result.final,
                    backend=judge_backend_factory(),
                    model=judge_model,
                )

        l2_passed = None if not expected.get("must_record") else bool(judgement and judgement.get("passed"))
        passed = l1_passed if l2_passed is None else l1_passed and l2_passed

        total_in += result.tokens_in
        total_out += result.tokens_out
        total_cost += result.cost_usd
        total_latency += result.latency_ms or 0.0

        trials.append({
            "trial": trial,
            "passed": passed,
            "code_passed": l1_passed,
            "judgement_passed": l2_passed,
            "result": result.to_dict(),
            "checks": l1,
            "judgement": judgement,
        })

    return {
        "case_id": case_id,
        "negative": case["negative"],
        "family": case["family"],
        "expected": expected,
        "trials": trials,
        "passed": all(t["passed"] for t in trials),
        "num_trials": len(trials),
        "tokens_in": total_in,
        "tokens_out": total_out,
        "cost_usd": total_cost,
        "latency_ms": total_latency,
    }


# =====================================================================
# FULL EVALUATION
# =====================================================================

def run_evaluation(
    *,
    cases: list[dict[str, Any]],
    model: str,
    backend_factory_for_case: Callable[[str], BackendFactory],
    judge_backend_factory: BackendFactory | None = None,
    judge_model: str | None = None,
    parallel_tools: bool = PARALLEL_TOOLS,
    autonomy: str = AUTONOMY,
    max_steps: int = MAX_STEPS,
    budget_usd: float = BUDGET_USD,
    prompt_version: str = PROMPT_VERSION,
    temperature: float = TEMPERATURE,
) -> dict[str, Any]:
    results = []

    for case in cases:
        results.append(run_case(
            case,
            model=model,
            backend_factory=backend_factory_for_case(case["case_id"]),
            judge_backend_factory=judge_backend_factory,
            judge_model=judge_model,
            parallel_tools=parallel_tools,
            autonomy=autonomy,
            max_steps=max_steps,
            budget_usd=budget_usd,
            prompt_version=prompt_version,
            temperature=temperature,
        ))

    ordinary = [r for r in results if not r["negative"]]
    negative = [r for r in results if r["negative"]]
    passed = sum(r["passed"] for r in results)

    summary = {
        "total_cases": len(results),
        "passed_cases": passed,
        "case_pass_rate": passed / len(results) if results else 0.0,
        "ordinary_cases": len(ordinary),
        "ordinary_passed": sum(r["passed"] for r in ordinary),
        "ordinary_pass_rate": sum(r["passed"] for r in ordinary) / len(ordinary) if ordinary else 0.0,
        "negative_cases": len(negative),
        "negative_passed": sum(r["passed"] for r in negative),
        "negative_pass_rate": sum(r["passed"] for r in negative) / len(negative) if negative else 0.0,
        "total_trials": sum(r["num_trials"] for r in results),
        "tokens_in": sum(r["tokens_in"] for r in results),
        "tokens_out": sum(r["tokens_out"] for r in results),
        "cost_usd": sum(r["cost_usd"] for r in results),
        "latency_ms": sum(r["latency_ms"] for r in results),
    }

    return {
        "backend": BACKEND,
        "model": model,
        "prompt_version": prompt_version,
        "autonomy": autonomy,
        "parallel_tools": parallel_tools,
        "summary": summary,
        "results": results,
    }


# =====================================================================
# OUTPUT
# =====================================================================

def save_results(evaluation: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evaluation, indent=2, ensure_ascii=False), encoding="utf-8")


def print_summary(evaluation: dict[str, Any]) -> None:
    s = evaluation["summary"]
    print("\n" + "=" * 60)
    print("Problem A Evaluation")
    print("=" * 60)
    print(f"Backend:        {evaluation['backend']}")
    print(f"Model:          {evaluation['model']}")
    print(f"Prompt:         {evaluation['prompt_version']}")
    print(f"Parallel:       {evaluation['parallel_tools']}")
    print(f"Cases:          {s['total_cases']}")
    print(f"Trials:         {s['total_trials']}")
    print(f"Overall:        {s['passed_cases']}/{s['total_cases']} ({s['case_pass_rate']:.1%})")
    print(f"Ordinary:       {s['ordinary_passed']}/{s['ordinary_cases']} ({s['ordinary_pass_rate']:.1%})")
    print(f"Negative:       {s['negative_passed']}/{s['negative_cases']} ({s['negative_pass_rate']:.1%})")
    print(f"Tokens in:      {s['tokens_in']}")
    print(f"Tokens out:     {s['tokens_out']}")
    print(f"Cost:           ${s['cost_usd']:.6f}")
    print(f"Latency:        {s['latency_ms']:.2f} ms")
    print("=" * 60)

    for case in evaluation["results"]:
        status = "PASS" if case["passed"] else "FAIL"
        print(f"{status}  {case['case_id']}  ({case['num_trials']} trial(s))")


# =====================================================================
# CLI
# =====================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Problem A evaluation harness.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("case_id", nargs="?", help="Run one case, e.g. CLM-8842")
    group.add_argument("--all", action="store_true", help="Run every case in the answer key")

    parser.add_argument("--backend", choices=("scripted", "live"), default=BACKEND)
    parser.add_argument("--prompt-version", choices=("v1", "v2"), default=PROMPT_VERSION)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--autonomy", choices=("suggest", "confirm", "act"), default=AUTONOMY)
    parser.add_argument("--sequential", action="store_true", help="Run independent tool calls sequentially")
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS)
    parser.add_argument("--budget-usd", type=float, default=BUDGET_USD)
    parser.add_argument("--judge-model", default=JUDGE_MODEL)
    parser.add_argument("--answer-key", type=Path, default=DEFAULT_ANSWER_KEY)
    parser.add_argument("--output", type=Path, default=DEFAULT_RESULTS)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    cases = load_answer_key(args.answer_key)

    if args.all:
        selected = cases
    else:
        selected = [c for c in cases if c["case_id"] == args.case_id]
        if not selected:
            raise SystemExit(f"Unknown case: {args.case_id}")

    def backend_factory_for_case(case_id: str) -> BackendFactory:
        return make_backend_factory(case_id, backend=args.backend, model=args.model)

    # The judge is deliberately a separate backend/model from the graded model.
    judge_factory = None
    if args.judge_model:
        if args.backend != "live":
            raise SystemExit("--judge-model currently requires --backend live.")
        from src.backends.live import LiveBackend
        judge_factory = lambda: LiveBackend()

    evaluation = run_evaluation(
        cases=selected,
        model=args.model,
        backend_factory_for_case=backend_factory_for_case,
        judge_backend_factory=judge_factory,
        judge_model=args.judge_model,
        parallel_tools=not args.sequential,
        autonomy=args.autonomy,
        max_steps=args.max_steps,
        budget_usd=args.budget_usd,
        prompt_version=args.prompt_version,
        temperature=TEMPERATURE,
    )

    save_results(evaluation, args.output)
    print_summary(evaluation)


if __name__ == "__main__":
    main()
