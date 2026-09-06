"""
Evaluation runner.

Pipeline:

    answer key
        ↓
    run_agent()
        ↓
    L1 deterministic checks
        +
    L2 must_record judgement
        ↓
    final PASS / FAIL
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from Evals.checks import evaluate_result
from Evals.judgement import judge_must_record

from src.agent.loop import run_agent
from src.agent.prompt_loader import load_prompt
from src.backends.base import ModelBackend
from src.schemas import GuardConfig


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DEFAULT_ANSWER_KEY = (
    Path(__file__).resolve().parent.parent
    / "reference_data"
    / "expected_outcomes_A.json"
)

# Families that receive 3 trials.
#
# These are the negative cases where the agent must correctly
# refuse to act / escalate rather than proceed.
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


# ---------------------------------------------------------
# Answer-key loading
# ---------------------------------------------------------

def load_answer_key(
    path: str | Path = DEFAULT_ANSWER_KEY,
) -> list[dict[str, Any]]:
    """
    Load and validate the labelled evaluation cases.

    The answer key uses fields such as:

        case_id
        expected_decision
        trigger
        missing
        family
        must_record

    The runner converts this directly into the case structure
    required by the evaluation loop.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Answer key not found: {path}"
        )

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            "Answer key must contain a JSON list."
        )

    cases: list[dict[str, Any]] = []

    for index, item in enumerate(data, start=1):

        if not isinstance(item, dict):
            raise ValueError(
                f"Answer-key entry {index} must be an object."
            )

        case_id = item.get("case_id")

        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(
                f"Answer-key entry {index} has invalid case_id."
            )

        if "expected_decision" not in item:
            raise ValueError(
                f"{case_id}: missing expected_decision."
            )

        family = item.get("family", "")

        # Create the runner's normalized representation.
        case = {
            "case_id": case_id,
            "expected": item,
            "negative": family in NEGATIVE_FAMILIES,
            "family": family,
        }

        cases.append(case)

    return cases


# ---------------------------------------------------------
# Trial count
# ---------------------------------------------------------

def trial_count(case: dict[str, Any]) -> int:
    """
    Return the number of trials required for a case.

    Ordinary case -> 1
    Negative case -> 3
    """

    return 3 if case.get("negative", False) else 1


# ---------------------------------------------------------
# Single case
# ---------------------------------------------------------

