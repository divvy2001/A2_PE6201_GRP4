# PE6201 A2 – Applied AI System

## Health Insurance Claim First Response

This project implements a single-agent ReAct system for first-response processing of health insurance claims.

The agent dynamically investigates claims using bounded tools, gathers evidence from the available records, determines the appropriate outcome, and performs a gated decision action when the required evidence has been established.

---

## Repository Structure

```text
A2_PE6201_GRP4/
│
├── case_contributions/
│   ├── Divyansh/
│   │   ├── claims.json
│   │   ├── expected_outcomes.json
│   │   ├── README.md
│   │   └── scripted_cases.py
│   ├── fengjingjing/
│   │   ├── cases.py
│   │   ├── guardrail_cases.py
│   │   ├── labels.json
│   │   └── README.md
│   ├── liang_luwen/
│   │   ├── cases.py
│   │   ├── labels.json
│   │   └── README.md
│   ├── li_zihao/
│   │   ├── cases.py
│   │   ├── labels.json
│   │   └── README.md
│   ├── miao_jiaxuan/
│   │   ├── cases.py
│   │   ├── labels.json
│   │   └── README.md
│   └── xiao_xiaohua/
│       ├── cases.py
│       ├── labels.json
│       └── README.md
│
├── docs/
│   ├── d2a_tool_rationale.md
│   ├── HANDOFF_LI_ZIHAO.md
│   ├── tool_interface_draft.md
│   ├── V1.2_INTERFACE_REFINEMENTS_BILINGUAL.md
│   └── VERSION_OVERVIEW_v1.1_BILINGUAL.md
│
├── Evals/
│   ├── checks.py
│   ├── evaluate.py
│   ├── judgement.py
│   ├── results.json
│   └── scripted_cases.py
│
├── notebooks/
│   ├── 01_loop_li_zihao.ipynb
│   └── 06_cost_liang_luwen.ipynb
│
├── outputs/
│   ├── ablation/
│   ├── cost/
│   ├── decision_log.jsonl
│   └── results/
│       ├── archive_pre_final/
│       └── *.json
│
├── reference_data/
│   ├── data_A/
│   │   ├── claims.json
│   │   ├── decided_claims.json
│   │   ├── hospitals.json
│   │   ├── members.json
│   │   ├── policies.json
│   │   ├── preauthorisations.json
│   │   ├── procedures.json
│   │   └── required_documents.json
│   ├── check_my_data.py
│   ├── data_dictionary.json
│   ├── expected_outcomes_A.json
│   ├── make_fixtures_A.py
│   └── README.md
│
├── scripts/
│   ├── run_ablation.py
│   ├── run_guardrail_cases.py
│   ├── run_loop_control_ablation.py
│   └── run_scripted.py
│
├── src/
│   ├── agent/
│   │   ├── dependency.py
│   │   ├── loop.py
│   │   ├── parser.py
│   │   ├── prompt_loader.py
│   │   ├── prompt_v1.txt
│   │   └── prompt_v2.txt
│   ├── backends/
│   │   ├── base.py
│   │   ├── live.py
│   │   └── scripted.py
│   ├── guards/
│   │   └── policy.py
│   ├── schemas.py
│   ├── telemetry/
│   │   └── cost.py
│   └── tools/
│       ├── base.py
│       ├── data_store.py
│       ├── descriptors.py
│       ├── problem_a.py
│       ├── registry.py
│       └── versioned.py
│
├── tests/
│   ├── test_cost.py
│   ├── test_descriptors.py
│   ├── test_guards.py
│   ├── test_loop.py
│   ├── test_tools.py
│   └── test_versioned_tools.py
│
├── contributions.md
└── README.md
```

The `.venv/`, `__pycache__/`, and other generated/package files are omitted from the overview above.

---

## Evaluation – Main Entry Point

The **`Evals/` directory is the main entry point for running the evaluation**.

The main evaluation script is:

```text
Evals/evaluate.py
```

The evaluation cases are defined in:

```text
Evals/scripted_cases.py
```

By default, the evaluation uses:

- **Backend:** `scripted`
- **Prompt version:** `v2`

The scripted backend is deterministic and does not require an API key.

---

## Running Evaluations

### Run one case

To run a single case using the default scripted backend and v2 prompt:

```bash
python -m Evals.evaluate --case-id CLM-8842
```

Replace `CLM-8842` with the ID of the case you want to evaluate.

### Run all cases

