# D7 Loop-Control Ablation

The experiment runs the same ten deterministic D7 cases twice. The failure
configuration removes only duplicate-action detection. Step, budget,
autonomy and hostile-text protections remain enabled. The restored
configuration enables the full protection stack.

| Configuration | Runs | Median turns | Worst-case turns | Cap-hit runs | Cap events | Loop-control cap-hit runs | Cap types |
|---|---:|---:|---:|---:|---:|---:|---|
| Dedupe removed | 10 | 2.0 | 4 | 8 | 9 | 3 | {"AUTONOMY_BLOCKED": 1, "BUDGET_EXCEEDED": 1, "HOSTILE_TEXT_REPEATED": 1, "INSTRUCTION_IN_NARRATIVE": 4, "STEP_LIMIT": 2} |
| Full protection | 10 | 2.0 | 4 | 8 | 9 | 3 | {"AUTONOMY_BLOCKED": 1, "BUDGET_EXCEEDED": 1, "DUPLICATE_ACTION": 1, "HOSTILE_TEXT_REPEATED": 1, "INSTRUCTION_IN_NARRATIVE": 4, "STEP_LIMIT": 1} |

## Turn distributions

- Dedupe removed: `{"1": 2, "2": 4, "3": 2, "4": 2}`
- Full protection: `{"1": 2, "2": 5, "3": 2, "4": 1}`

## Interpretation

With duplicate-action detection removed, the repeated-action case continues
until the retained step cap. With the full stack restored, the same repeated
call is stopped earlier by `DUPLICATE_ACTION`. The other D7 cases keep the
same controls and provide the common evaluation set for the distribution.