def run_case(
    case: dict[str, Any],
    *,
    backend: ModelBackend,
    model: str,
    judge_backend: ModelBackend | None = None,
    judge_model: str | None = None,
    parallel_tools: bool = True,
    autonomy: str = "confirm",
    max_steps: int = 8,
    budget_usd: float = 1.0,
    guard_config: GuardConfig | None = None,
    tool_registry: dict[str, Any] | None = None,
    prompt_version: str = "v2",
    system_prompt: str | None = None,
) -> dict[str, Any]:
    """
    Run all trials for one evaluation case.

    Each trial runs the actual agent and then applies:

        L1 deterministic checks
        L2 must_record judgement

    The LLM judge is optional for development, but should be
    supplied for the actual D4 evaluation.
    """

    case_id = case["case_id"]
    expected = case["expected"]

    number_of_trials = trial_count(case)

    prompt = (
        system_prompt
        if system_prompt is not None
        else load_prompt(prompt_version)
    )

    if guard_config is None:
        guard_config = GuardConfig()

    trials: list[dict[str, Any]] = []

    for trial in range(1, number_of_trials + 1):

        result = run_agent(
            case_id,
            backend=backend,
            model=model,
            parallel_tools=parallel_tools,
            autonomy=autonomy,
            max_steps=max_steps,
            budget_usd=budget_usd,
            guard_config=guard_config,
            tool_registry=tool_registry,
            prompt_version=prompt_version,
            trial=trial,
            system_prompt=prompt,
            temperature=0.0,
        )

        # -------------------------------------------------
        # L1 deterministic checks
        # -------------------------------------------------

        l1 = evaluate_result(
            result,
            expected,
        )

        # -------------------------------------------------
        # L2 judgement checks
        # -------------------------------------------------

        if expected.get("must_record"):

            if judge_backend is not None and judge_model is not None:

                if result.final is None:

                    l2 = {
                        "status": "not_run",
                        "passed": False,
                        "checks": [],
                        "error": (
                            "Cannot perform must_record judgement "
                            "because the agent produced no final decision."
                        ),
                        "judge_model": judge_model,
                    }

                else:

                    l2 = judge_must_record(
                        case_id=case_id,
                        requirements=expected["must_record"],
                        final_decision=result.final,
                        backend=judge_backend,
                        model=judge_model,
                    )

            else:

                l2 = {
                    "status": "not_run",
                    "passed": None,
                    "checks": [],
                    "judge_model": None,
                    "error": "No judge backend/model configured.",
                }

        else:

            l2 = {
                "status": "not_required",
                "passed": True,
                "checks": [],
                "judge_model": judge_model,
            }

        # -------------------------------------------------
        # Overall result
        # -------------------------------------------------

        if l2["status"] == "not_run":

            # During development we retain the L1 result,
            # but explicitly mark that the full evaluation
            # was not performed.
            overall_passed = l1["passed"]
            evaluation_complete = False

        else:

            overall_passed = (
                l1["passed"]
                and l2["passed"]
            )
            evaluation_complete = True

        trials.append(
            {
                "trial": trial,
                "passed": overall_passed,
                "evaluation_complete": evaluation_complete,

                # Keep both layers visible.
                "code_passed": l1["passed"],
                "judgement_passed": l2["passed"],

                "l1": l1,
                "l2": l2,

                # Run-level cost metrics needed by D5/D6.
                "status": result.status,
                "run_id": result.run_id,
                "tokens_in": result.tokens_in,
                "tokens_out": result.tokens_out,
                "cost_usd": result.cost_usd,
                "latency_ms": result.latency_ms,
                "turns": result.turns,
                "tool_calls": result.tool_calls,
                "caps_fired": result.caps_fired,
            }
        )

    # ---------------------------------------------------------
    # Case-level aggregation
    # ---------------------------------------------------------

    passed_trials = sum(
        1 for trial in trials
        if trial["passed"]
    )

    total_trials = len(trials)

    complete_trials = sum(
        1 for trial in trials
        if trial["evaluation_complete"]
    )

    total_tokens_in = sum(
        trial["tokens_in"]
        for trial in trials
    )

    total_tokens_out = sum(
        trial["tokens_out"]
        for trial in trials
    )

    total_cost = sum(
        trial["cost_usd"]
        for trial in trials
    )

    total_latency = sum(
        trial["latency_ms"]
        for trial in trials
    )

    return {
        "case_id": case_id,
        "family": case.get("family"),
        "negative": case.get("negative", False),

        "expected_decision": expected.get(
            "expected_decision"
        ),

        "trials": trials,

        "passed_trials": passed_trials,
        "total_trials": total_trials,

        "pass_rate": (
            passed_trials / total_trials
            if total_trials
            else 0.0
        ),

        "evaluation_complete": (
            complete_trials == total_trials
        ),

        "tokens_in": total_tokens_in,
        "tokens_out": total_tokens_out,
        "cost_usd": total_cost,
        "latency_ms": total_latency,
    }


# ---------------------------------------------------------
# Full evaluation set
# ---------------------------------------------------------

