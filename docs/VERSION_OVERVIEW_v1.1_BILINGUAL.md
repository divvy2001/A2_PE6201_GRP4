# PE6201 A2 Group 4 — Version Overview / 版本说明

This document explains what v1.0 implemented, what v1.1 added, and what the
project can currently run.

本文说明 v1.0 已实现的内容、v1.1 新增的内容，以及项目目前可以运行的能力。

---

## 1. Version 1.0 / v1.0 实现内容

### 中文

v1.0 由 XIAO XIAOHUA 完成，主要建立了 Problem A 的底层数据访问层。

`src/tools/data_store.py` 可以从老师提供的 JSON 数据中读取和查询：

- claim（理赔申请）；
- member（会员）；
- policy（保单）；
- hospital（医院）；
- procedure（医疗项目）；
- required document（所需文件）；
- pre-authorisation（预授权记录）；
- decided claim（历史已处理理赔）。

v1.0 还实现了 duplicate claim 检查。只有以下四项全部相同，才会认定为重复理赔：

1. `member_id`；
2. `hospital_id`；
3. `date_of_service`；
4. 完整的 procedure line items，包括 code 和 amount。

为了防止误判，line items 会先进行标准化和排序，因此输入顺序不同不会影响比较结果。

v1.0 包含 5 个数据层测试：

- 查询已知 claim；
- 未知 claim 返回清晰错误；
- true duplicate 正确匹配；
- 服务日期不同的 near-miss 不被误判为 duplicate；
- line items 不同的 near-miss 不被误判为 duplicate。

### English

Version 1.0 was implemented by XIAO XIAOHUA and established the low-level data
access layer for Problem A.

`src/tools/data_store.py` can load and query the teacher-provided JSON data for:

- claims;
- members;
- policies;
- hospitals;
- procedures;
- required documents;
- pre-authorisation records; and
- previously decided claims.

v1.0 also implemented duplicate-claim detection. A claim is considered a true
duplicate only when all four fields match:

1. `member_id`;
2. `hospital_id`;
3. `date_of_service`; and
4. the complete set of procedure line items, including code and amount.

Line items are normalised and sorted before comparison, so their input order does
not change the result.

v1.0 includes five data-layer tests covering a known claim, a clear error for an
unknown claim, a true duplicate, a date near-miss, and a line-item near-miss.

---

## 2. Version 1.1 additions / v1.1 新增内容

### 中文

v1.1 保留了 v1.0 的数据、`data_store.py` 和原有测试，并在其基础上加入了
LI ZIHAO 负责的 agent loop、公共架构和集成骨架。

新增内容如下：

| 文件 | 新增能力 |
|---|---|
| `src/schemas.py` | 定义统一的 `ModelResponse`、`ToolResult`、`Action`、`ActionBlock`、`Observation`、`FinalDecision`、`TraceEvent`、`GuardConfig` 和 `RunResult` |
| `src/backends/base.py` | 定义统一的 `ModelBackend` 接口，使 scripted 和 live backend 可以使用同一个 loop |
| `src/agent/parser.py` | 严格解析模型输出的 JSON；每轮只接受一个 `ActionBlock` 或一个 `FinalDecision` |
| `src/agent/dependency.py` | 检查 `call_id`、同一批次重复调用，以及 write tool 是否被错误地放入并行批次 |
| `src/agent/loop.py` | 实现手写单 Agent ReAct loop、顺序/并行工具执行、Observation 回传、parse retry、预算/步数/重复调用限制、autonomy 保护、guard hooks、trace 和统一 RunResult |
| `notebooks/01_loop_li_zihao.ipynb` | 提供不需要 API key 的最小 loop 演示 |
| `tests/test_loop.py` | 测试 parser、并行 ActionBlock、重复调用拦截和 guard hook |
| `docs/HANDOFF_LI_ZIHAO.md` | 说明模块接口、运行方法、责任边界和后续接入要求 |

v1.1 的 loop 结构参考并复用了 Class 4 的核心思想：

```text
Ask model → Meter usage → Parse/stop → Apply guards
          → Execute tools → Append observations → Next turn
```

课堂代码中的 order/shipment 业务内容没有被复制；它们被替换为适用于
health-insurance claim 项目的通用接口。

### English

