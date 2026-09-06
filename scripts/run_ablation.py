"""Guard on/off ablation over the 10 scripted guardrail cases.

Runs every case in `case_contributions/fengjingjing/guardrail_cases.py`
twice — once with the full guard stack enabled, once with every guard
(loop-level `GuardConfig` flags plus the domain `GuardHooks` toggles)
disabled — and reports, per case, whether the run's outcome changed and
whether an action that should have been blocked actually executed.

    python -m scripts.run_ablation

This is the artefact referenced in Miao's checklist item "guard 开启/关闭的
ablation 对照"; the printed table is meant to be pasted into the
poka-yoke / experiment write-up.

Caveat worth flagging to the team: `src/agent/loop.py` enforces the
suggest-mode write block unconditionally inside `_call_tool` — it does not
consult `GuardConfig.autonomy_enabled` at all. So GR-05 does not change
between the "on" and "off" columns below no matter how the guard config is
set; only `GuardHooks.autonomy_guard_enabled` (a defence-in-depth re-check)
is actually toggle-able for that case. This is worth confirming with Miao
against the intended spec.
"""

from __future__ import annotations

from types import SimpleNamespace

from case_contributions.fengjingjing.guardrail_cases import ALL_CASES
from src.agent.loop import run_agent
from src.guards.policy import GuardHooks
from src.schemas import GuardConfig


GUARDS_ON = (
    GuardConfig(step_limit_enabled=True, budget_enabled=True, dedupe_enabled=True, autonomy_enabled=True),
    lambda: GuardHooks(hostile_text_enabled=True, autonomy_guard_enabled=True),
)
GUARDS_OFF = (
    GuardConfig(step_limit_enabled=False, budget_enabled=False, dedupe_enabled=False, autonomy_enabled=False),
    lambda: GuardHooks(hostile_text_enabled=False, autonomy_guard_enabled=False),
)


def _run_one(case, guard_config, guard_hooks_factory):
    guard_hooks = guard_hooks_factory()
    run_kwargs, recorder = case.build(guard_hooks, guard_config)
    try:
        result = run_agent(**run_kwargs)
    except (StopIteration, RuntimeError):
        # With the relevant cap disabled the loop no longer halts where the
        # scripted case expected it to, so it keeps calling the model past
        # the end of the fixed response script. That is itself the ablation
        # finding for this case: without the guard, the run does not stop.
        result = SimpleNamespace(status="ran_past_script(no_halt)", caps_fired=[])
    blocked_write_executed = any(
        recorder.get(tool)
        for tool in ("issue_decision_letter",)
    ) and case.family in {"autonomy", "hostile_text"}
    return result, recorder, blocked_write_executed


def _write_executed(recorder: dict) -> bool:
    return bool(recorder.get("issue_decision_letter"))


def main() -> int:
    header = (
        f"{'Case':7} {'Family':14} {'ON status':11} {'ON caps':32} {'ON write':9} "
        f"{'OFF status':24} {'OFF caps':10} {'OFF write'}"
    )
    print(header)
    print("-" * len(header))

    unsafe_when_off = []
    for case in ALL_CASES:
        on_config, on_hooks_factory = GUARDS_ON
        off_config, off_hooks_factory = GUARDS_OFF

        on_result, on_recorder, _ = _run_one(case, on_config, on_hooks_factory)
        off_result, off_recorder, _ = _run_one(case, off_config, off_hooks_factory)

        print(
            f"{case.case_id:7} {case.family:14} "
            f"{on_result.status:11} {str(on_result.caps_fired):32} {str(_write_executed(on_recorder)):9} "
            f"{off_result.status:24} {str(off_result.caps_fired):10} {_write_executed(off_recorder)}"
        )

        # A case is only "unsafe with guards off" if the write tool actually
        # executed where the guarded run kept it from executing.
        if not on_recorder.get("issue_decision_letter") and off_recorder.get("issue_decision_letter"):
            unsafe_when_off.append(case.case_id)

    print()
    if unsafe_when_off:
        print(f"Guard-off runs that let a write execute the guarded run blocked: {unsafe_when_off}")
    else:
        print("No case let a write execute with guards off that the guarded run blocked to a different tool result;")
        print("compare status/caps columns above for read-only cases (GR-02/03/04/06/09/10).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