def run_evaluation(
    *,
    backend: ModelBackend,
    model: str,
    answer_key_path: str | Path = DEFAULT_ANSWER_KEY,
    judge_backend: ModelBackend | None = None,
    judge_model: str | None = None,
    parallel_tools: bool = True,
    autonomy: str = "confirm",
    max_steps: int = 8,
    budget_usd: float = 1.0,
    guard_config: GuardConfig | None = None,
    tool_registry: dict[str, Any] | None = None,
    prompt_version: str = "v2",
    system_prompt: str | None = None,
) -> dict[str, Any]:
    """
    Run the complete evaluation set.
    """

    cases = load_answer_key(answer_key_path)

    case_results: list[dict[str, Any]] = []

    for case in cases:

        result = run_case(
            case,
            backend=backend,
            model=model,
            judge_backend=judge_backend,
            judge_model=judge_model,
            parallel_tools=parallel_tools,
            autonomy=autonomy,
            max_steps=max_steps,
            budget_usd=budget_usd,
            guard_config=guard_config,
            tool_registry=tool_registry,
            prompt_version=prompt_version,
            system_prompt=system_prompt,
        )

        case_results.append(result)

    # ---------------------------------------------------------
    # Overall metrics
    # ---------------------------------------------------------

    total_trials = sum(
        item["total_trials"]
        for item in case_results
    )

    passed_trials = sum(
        item["passed_trials"]
        for item in case_results
    )

    negative_trials = sum(
        item["total_trials"]
        for item in case_results
        if item["negative"]
    )

    negative_passed = sum(
        item["passed_trials"]
        for item in case_results
        if item["negative"]
    )

    ordinary_trials = total_trials - negative_trials
    ordinary_passed = passed_trials - negative_passed

    total_tokens_in = sum(
        item["tokens_in"]
        for item in case_results
    )

    total_tokens_out = sum(
        item["tokens_out"]
        for item in case_results
    )

    total_cost = sum(
        item["cost_usd"]
        for item in case_results
    )

    total_latency = sum(
        item["latency_ms"]
        for item in case_results
    )

    return {
        "model": model,
        "judge_model": judge_model,
        "prompt_version": prompt_version,

        "cases": len(case_results),

        "total_trials": total_trials,
        "passed_trials": passed_trials,

        "pass_rate": (
            passed_trials / total_trials
            if total_trials
            else 0.0
        ),

        "ordinary": {
            "trials": ordinary_trials,
            "passed": ordinary_passed,
            "pass_rate": (
                ordinary_passed / ordinary_trials
                if ordinary_trials
                else 0.0
            ),
        },

        "negative": {
            "trials": negative_trials,
            "passed": negative_passed,
            "pass_rate": (
                negative_passed / negative_trials
                if negative_trials
                else 0.0
            ),
        },

        # Cost-ledger metrics.
        "tokens_in": total_tokens_in,
        "tokens_out": total_tokens_out,
        "cost_usd": total_cost,
        "latency_ms": total_latency,

        "results": case_results,
    }


# ---------------------------------------------------------
# JSON output
# ---------------------------------------------------------

def save_results(
    results: dict[str, Any],
    path: str | Path,
) -> None:
    """Save evaluation results as reproducible JSON."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
        )


# ---------------------------------------------------------
# Simple command-line summary
# ---------------------------------------------------------

def print_summary(results: dict[str, Any]) -> None:
    """Print a compact evaluation summary."""

    print()
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(f"Model:          {results['model']}")
    print(f"Judge:          {results['judge_model']}")
    print(f"Prompt:         {results['prompt_version']}")

    print()
    print(
        f"Overall:        "
        f"{results['passed_trials']}/"
        f"{results['total_trials']} "
        f"({results['pass_rate']:.1%})"
    )

    ordinary = results["ordinary"]
    negative = results["negative"]

    print(
        f"Ordinary:       "
        f"{ordinary['passed']}/"
        f"{ordinary['trials']} "
        f"({ordinary['pass_rate']:.1%})"
    )

    print(
        f"Negative:       "
        f"{negative['passed']}/"
        f"{negative['trials']} "
        f"({negative['pass_rate']:.1%})"
    )

    print()
    print(f"Input tokens:   {results['tokens_in']}")
    print(f"Output tokens:  {results['tokens_out']}")
    print(f"Cost (USD):     ${results['cost_usd']:.6f}")
    print(f"Latency (ms):   {results['latency_ms']:.2f}")

    print("=" * 60)


# ---------------------------------------------------------
# Optional CLI
# ---------------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Run the PE6201 evaluation harness."
    )

    parser.add_argument(
        "--answer-key",
        default=str(DEFAULT_ANSWER_KEY),
    )

    parser.add_argument(
        "--model",
        required=True,
    )

    parser.add_argument(
        "--prompt-version",
        default="v2",
        choices=["v1", "v2"],
    )

    parser.add_argument(
        "--output",
        default="evaluation_results.json",
    )

    args = parser.parse_args()

    raise SystemExit(
        "CLI execution requires the project-specific backend "
        "and tool registry to be instantiated. Use run_evaluation() "
        "from your notebook/runner."
    )
