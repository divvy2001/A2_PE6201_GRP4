"""
Single entry point for Problem A evaluation.

Usage from the repository root:

    python Evals/evaluate.py CLM-8842
    python Evals/evaluate.py --all
    python Evals/evaluate.py CLM-8842 --responses path/to/responses.json
    python Evals/evaluate.py --all --responses path/to/responses.json

The evaluator has one flow:

    answer key -> select case(s) -> run trial(s)
                -> deterministic checks
                -> optional L2 judgement
                -> aggregate -> print/save

The agent loop remains in src/agent/loop.py.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Callable

from src.agent.loop import run_agent
from src.agent.prompt_loader import load_prompt
from src.backends.base import ModelBackend
from src.backends.scripted import ScriptedBackend
from src.schemas import GuardConfig, RunResult
from src.tools.base import ToolHandler
from src.tools.problem_a import TOOLS
from src.tools.versioned import get_versioned_tool_registry

from Evals.checks import evaluate_result
from Evals.judgement import judge_must_record


# ---------------------------------------------------------------------
# Paths and defaults
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ANSWER_KEY = PROJECT_ROOT / "reference_data" / "expected_outcomes_A.json"
DEFAULT_RESULTS = PROJECT_ROOT / "Evals" / "results.json"

DEFAULT_MODEL = "scripted"
DEFAULT_PROMPT_VERSION = "v2"
DEFAULT_AUTONOMY = "act"
DEFAULT_MAX_STEPS = 12
DEFAULT_BUDGET_USD = 1.0


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
# Types
# ---------------------------------------------------------------------

BackendFactory = Callable[[], ModelBackend]


# ---------------------------------------------------------------------
# Answer-key loading
# ---------------------------------------------------------------------

def load_answer_key(
    path: Path = DEFAULT_ANSWER_KEY,
) -> list[dict[str, Any]]:
    """Load and normalize the Problem A evaluation answer key."""

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Answer key must contain a JSON list.")

    cases: list[dict[str, Any]] = []

    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Every answer-key entry must be an object.")

        case_id = item.get("case_id")
        if not case_id:
            raise ValueError("Answer-key entry is missing case_id.")

        decision = item.get("expected_decision")
        if decision not in {
            "approve_in_principle",
            "request_document",
            "escalate",
        }:
            raise ValueError(
                f"{case_id}: invalid expected_decision {decision!r}"
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
    """Ordinary cases run once; negative cases run three times."""

    return 3 if case["negative"] else 1


# ---------------------------------------------------------------------
# Scripted response loading
# ---------------------------------------------------------------------

def load_scripted_responses(path: Path) -> dict[str, list[str]]:
    """
    Load deterministic model responses.

    Expected JSON shape:

        {
          "CLM-8842": [
            "<model response for turn 1>",
            "<model response for turn 2>",
            ...
          ]
        }

    One response is consumed per model turn. A fresh ScriptedBackend is
    created for every trial, so every trial starts from response 1.
    """

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Scripted responses must be a JSON object.")

    result: dict[str, list[str]] = {}

    for case_id, responses in data.items():
        if not isinstance(case_id, str):
            raise ValueError("Scripted response case IDs must be strings.")

        if not isinstance(responses, list) or not all(
            isinstance(response, str) for response in responses
        ):
            raise ValueError(
                f"{case_id}: scripted responses must be a list of strings."
            )

        result[case_id] = responses

    return result


# ---------------------------------------------------------------------
# Backend helpers
# ---------------------------------------------------------------------

def _fresh_backend(
    *,
    backend: ModelBackend | None,
    backend_factory: BackendFactory | None,
) -> ModelBackend:
    """
    Return a backend for one trial.

    A factory is preferred because it guarantees a clean backend state.
    """

    if backend_factory is not None:
        return backend_factory()

    if backend is None:
        raise ValueError("Provide either backend or backend_factory.")

    # ScriptedBackend exposes fresh(), which is the correct behavior for
    # repeated trials. Other backends are assumed to be stateless.
    fresh = getattr(backend, "fresh", None)
    if callable(fresh):
        return fresh()

    return backend


def make_scripted_backend_factory(
    responses: Sequence[str],
) -> BackendFactory:
    """Create a factory that returns a fresh scripted backend per trial."""

    frozen_responses = list(responses)

    def factory() -> ModelBackend:
        return ScriptedBackend(frozen_responses)

    return factory


# ---------------------------------------------------------------------
# L1 + L2 evaluation
# ---------------------------------------------------------------------

def _run_judgement(
    *,
    result: RunResult,
    expected: dict[str, Any],
    judge_backend: ModelBackend | None,
    judge_model: str | None,
) -> dict[str, Any] | None:
    """Run L2 only when the answer key contains must_record requirements."""

    requirements = expected.get("must_record")
    if not requirements:
        return None

    if not isinstance(requirements, list):
        raise ValueError("must_record must be a list when supplied.")

    if judge_backend is None or not judge_model:
        return {
            "status": "not_run",
            "passed": False,
            "checks": [],
            "reason": (
                "must_record is required but no judge backend/model "
                "was supplied."
            ),
        }

    return judge_must_record(
        case_id=result.case_id,
        requirements=requirements,
        final_decision=result.final,
        backend=judge_backend,
        model=judge_model,
    )


def run_trial(
    case: dict[str, Any],
    *,
    trial: int,
    model: str,
    backend: ModelBackend,
    judge_backend: ModelBackend | None = None,
    judge_model: str | None = None,
    parallel_tools: bool = True,
    autonomy: str = DEFAULT_AUTONOMY,
    max_steps: int = DEFAULT_MAX_STEPS,
    budget_usd: float = DEFAULT_BUDGET_USD,
    guard_config: GuardConfig | None = None,
    tool_registry: Mapping[str, ToolHandler] | None = None,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    system_prompt: str | None = None,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """
    Run exactly one agent trial and evaluate it.

    This is the core evaluation unit:
        run_agent -> checks.py -> optional judgement.py
    """

    if system_prompt is None:
        system_prompt = load_prompt(prompt_version)

    if guard_config is None:
        guard_config = GuardConfig()

    versioned_tools = get_versioned_tool_registry(
        prompt_version,
        base_registry=tool_registry or TOOLS,
    )

    result = run_agent(
        case["case_id"],
        backend=backend,
        model=model,
        parallel_tools=parallel_tools,
        autonomy=autonomy,
        max_steps=max_steps,
        budget_usd=budget_usd,
        guard_config=guard_config,
        tool_registry=versioned_tools,
        prompt_version=prompt_version,
        trial=trial,
        system_prompt=system_prompt,
        temperature=temperature,
    )

    # L1: deterministic comparison against the answer key.
    code_checks = evaluate_result(
        result,
        case["expected"],
    )

    # L2: semantic judgement of must_record requirements.
    judgement = _run_judgement(
        result=result,
        expected=case["expected"],
        judge_backend=judge_backend,
        judge_model=judge_model,
    )

    code_passed = bool(code_checks["code_passed"])

    if case["expected"].get("must_record"):
        judgement_passed = bool(
            judgement is not None
            and judgement.get("passed", False)
        )
        overall_passed = code_passed and judgement_passed
    else:
        judgement_passed = None
        overall_passed = code_passed

    return {
        "trial": trial,
        "passed": overall_passed,
        "code_passed": code_passed,
        "judgement_passed": judgement_passed,
        "result": result.to_dict(),
        "checks": code_checks,
        "judgement": judgement,
    }


# ---------------------------------------------------------------------
# Case evaluation
# ---------------------------------------------------------------------

def run_case(
    case: dict[str, Any],
    *,
    model: str,
    backend_factory: BackendFactory,
    judge_backend_factory: BackendFactory | None = None,
    judge_model: str | None = None,
    parallel_tools: bool = True,
    autonomy: str = DEFAULT_AUTONOMY,
    max_steps: int = DEFAULT_MAX_STEPS,
    budget_usd: float = DEFAULT_BUDGET_USD,
    guard_config: GuardConfig | None = None,
    tool_registry: Mapping[str, ToolHandler] | None = None,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    system_prompt: str | None = None,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """Run one case for its required number of trials and aggregate it."""

    num_trials = trial_count(case)
    trials: list[dict[str, Any]] = []

    for trial in range(1, num_trials + 1):
        trial_backend = backend_factory()

        # The judge is also fresh for each trial when a factory is supplied.
        trial_judge_backend = (
            judge_backend_factory()
            if judge_backend_factory is not None
            else None
        )

        trial_result = run_trial(
            case,
            trial=trial,
            model=model,
            backend=trial_backend,
            judge_backend=trial_judge_backend,
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

        trials.append(trial_result)

    passed = all(trial["passed"] for trial in trials)

    return {
        "case_id": case["case_id"],
        "negative": case["negative"],
        "family": case["family"],
        "expected": case["expected"],
        "num_trials": num_trials,
        "passed": passed,
        "trials": trials,
    }


# ---------------------------------------------------------------------
# Full evaluation
# ---------------------------------------------------------------------

def run_evaluation(
    *,
    cases: list[dict[str, Any]],
    model: str,
    backend_factory_for_case: Callable[[str], BackendFactory],
    judge_backend_factory: BackendFactory | None = None,
    judge_model: str | None = None,
    parallel_tools: bool = True,
    autonomy: str = DEFAULT_AUTONOMY,
    max_steps: int = DEFAULT_MAX_STEPS,
    budget_usd: float = DEFAULT_BUDGET_USD,
    guard_config: GuardConfig | None = None,
    tool_registry: Mapping[str, ToolHandler] | None = None,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """
    Run the selected evaluation cases.

    The caller decides how a case gets its backend. This keeps the evaluator
    vendor-neutral and lets scripted and live runs use exactly the same
    evaluation/checking path.
    """

    case_results: list[dict[str, Any]] = []

    for case in cases:
        result = run_case(
            case,
            model=model,
            backend_factory=backend_factory_for_case(case["case_id"]),
            judge_backend_factory=judge_backend_factory,
            judge_model=judge_model,
            parallel_tools=parallel_tools,
            autonomy=autonomy,
            max_steps=max_steps,
            budget_usd=budget_usd,
            guard_config=guard_config,
            tool_registry=tool_registry,
            prompt_version=prompt_version,
            temperature=temperature,
        )
        case_results.append(result)

    ordinary = [case for case in case_results if not case["negative"]]
    negative = [case for case in case_results if case["negative"]]

    passed_cases = sum(case["passed"] for case in case_results)
    ordinary_passed = sum(case["passed"] for case in ordinary)
    negative_passed = sum(case["passed"] for case in negative)

    total_trials = sum(case["num_trials"] for case in case_results)

    # Metrics remain part of the result because D5 consumes them later.
    total_tokens_in = sum(
        trial["result"]["tokens_in"]
        for case in case_results
        for trial in case["trials"]
    )
    total_tokens_out = sum(
        trial["result"]["tokens_out"]
        for case in case_results
        for trial in case["trials"]
    )
    total_cost = sum(
        trial["result"]["cost_usd"]
        for case in case_results
        for trial in case["trials"]
    )
    total_latency = sum(
        trial["result"]["latency_ms"] or 0.0
        for case in case_results
        for trial in case["trials"]
    )

    return {
        "model": model,
        "prompt_version": prompt_version,
        "autonomy": autonomy,
        "parallel_tools": parallel_tools,
        "summary": {
            "total_cases": len(case_results),
            "passed_cases": passed_cases,
            "case_pass_rate": (
                passed_cases / len(case_results)
                if case_results
                else 0.0
            ),
            "ordinary_cases": len(ordinary),
            "ordinary_passed": ordinary_passed,
            "ordinary_pass_rate": (
                ordinary_passed / len(ordinary)
                if ordinary
                else 0.0
            ),
            "negative_cases": len(negative),
            "negative_passed": negative_passed,
            "negative_pass_rate": (
                negative_passed / len(negative)
                if negative
                else 0.0
            ),
            "total_trials": total_trials,
            "tokens_in": total_tokens_in,
            "tokens_out": total_tokens_out,
            "cost_usd": total_cost,
            "latency_ms": total_latency,
        },
        "results": case_results,
    }


# ---------------------------------------------------------------------
# Saving and display
# ---------------------------------------------------------------------

def save_results(
    evaluation: dict[str, Any],
    path: Path = DEFAULT_RESULTS,
) -> None:
    """Save the complete evaluation result as JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            evaluation,
            file,
            indent=2,
            ensure_ascii=False,
        )