To run all evaluation cases:

```bash
python -m Evals.evaluate --all
```

Because the default backend is scripted, this runs the deterministic scripted evaluation with prompt version v2.

### Add an LLM judge

To run the evaluation with an LLM judge:

```bash
python -m Evals.evaluate --all --judge-model "JUDGE_MODEL"
```

For a single case:

```bash
python -m Evals.evaluate --case-id CLM-8842 --judge-model "JUDGE_MODEL"
```

The judge is used for semantic/L2 judgement checks.

### Run the live backend

To evaluate a live model through OpenRouter:

```bash
python -m Evals.evaluate --all --backend live --model "AGENT_MODEL"
```

For a single live case:

```bash
python -m Evals.evaluate --case-id CLM-8842 --backend live --model "AGENT_MODEL"
```

For a live evaluation with an LLM judge:

```bash
python -m Evals.evaluate --all --backend live --model "AGENT_MODEL" --judge-model "JUDGE_MODEL"
```

The live backend requires an OpenRouter API key. The evaluation script prompts for the key when the live backend or an LLM judge is used.

---

## Evaluation Cases

The evaluation harness runs the cases defined in:

```text
Evals/scripted_cases.py
```

The cases cover ordinary, negative, and adversarial scenarios.

The expected outcomes used for evaluation are stored in:

```text
reference_data/expected_outcomes_A.json
```

Each case is evaluated against the expected outcome using deterministic checks and, where configured, semantic judgement.

---

## Evaluation Checks

The evaluation uses two levels of checks.

### L1 – Deterministic checks

L1 verifies structured requirements such as:

- Decision
- Trigger
- Missing information
- Escalation
- Required totals
- Gated action behaviour

### L2 – Judgement checks

L2 evaluates semantic requirements in the agent's final response, including whether the required evidence and reasoning are present.

The overall result is:

```text
Overall = L1 pass AND L2 pass
```

---

## Evaluation Results

Evaluation results are stored as JSON files in:

```text
outputs/results/
```

The repository also contains:

```text
Evals/results.json
```

and archived evaluation results under:

```text
outputs/results/archive_pre_final/
```

The JSON result files contain evaluation outputs such as:

- Case-level results
- Trial-level results
- L1 results
- L2 judgement results
- Overall pass/fail status
- Token usage
- Tool calls and execution traces
- Latency and other evaluation metrics

This allows results to be inspected without rerunning the evaluation.

---

## Trials

Ordinary cases are evaluated once.

Negative cases are evaluated across multiple trials to assess consistency when the correct response requires requesting information or escalating rather than approving the claim.

The evaluation results distinguish:

- Case pass rate
- Trial pass rate
- L1 pass rate
- L2 pass rate

---

## Guardrails

The agent includes controls intended to prevent unsafe or uncontrolled behaviour, including:

- Maximum step limit
- Budget ceiling
- Action de-duplication
- Explicit autonomy mode
- Gate before irreversible actions
- Protection against repeated tool execution
- Handling of hostile or prompt-injection-style request text

Guardrail cases can be run using:

```bash
python scripts/run_guardrail_cases.py
```

---

## Other Scripts

Additional analysis and experiment scripts are available under:

```text
scripts/
```

These include:

```bash
python scripts/run_scripted.py
python scripts/run_ablation.py
python scripts/run_loop_control_ablation.py
python scripts/run_guardrail_cases.py
```

---

## Reference Data

The reference data used by the system is located under:

```text
reference_data/
```

The main claim data is under:

```text
reference_data/data_A/
```

The expected outcomes are stored separately in:

```text
reference_data/expected_outcomes_A.json
```

The `reference_data/README.md` file provides additional information about the fixture data.

---

## Contributions

A separate file is provided at the repository root for documenting team contributions:

```text
contributions.md
```

The contents of this file will document individual team-member contributions to the project.

---

## Reproducibility

For a deterministic evaluation, use the default scripted backend:

```bash
python -m Evals.evaluate --all
```

The default prompt version is v2.

Live evaluations can vary because model responses, reasoning trajectories, provider latency, and tool-use decisions are not deterministic.

---

## Project Context

This project was developed for:

**PE6201 – Emerging AI Technologies**  
**A2 Applied AI System**  
**Problem A – Health Insurance Claim First Response**

The system is designed as a single-agent workflow rather than a fixed sequence of calls because the appropriate investigation path depends on evidence discovered during execution.
