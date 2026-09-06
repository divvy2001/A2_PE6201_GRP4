"""Run the health-insurance evaluation set through the agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from src.agent.loop import run_agent
from src.agent.prompt_loader import load_prompt
from src.backends.base import ModelBackend
from src.schemas import GuardConfig, RunResult

from evaluation.checks import evaluate_result


# These are the negative families in the supplied starter evaluation set.
# They receive 3 trials according to the assignment.
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


def load_evaluation_cases(
    path: str | Path,
) -> list[dict[str, Any]]:
    """Load the labelled evaluation answer key."""

    path = Path(path)

    with path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list):
        raise ValueError(
            "Evaluation answer key must contain a JSON list."
        )

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError(
                "Each evaluation case must be a JSON object."
            )

        if "case_id" not in case:
            raise ValueError(
                "Evaluation case is missing 'case_id'."
            )

        if "expected_decision" not in case:
            raise ValueError(
                f"{case['case_id']} is missing "
                "'expected_decision'."
            )

    return cases


def is_negative_case(
    case: Mapping[str, Any],
) -> bool:
    """Return whether this case receives three trials."""

    return case.get("family") in NEGATIVE_FAMILIES


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
    """Run and grade one case/trial."""

    case_id = case["case_id"]

    # The evaluator knows the case ID and expected outcome.
    # The agent obtains the actual claim/world data through its tools.
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
        dict(case),
    )

    return {
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

    Ordinary cases: 1 trial.
    Negative cases: 3 trials.
    """

    results: list[dict[str, Any]] = []

    for case in cases:
        trial_count = (
            3
            if is_negative_case(case)
            else 1
        )

        for trial in range(1, trial_count + 1):
            results.append(
                run_case(
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
            )

    return results


def summarise_results(
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a small summary for reporting."""

    total_runs = len(results)

    code_passes = sum(
        1
        for result in results
        if result["evaluation"]["code_passed"]
    )

    completed_runs = sum(
        1
        for result in results
        if result["run"]["status"] == "completed"
    )

    total_tokens_in = sum(
        result["run"].get("tokens_in", 0)
        for result in results
    )

    total_tokens_out = sum(
        result["run"].get("tokens_out", 0)
        for result in results
    )

    total_cost = sum(
        result["run"].get("cost_usd", 0.0)
        for result in results
    )

    return {
        "total_runs": total_runs,
        "code_passes": code_passes,
        "code_pass_rate": (
            code_passes / total_runs
            if total_runs
            else 0.0
        ),
        "completed_runs": completed_runs,
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
        "total_cost_usd": total_cost,
    }