def print_summary(evaluation: dict[str, Any]) -> None:
    """Print a compact human-readable summary."""

    summary = evaluation["summary"]

    print()
    print("=" * 64)
    print("Problem A Evaluation")
    print("=" * 64)
    print(f"Model:       {evaluation['model']}")
    print(f"Prompt:      {evaluation['prompt_version']}")
    print(f"Parallel:    {evaluation['parallel_tools']}")
    print(f"Autonomy:    {evaluation['autonomy']}")
    print()
    print(
        f"Overall:     {summary['passed_cases']}/"
        f"{summary['total_cases']} "
        f"({summary['case_pass_rate']:.1%})"
    )
    print(
        f"Ordinary:    {summary['ordinary_passed']}/"
        f"{summary['ordinary_cases']} "
        f"({summary['ordinary_pass_rate']:.1%})"
    )
    print(
        f"Negative:    {summary['negative_passed']}/"
        f"{summary['negative_cases']} "
        f"({summary['negative_pass_rate']:.1%})"
    )
    print(f"Trials:      {summary['total_trials']}")
    print(f"Tokens in:   {summary['tokens_in']}")
    print(f"Tokens out:  {summary['tokens_out']}")
    print(f"Cost:        ${summary['cost_usd']:.6f}")
    print(f"Latency:     {summary['latency_ms']:.2f} ms")
    print()

    for case in evaluation["results"]:
        status = "PASS" if case["passed"] else "FAIL"
        print(
            f"{status:<5} {case['case_id']:<12} "
            f"trials={case['num_trials']}"
        )

    print("=" * 64)


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the Problem A evaluation harness."
    )

    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "case_id",
        nargs="?",
        help="Run one case, e.g. CLM-8842.",
    )
    selection.add_argument(
        "--all",
        action="store_true",
        help="Run every case in the answer key.",
    )

    parser.add_argument(
        "--answer-key",
        type=Path,
        default=DEFAULT_ANSWER_KEY,
        help="Path to expected_outcomes_A.json.",
    )
    parser.add_argument(
        "--responses",
        type=Path,
        required=True,
        help=(
            "JSON file containing scripted model responses keyed by case_id."
        ),
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Model label recorded in the evaluation.",
    )
    parser.add_argument(
        "--prompt-version",
        choices=("v1", "v2"),
        default=DEFAULT_PROMPT_VERSION,
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Execute independent tool calls sequentially instead of in parallel.",
    )
    parser.add_argument(
        "--autonomy",
        choices=("suggest", "confirm", "act"),
        default=DEFAULT_AUTONOMY,
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=DEFAULT_MAX_STEPS,
    )
    parser.add_argument(
        "--budget-usd",
        type=float,
        default=DEFAULT_BUDGET_USD,
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Optional L2 judge model. Requires a live judge backend in code.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RESULTS,
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    all_cases = load_answer_key(args.answer_key)

    if args.all:
        cases = all_cases
    else:
        cases = [
            case
            for case in all_cases
            if case["case_id"] == args.case_id
        ]

        if not cases:
            available = ", ".join(case["case_id"] for case in all_cases)
            raise SystemExit(
                f"Unknown case {args.case_id!r}. Available cases: {available}"
            )

    scripted_responses = load_scripted_responses(args.responses)

    missing = [
        case["case_id"]
        for case in cases
        if case["case_id"] not in scripted_responses
    ]

    if missing:
        raise SystemExit(
            "No scripted responses supplied for: "
            + ", ".join(missing)
        )

    def backend_factory_for_case(case_id: str) -> BackendFactory:
        return make_scripted_backend_factory(
            scripted_responses[case_id]
        )

    evaluation = run_evaluation(
        cases=cases,
        model=args.model,
        backend_factory_for_case=backend_factory_for_case,
        parallel_tools=not args.sequential,
        autonomy=args.autonomy,
        max_steps=args.max_steps,
        budget_usd=args.budget_usd,
        prompt_version=args.prompt_version,
    )

    save_results(evaluation, args.output)
    print_summary(evaluation)


if __name__ == "__main__":
    main()
