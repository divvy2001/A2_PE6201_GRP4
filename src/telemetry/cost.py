"""Reusable D6 cost-to-serve functions for PE6201 A2 Problem A.

The baseline follows the Class 5 three-layer model:

Layer 1 = model token cost + retrieval/tool fees
Layer 2 = (1 - success_rate) * failure_cost
Monthly = (Layer 1 + Layer 2) * volume + Layer 3

All inputs are explicit so the notebook remains the source of business assumptions.
"""

from __future__ import annotations


def _validate_rate(value: float, name: str = "success_rate") -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


def baseline_variable_cost(
    tokens_in: float,
    tokens_out: float,
    input_price_per_1m: float,
    output_price_per_1m: float,
    retrieval_usd: float = 0.0,
    tool_usd: float = 0.0,
) -> float:
    """Layer 1 variable cost for one task/run."""
    values = {
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "input_price_per_1m": input_price_per_1m,
        "output_price_per_1m": output_price_per_1m,
        "retrieval_usd": retrieval_usd,
        "tool_usd": tool_usd,
    }
    if any(value < 0 for value in values.values()):
        bad = [name for name, value in values.items() if value < 0]
        raise ValueError(f"Cost inputs cannot be negative: {bad}")

    return (
        tokens_in / 1_000_000 * input_price_per_1m
        + tokens_out / 1_000_000 * output_price_per_1m
        + retrieval_usd
        + tool_usd
    )


def expected_fallback_cost(success_rate: float, failure_cost_usd: float) -> float:
    """Layer 2 expected human fallback cost for one task."""
    _validate_rate(success_rate)
    if failure_cost_usd < 0:
        raise ValueError("failure_cost_usd cannot be negative")
    return (1.0 - success_rate) * failure_cost_usd


def cost_per_successful_task(
    variable_cost_usd: float,
    success_rate: float,
    failure_cost_usd: float,
) -> float:
    """Layer 1 + Layer 2 cost-to-serve for one task."""
    if variable_cost_usd < 0:
        raise ValueError("variable_cost_usd cannot be negative")
    return variable_cost_usd + expected_fallback_cost(success_rate, failure_cost_usd)


def monthly_cost(
    cost_per_task_usd: float,
    volume: int,
    fixed_monthly_usd: float,
) -> float:
    """Monthly cost including Layer 3."""
    if cost_per_task_usd < 0 or volume < 0 or fixed_monthly_usd < 0:
        raise ValueError("Monthly cost inputs cannot be negative")
    return cost_per_task_usd * volume + fixed_monthly_usd


def break_even_success_rate(
    cheap_variable_cost_usd: float,
    expensive_total_cost_usd: float,
    failure_cost_usd: float,
) -> float:
    """Success rate at which a cheap model matches a benchmark cost-to-serve."""
    if failure_cost_usd <= 0:
        raise ValueError("failure_cost_usd must be greater than zero")
    p = 1.0 - (expensive_total_cost_usd - cheap_variable_cost_usd) / failure_cost_usd
    return max(0.0, min(1.0, p))


def sensitivity_rates(
    success_rate: float,
    spread: float = 0.10,
    step: float = 0.05,
) -> list[float]:
    """Return bounded success-rate points across ±spread at the requested step."""
    _validate_rate(success_rate)
    if spread < 0 or step <= 0:
        raise ValueError("spread must be non-negative and step must be positive")

    lower = max(0.0, success_rate - spread)
    upper = min(1.0, success_rate + spread)
    values: list[float] = []
    current = lower
    while current <= upper + 1e-12:
        values.append(round(current, 10))
        current += step
    return values
