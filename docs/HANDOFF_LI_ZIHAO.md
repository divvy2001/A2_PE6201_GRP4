# LI ZIHAO handoff — loop / architecture / integration (v1.1)

## Implemented

- `src/schemas.py`: shared schema v1.0 objects and validation.
- `src/backends/base.py`: provider-neutral `ModelBackend` protocol.
- `src/agent/parser.py`: strict JSON ActionBlock/Final parser.
- `src/agent/dependency.py`: call-id, duplicate and write-batch validation.
- `src/agent/loop.py`: one manual loop for scripted/live backends, ordered
  observations, sequential/parallel switch, parse retry, step/budget/dedupe caps,
  autonomy protection, injectable guard hooks, trace and unified `RunResult`.
- `tests/test_loop.py`: parser, parallel smoke run and duplicate-action tests.
- `notebooks/01_loop_li_zihao.ipynb`: API-free runnable demonstration.

The six-stage structure is adapted from the Class 4 `run_agent`: ask, meter,
stop/parse, guard, act and append. The order-domain functions were not copied.

## Inputs expected from other owners

- XIAO: `src.tools.registry.TOOLS` whose functions return `ToolResult` or the
  equivalent `{ok, data, error}` dictionary.
- Divyansh: scripted/live classes implementing `ModelBackend.generate(...)`.
- FENG: guard hooks. v1.1 already enforces the core step, budget, duplicate and
  suggest-mode write protections; her policy module will add domain checks.
- MIAO: the frozen v1/v2 system-prompt text.
- LIANG: final pricing source. `ModelResponse.cost_usd` is currently an optional
  backward-compatible field used by the budget cap.

## Run tests

From the repository root:

```text
python -m unittest discover -s tests -v
```

## Current limitation

This version intentionally does not implement Xiaohua's public Problem A wrappers
or registry, Divyansh's production scripted backend, Feng's domain guard policy,
or a live provider. The smoke test injects same-shape stubs so the loop can be
developed and reviewed without waiting for those modules.
