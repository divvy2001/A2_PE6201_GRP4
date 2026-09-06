"""
Evaluation runner for Problem A.

Responsibilities:
- Load the evaluation answer key.
- Determine whether a case is ordinary or negative.
- Run ordinary cases once and negative cases three times.
- Create a fresh backend for every trial.
- Run deterministic L1 checks.
- Run optional L2 judgement checks for `must_record`.
- Aggregate evaluation metrics.
- Save results to JSON.

The agent loop itself remains in src/agent/loop.py.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from src.agent.loop import run_agent
from src.agent.prompt_loader import load_prompt
from src.backends.base import ModelBackend
from src.schemas import RunResult

from Evals.checks import evaluate_result
from Evals.judgement import judge_must_record


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

DEFAULT_ANSWER_KEY = (
    Path(__file__).resolve().parent.parent
    / "reference_data"
    / "expected_outcomes_A.json"
)


# ---------------------------------------------------------------------
# Negative-case families
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------
# Answer-key loading
# ---------------------------------------------------------------------

def load_answer_key(
    path: Path = DEFAULT_ANSWER_KEY,
) -> list[dict[str, Any]]:
    """
    Load and normalize the evaluation answer key.

    Each returned case has:

        {
            "case_id": ...,
            "expected": {...},
            "negative": True/False,
            "family": ...
        }
    """

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Answer key must contain a JSON list.")

    cases: list[dict[str, Any]] = []

    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Every answer-key entry must be an object.")

        case_id = item.get("case_id")

        if not case_id:
            raise ValueError("Answer-key entry is missing case_id.")

        expected_decision = item.get("expected_decision")

        if expected_decision not in {
            "approve_in_principle",
            "request_document",
            "escalate",
        }:
            raise ValueError(
                f"{case_id}: invalid expected_decision "
                f"{expected_decision!r}"
            )

        family = item.get("family")

        cases.append(
            {
                "case_id": case_id,
                "expected": item,
                "negative": family in NEGATIVE_FAMILIES,
                "family": family,
            }
        )

    return cases


# ---------------------------------------------------------------------
# Trial count
# ---------------------------------------------------------------------

def trial_count(case: dict[str, Any]) -> int:
    """
    Return the required number of trials for an evaluation case.

    Ordinary case:
        1 trial

    Negative case:
        3 trials
    """

    return 3 if case["negative"] else 1


# ---------------------------------------------------------------------
# Backend creation
# ---------------------------------------------------------------------

BackendFactory = Callable[[], ModelBackend]


def _get_backend(
    *,
    backend: ModelBackend | None,
    backend_factory: BackendFactory | None,
) -> ModelBackend:
    """
    Create the backend for one individual trial.

    Preferred approach:
        backend_factory()

    This guarantees that every trial gets a fresh backend instance.

    A backend instance is still accepted for compatibility with existing
    code, but it will be reused if no factory is supplied.
    """

    if backend_factory is not None:
        return backend_factory()

    if backend is None:
        raise ValueError(
            "Provide either backend or backend_factory."
        )

    return backend


# ---------------------------------------------------------------------
# Single-case evaluation
# ---------------------------------------------------------------------

def run_case(
    case: dict[str, Any],
    *,
    model: str,
    backend: ModelBackend | None = None,
    backend_factory: BackendFactory | None = None,
    judge_backend: ModelBackend | None = None,
    judge_backend_factory: BackendFactory | None = None,
    judge_model: str | None = None,
    parallel_tools: bool = True,
    autonomy: str = "suggest",
    max_steps: int = 12,
    budget_usd: float = 1.0,
    guard_config: dict[str, Any] | None = None,
    tool_registry: dict[str, Any] | None = None,
    prompt_version: str = "v2",
    system_prompt: str | None = None,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """
    Run one evaluation case.

    Negative cases are run three times.
    Ordinary cases are run once.

    A fresh backend is created for every trial when `backend_factory`
    is provided.
    """

    case_id = case["case_id"]
    expected = case["expected"]

    # Load the requested prompt version once.
    if system_prompt is None:
        system_prompt = load_prompt(prompt_version)

    num_trials = trial_count(case)

    trial_results: list[dict[str, Any]] = []

    total_tokens_in = 0
    total_tokens_out = 0
    total_cost_usd = 0.0
    total_latency_ms = 0.0

    for trial in range(1, num_trials + 1):

        # -------------------------------------------------------------
        # Fresh backend for every trial
        # -------------------------------------------------------------

        trial_backend = _get_backend(
            backend=backend,
            backend_factory=backend_factory,
        )

        # -------------------------------------------------------------
        # Run the agent
        # -------------------------------------------------------------

        result: RunResult = run_agent(
            case_id,
            backend=trial_backend,
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

        # -------------------------------------------------------------
        # L1 deterministic checks
        # -------------------------------------------------------------

        l1 = evaluate_result(
            result,
            expected,
        )

        # -------------------------------------------------------------
        # L2 judgement check
        # -------------------------------------------------------------

        judgement = None

        if expected.get("must_record"):

            if judge_model is None:
                judgement = {
                    "status": "not_run",
                    "passed": False,
                    "reason": (
                        "must_record is required but no judge_model "
                        "was supplied."
                    ),
                }

            else:
                trial_judge_backend = None

                if judge_backend_factory is not None:
                    trial_judge_backend = judge_backend_factory()
                elif judge_backend is not None:
                    trial_judge_backend = judge_backend

                if trial_judge_backend is None:
                    judgement = {
                        "status": "not_run",
                        "passed": False,
                        "reason": (
                            "must_record is required but no "
                            "judge_backend was supplied."
                        ),
                    }

                else:
                    judgement = judge_must_record(
                        result=result,
                        expected=expected,
                        judge_backend=trial_judge_backend,
                        judge_model=judge_model,
                    )

        # -------------------------------------------------------------
        # Combine L1 + L2
        # -------------------------------------------------------------

        l1_passed = bool(l1["code_passed"])

        judgement_required = bool(
            expected.get("must_record")
        )

        if judgement_required:

            if judgement is None:
                l2_passed = False
            else:
                l2_passed = bool(
                    judgement.get("passed", False)
                )

            overall_passed = (
                l1_passed
                and l2_passed
            )

        else:
            l2_passed = None
            overall_passed = l1_passed

        # -------------------------------------------------------------
        # Metrics
        # -------------------------------------------------------------

        total_tokens_in += result.tokens_in
        total_tokens_out += result.tokens_out
        total_cost_usd += result.cost_usd
        total_latency_ms += result.latency_ms

        trial_results.append(
            {
                "trial": trial,
                "passed": overall_passed,
                "code_passed": l1_passed,
                "judgement_passed": l2_passed,
                "result": result.model_dump(),
                "checks": l1,
                "judgement": judgement,
            }
        )

    # -----------------------------------------------------------------
    # Case-level aggregation
    # -----------------------------------------------------------------

    case_passed = all(
        trial["passed"]
        for trial in trial_results
    )

    return {
        "case_id": case_id,
        "negative": case["negative"],
        "family": case["family"],
        "expected": expected,
        "trials": trial_results,
        "passed": case_passed,
        "num_trials": num_trials,
        "tokens_in": total_tokens_in,
        "tokens_out": total_tokens_out,
        "cost_usd": total_cost_usd,
        "latency_ms": total_latency_ms,
    }


# ---------------------------------------------------------------------
# Full evaluation
# ---------------------------------------------------------------------

def run_evaluation(
    *,
    cases: list[dict[str, Any]] | None = None,
    answer_key_path: Path = DEFAULT_ANSWER_KEY,
    model: str,
    backend: ModelBackend | None = None,
    backend_factory: BackendFactory | None = None,
    judge_backend: ModelBackend | None = None,
    judge_backend_factory: BackendFactory | None = None,
    judge_model: str | None = None,
    parallel_tools: bool = True,
    autonomy: str = "suggest",
    max_steps: int = 12,
    budget_usd: float = 1.0,
    guard_config: dict[str, Any] | None = None,
    tool_registry: dict[str, Any] | None = None,
    prompt_version: str = "v2",
    system_prompt: str | None = None,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """
    Run the complete evaluation set.

    If `cases` is not supplied, the answer key is loaded automatically.
    """

    if cases is None:
        cases = load_answer_key(answer_key_path)

    if system_prompt is None:
        system_prompt = load_prompt(prompt_version)

    case_results: list[dict[str, Any]] = []

    for case in cases:

        case_result = run_case(
            case,
            model=model,
            backend=backend,
            backend_factory=backend_factory,
            judge_backend=judge_backend,
            judge_backend_factory=judge_backend_factory,
            judge_model=judge_model,
            parallel_tools=parallel_tools,
            autonomy=autonomy,
            max_steps=max_steps,
            budget_usd=budget_usd,
            guard_config=guard_config,
            tool_registry=tool_registry,
            prompt_version=prompt_version,
            system_prompt=system_prompt,
            temperature=temperature,
        )

        case_results.append(case_result)

    # -----------------------------------------------------------------
    # Aggregate metrics
    # -----------------------------------------------------------------

    total_cases = len(case_results)

    passed_cases = sum(
        1
        for case in case_results
        if case["passed"]
    )

    negative_cases = [
        case
        for case in case_results
        if case["negative"]
    ]

    ordinary_cases = [
        case
        for case in case_results
        if not case["negative"]
    ]

    negative_passed = sum(
        1
        for case in negative_cases
        if case["passed"]
    )

    ordinary_passed = sum(
        1
        for case in ordinary_cases
        if case["passed"]
    )

    total_trials = sum(
        case["num_trials"]
        for case in case_results
    )

    total_tokens_in = sum(
        case["tokens_in"]
        for case in case_results
    )

    total_tokens_out = sum(
        case["tokens_out"]
        for case in case_results
    )

    total_cost_usd = sum(
        case["cost_usd"]
        for case in case_results
    )

    total_latency_ms = sum(
        case["latency_ms"]
        for case in case_results
    )

    return {
        "model": model,
        "prompt_version": prompt_version,
        "autonomy": autonomy,
        "parallel_tools": parallel_tools,

        "summary": {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "case_pass_rate": (
                passed_cases / total_cases
                if total_cases
                else 0.0
            ),

            "ordinary_cases": len(ordinary_cases),
            "ordinary_passed": ordinary_passed,
            "ordinary_pass_rate": (
                ordinary_passed / len(ordinary_cases)
                if ordinary_cases
                else 0.0
            ),

            "negative_cases": len(negative_cases),
            "negative_passed": negative_passed,
            "negative_pass_rate": (
                negative_passed / len(negative_cases)
                if negative_cases
                else 0.0
            ),

            "total_trials": total_trials,

            "tokens_in": total_tokens_in,
            "tokens_out": total_tokens_out,
            "cost_usd": total_cost_usd,
            "latency_ms": total_latency_ms,
        },

        "results": case_results,
    }


# ---------------------------------------------------------------------
# Save results
# ---------------------------------------------------------------------

def save_results(
    evaluation: dict[str, Any],
    path: Path,
) -> None:
    """Save evaluation results as formatted JSON."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open("w", encoding="utf-8") as f:
        json.dump(
            evaluation,
            f,
            indent=2,
            ensure_ascii=False,
        )


