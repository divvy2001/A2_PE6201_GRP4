"""Produce report-ready D7 loop-control ablation statistics.

This experiment removes exactly one protection: duplicate-action detection.
The step, budget, autonomy and hostile-text protections remain enabled.  The
same ten deterministic D7 guardrail cases run under both configurations.

The repeated-action fixture contains a finite scripted response sequence.  A
repeat-last wrapper extends only that deterministic sequence so the
dedupe-removed run can reach the retained step cap instead of ending because
the test fixture ran out of responses.

Run from the repository root:

    python -m scripts.run_loop_control_ablation

Outputs:
    outputs/ablation/loop_control_ablation.json
    outputs/ablation/loop_control_ablation.csv
    outputs/ablation/loop_control_ablation_summary.md
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

from case_contributions.fengjingjing.guardrail_cases import ALL_CASES
from src.agent.loop import run_agent
from src.guards.policy import GuardHooks
from src.schemas import GuardConfig, ModelResponse


OUTPUT_DIR = Path("outputs") / "ablation"
JSON_PATH = OUTPUT_DIR / "loop_control_ablation.json"
CSV_PATH = OUTPUT_DIR / "loop_control_ablation.csv"
SUMMARY_PATH = OUTPUT_DIR / "loop_control_ablation_summary.md"

FULL_PROTECTION = GuardConfig(
    step_limit_enabled=True,
    budget_enabled=True,
    dedupe_enabled=True,
    autonomy_enabled=True,
)
DEDUPE_REMOVED = GuardConfig(
    step_limit_enabled=True,
    budget_enabled=True,
    dedupe_enabled=False,
    autonomy_enabled=True,
)


class RepeatLastBackend:
    """Replay a finite scripted sequence, then repeat its last response."""

    name = "scripted-d7-repeat-last"

    def __init__(self, turns: list[tuple[dict[str, Any], float]]) -> None:
        if not turns:
            raise ValueError("The D7 scripted backend must contain at least one turn")
        self._turns = turns
        self._index = 0

    def generate(self, messages, *, model, temperature=0.0) -> ModelResponse:
        index = min(self._index, len(self._turns) - 1)
        payload, cost_usd = self._turns[index]
        self._index += 1
        return ModelResponse(
            json.dumps(payload),
            tokens_in=10,
            tokens_out=5,
            model=model,
            latency_ms=1.0,
            cost_usd=cost_usd,
        )


def _make_repeatable(run_kwargs: dict[str, Any]) -> None:
    original = run_kwargs["backend"]
    scripted_turns = list(original._turns)
    run_kwargs["backend"] = RepeatLastBackend(scripted_turns)


def _run_configuration(label: str, guard_config: GuardConfig) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in ALL_CASES:
        hooks = GuardHooks(hostile_text_enabled=True, autonomy_guard_enabled=True)
        run_kwargs, recorder = case.build(hooks, guard_config)
        _make_repeatable(run_kwargs)
        result = run_agent(**run_kwargs)
        rows.append(
            {
                "configuration": label,
                "case_id": case.case_id,
                "family": case.family,
                "status": result.status,
                "turns": result.turns,
                "tool_calls": result.tool_calls,
                "caps_fired": list(result.caps_fired),
                "error_code": (result.error or {}).get("code"),
                "write_executed": bool(recorder.get("issue_decision_letter")),
            }
        )
    return rows


def _summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    turns = [int(row["turns"]) for row in rows]
    cap_types = Counter(
        cap for row in rows for cap in row["caps_fired"]
    )
    loop_control_caps = {"DUPLICATE_ACTION", "STEP_LIMIT", "BUDGET_EXCEEDED"}
    return {
        "runs": len(rows),
        "median_turns": median(turns),
        "worst_case_turns": max(turns),
        "cap_hit_runs": sum(bool(row["caps_fired"]) for row in rows),
        "cap_events": sum(len(row["caps_fired"]) for row in rows),
        "loop_control_cap_hit_runs": sum(
            bool(loop_control_caps.intersection(row["caps_fired"])) for row in rows
        ),
        "cap_types": dict(sorted(cap_types.items())),
        "turn_distribution": dict(sorted(Counter(turns).items())),
        "status_distribution": dict(sorted(Counter(row["status"] for row in rows).items())),
    }


def _write_csv(rows: list[dict[str, Any]]) -> None:
    fields = [
        "configuration",
        "case_id",
        "family",
        "status",
        "turns",
        "tool_calls",
        "caps_fired",
        "error_code",
        "write_executed",
    ]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["caps_fired"] = ";".join(row["caps_fired"])
            writer.writerow(csv_row)


def _write_summary(payload: dict[str, Any]) -> None:
    before = payload["summary"]["dedupe_removed"]
    after = payload["summary"]["full_protection"]
    content = f"""# D7 Loop-Control Ablation

The experiment runs the same ten deterministic D7 cases twice. The failure
configuration removes only duplicate-action detection. Step, budget,
autonomy and hostile-text protections remain enabled. The restored
configuration enables the full protection stack.

| Configuration | Runs | Median turns | Worst-case turns | Cap-hit runs | Cap events | Loop-control cap-hit runs | Cap types |
|---|---:|---:|---:|---:|---:|---:|---|
| Dedupe removed | {before['runs']} | {before['median_turns']} | {before['worst_case_turns']} | {before['cap_hit_runs']} | {before['cap_events']} | {before['loop_control_cap_hit_runs']} | {json.dumps(before['cap_types'], sort_keys=True)} |
| Full protection | {after['runs']} | {after['median_turns']} | {after['worst_case_turns']} | {after['cap_hit_runs']} | {after['cap_events']} | {after['loop_control_cap_hit_runs']} | {json.dumps(after['cap_types'], sort_keys=True)} |

## Turn distributions

- Dedupe removed: `{json.dumps(before['turn_distribution'], sort_keys=True)}`
- Full protection: `{json.dumps(after['turn_distribution'], sort_keys=True)}`

## Interpretation

With duplicate-action detection removed, the repeated-action case continues
until the retained step cap. With the full stack restored, the same repeated
call is stopped earlier by `DUPLICATE_ACTION`. The other D7 cases keep the
same controls and provide the common evaluation set for the distribution.
"""
    SUMMARY_PATH.write_text(content, encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    before_rows = _run_configuration("dedupe_removed", DEDUPE_REMOVED)
    after_rows = _run_configuration("full_protection", FULL_PROTECTION)
    rows = before_rows + after_rows
    payload = {
        "experiment": {
            "evaluation_set": "10 deterministic D7 guardrail cases",
            "removed_protection": "duplicate-action detection",
            "retained_protections": [
                "step limit",
                "budget ceiling",
                "autonomy protection",
                "hostile-text protection",
            ],
            "measurement_note": (
                "Finite scripted responses repeat their final response only "
                "to let an unhalted run reach the retained step cap."
            ),
        },
        "summary": {
            "dedupe_removed": _summarise(before_rows),
            "full_protection": _summarise(after_rows),
        },
        "runs": rows,
    }

    JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_csv(rows)
    _write_summary(payload)

    print(SUMMARY_PATH.read_text(encoding="utf-8"))
    print(f"JSON: {JSON_PATH}")
    print(f"CSV: {CSV_PATH}")
    print(f"Summary: {SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
