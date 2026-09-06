"""Evaluation runner for the health-insurance ReAct agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from src.agent.loop import run_agent
from src.agent.prompt_loader import load_prompt
from src.backends.base import ModelBackend
from src.schemas import GuardConfig, RunResult

from Evals.checks import evaluate_result


REFERENCE_DATA = (
    Path(__file__).resolve().parent.parent
    / "reference_data"
)


def run_case(
    case: Mapping[str, Any],
    *,
    backend: ModelBackend,
    model: str,
    parallel_tools: bool,
    autonomy: str,
    max_steps: int,
    budget_usd: float,
    guard_config: GuardConfig,
    tool_registry: Mapping[str, Any],
    prompt_version: str = "v2",
    trial: int = 1,
    temperature: float = 0.0,
    guard_hooks: Any = None,
) -> dict[str, Any]:
    """Run and grade one evaluation trial."""

    case_id = case["case_id"]

    system_prompt = load_prompt(prompt_version)

    result: RunResult = run_agent(
        case_id=case_id,
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
        system_prompt=system_prompt,
        temperature=temperature,
        guard_hooks=guard_hooks,
    )

    evaluation = evaluate_result(
        result,
        case,
    )

    return {
        "case_id": case_id,
        "trial": trial,
        "run": result.to_dict(),
        "evaluation": evaluation,
    }


def run_evaluation(
    cases: list[Mapping[str, Any]],
    *,
    backend: ModelBackend,
    model: str,
    parallel_tools: bool,
    autonomy: str,
    max_steps: int,
    budget_usd: float,
    guard_config: GuardConfig,
    tool_registry: Mapping[str, Any],
    prompt_version: str = "v2",
    temperature: float = 0.0,
    guard_hooks: Any = None,
) -> list[dict[str, Any]]:
    """
    Run the complete evaluation set.

    Ordinary cases:
        1 trial

    Negative cases:
        3 trials
    """

    results: list[dict[str, Any]] = []

    for case in cases:
        trial_count = 3 if case.get("negative", False) else 1

        for trial in range(1, trial_count + 1):
            result = run_case(
                case,
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
                temperature=temperature,
                guard_hooks=guard_hooks,
            )

            results.append(result)

    return results


def summarize_results(
    results: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Create a simple summary for reporting."""

    total_trials = len(results)

    passed_trials = sum(
        1
        for result in results
        if result["evaluation"]["passed"]
    )

    failed_trials = total_trials - passed_trials

    return {
        "total_trials": total_trials,
        "passed_trials": passed_trials,
        "failed_trials": failed_trials,
        "pass_rate": (
            passed_trials / total_trials
            if total_trials
            else 0.0
        ),
    }
