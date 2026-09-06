"""Run FENG jingjing's 10 scripted guardrail cases and print a pass/fail report.

    python -m scripts.run_guardrail_cases

Exits non-zero if any case fails, so it can be wired into CI alongside
`python -m unittest discover -s tests`.
"""

from __future__ import annotations

import sys

from case_contributions.fengjingjing.guardrail_cases import ALL_CASES
from src.agent.loop import run_agent
from src.guards.policy import GuardHooks
from src.schemas import GuardConfig


def main() -> int:
    failures = 0
    for case in ALL_CASES:
        guard_hooks = GuardHooks()
        guard_config = GuardConfig()
        run_kwargs, recorder = case.build(guard_hooks, guard_config)
        result = run_agent(**run_kwargs)
        issues = case.expect(result, recorder)

        tag = "HOSTILE" if case.hostile else "       "
        if issues:
            failures += 1
            print(f"[FAIL] {case.case_id} {tag} ({case.family}) — {case.note}")
            for issue in issues:
                print(f"        - {issue}")
        else:
            print(f"[ OK ] {case.case_id} {tag} ({case.family}) status={result.status} caps={result.caps_fired}")

    print()
    print(f"{len(ALL_CASES) - failures}/{len(ALL_CASES)} guardrail cases passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
