from src.telemetry.cost import (
    baseline_variable_cost,
    break_even_success_rate,
    cost_per_successful_task,
    expected_fallback_cost,
    monthly_cost,
    sensitivity_rates,
)


def test_problem_a_failure_cost_layer_and_monthly_formula():
    failure_cost = 38.0 * 12.0 / 60.0
    assert failure_cost == 7.6
    assert expected_fallback_cost(0.60, failure_cost) == 3.04
    total = cost_per_successful_task(0.01, 0.60, failure_cost)
    assert abs(total - 3.05) < 1e-12
    assert abs(monthly_cost(total, 8000, 0.0) - 24400.0) < 1e-9


def test_variable_cost_and_break_even_are_bounded():
    c = baseline_variable_cost(1_000_000, 100_000, 0.20, 1.20)
    assert abs(c - 0.32) < 1e-12
    p = break_even_success_rate(0.001, 3.0, 7.6)
    assert 0.0 <= p <= 1.0


def test_sensitivity_points_include_measured_rate():
    rates = sensitivity_rates(0.60)
    assert rates == [0.5, 0.55, 0.6, 0.65, 0.7]