# ---------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------

def print_summary(
    evaluation: dict[str, Any],
) -> None:
    """Print a compact evaluation summary."""

    summary = evaluation["summary"]

    print()
    print("=" * 60)
    print("Evaluation Summary")
    print("=" * 60)

    print(f"Model:          {evaluation['model']}")
    print(f"Prompt:         {evaluation['prompt_version']}")
    print(f"Cases:          {summary['total_cases']}")
    print(f"Trials:         {summary['total_trials']}")

    print(
        f"Overall:        "
        f"{summary['passed_cases']}/{summary['total_cases']} "
        f"({summary['case_pass_rate']:.1%})"
    )

    print(
        f"Ordinary:       "
        f"{summary['ordinary_passed']}/"
        f"{summary['ordinary_cases']} "
        f"({summary['ordinary_pass_rate']:.1%})"
    )

    print(
        f"Negative:       "
        f"{summary['negative_passed']}/"
        f"{summary['negative_cases']} "
        f"({summary['negative_pass_rate']:.1%})"
    )

    print(f"Tokens in:      {summary['tokens_in']}")
    print(f"Tokens out:     {summary['tokens_out']}")
    print(f"Cost:           ${summary['cost_usd']:.6f}")
    print(f"Latency:        {summary['latency_ms']:.2f} ms")

    print("=" * 60)