Version 1.1 preserves the v1.0 reference data, `data_store.py`, and original tests.
It adds the agent-loop, shared architecture, and integration skeleton owned by
LI ZIHAO.

The additions are:

| File | Added capability |
|---|---|
| `src/schemas.py` | Shared `ModelResponse`, `ToolResult`, `Action`, `ActionBlock`, `Observation`, `FinalDecision`, `TraceEvent`, `GuardConfig`, and `RunResult` contracts |
| `src/backends/base.py` | A common `ModelBackend` interface so scripted and live backends can use the same loop |
| `src/agent/parser.py` | Strict JSON parsing; each model turn must contain exactly one ActionBlock or FinalDecision |
| `src/agent/dependency.py` | Validation for call IDs, duplicate calls within a block, and unsafe batching of a write tool |
| `src/agent/loop.py` | A hand-written single-agent ReAct loop with sequential/parallel execution, observation feedback, bounded parse retry, step/budget/duplicate controls, autonomy protection, guard hooks, traces, and a unified RunResult |
| `notebooks/01_loop_li_zihao.ipynb` | A minimum API-free demonstration of the loop |
| `tests/test_loop.py` | Tests for parsing, parallel ActionBlocks, duplicate-action blocking, and guard-hook integration |
| `docs/HANDOFF_LI_ZIHAO.md` | Module boundaries, reproduction instructions, and integration requirements |

The v1.1 loop adapts the main six-stage idea from the Class 4 code:

```text
Ask model → Meter usage → Parse/stop → Apply guards
          → Execute tools → Append observations → Next turn
```

The order/shipment domain logic from the classroom example was not copied. It was
replaced with provider-neutral interfaces suitable for the health-insurance claim
project.

---

## 3. What can run now? / 目前可以实现什么？

### 中文

v1.1 目前已经可以：

- 使用统一接口接收 scripted backend 或 live backend；
- 接收模型产生的单个 Action 或包含多个 Action 的 ActionBlock；
- 判断 JSON 输出是否合法；
- 将多个独立的只读工具按顺序或并行执行；
- 保证 Observation 按 `call_id` 顺序放回模型上下文；
- 将未知工具、参数错误和工具异常转换成结构化错误，而不是让整个程序崩溃；
- 对连续两次无效模型输出进行受限重试和失败处理；
- 阻止重复工具调用；
- 执行 step limit 和 budget limit；
- 在 `suggest` 模式下阻止 write tool；
- 调用其他成员后续提供的 guardrail hooks；
- 记录 model、tool、guard 和 final 事件；
- 输出统一的 `RunResult`，供 evaluation 和 cost 模块使用；
- 使用 stub backend 和 stub tools 完成不需要 API key 的端到端 smoke run。

当前共有 10 个自动化测试，全部通过：

- Xiaohua 的 5 个数据层测试；
- Zihao 的 5 个 parser、loop 和 guard/integration 测试。

运行测试：

```text
python -m unittest discover -s tests -v
```

运行 `notebooks/01_loop_li_zihao.ipynb` 可以看到一次最小的完整流程：模型先请求
`get_claim`，loop 执行工具并回传 Observation，然后模型返回 FinalDecision，最终生成
状态为 `completed` 的 RunResult。

### English

v1.1 can currently:

- accept either a scripted or live backend through one shared interface;
- accept a single Action or a multi-action ActionBlock;
- validate the model's JSON output;
- execute independent read tools sequentially or in parallel;
- return all observations to the model in `call_id` order;
- convert unknown tools, invalid arguments, and tool exceptions into structured errors;
- apply a bounded retry when model output cannot be parsed;
- stop repeated tool calls;
- enforce step and budget limits;
- block write tools in `suggest` mode;
- call guardrail hooks supplied by another module;
- record model, tool, guard, and final events;
- produce a unified `RunResult` for evaluation and cost analysis; and
- complete an API-free end-to-end smoke run with stub backends and tools.

There are currently ten passing automated tests: Xiaohua's five data-layer tests
and Zihao's five parser, loop, guard, and integration tests.

Run all tests with:

```text
python -m unittest discover -s tests -v
```

Running `notebooks/01_loop_li_zihao.ipynb` demonstrates the minimum complete flow:
the backend first requests `get_claim`, the loop executes it and returns an
Observation, the backend then returns a FinalDecision, and the loop produces a
completed RunResult.
