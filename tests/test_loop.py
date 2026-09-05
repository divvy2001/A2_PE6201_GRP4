import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.agent.loop import run_agent
from src.agent.parser import StepParseError, parse_step
from src.schemas import ActionBlock, FinalDecision, GuardConfig, GuardDecision, ModelResponse, ToolResult
from src.tools.problem_a import TOOLS


class SequenceBackend:
    name = "scripted-test"

    def __init__(self, responses):
        self.responses = iter(responses)

    def generate(self, messages, *, model, temperature=0.0):
        text = next(self.responses)
        return ModelResponse(text, 10, 5, model, latency_ms=1.0, cost_usd=0.001)


def response(payload):
    return json.dumps(payload)


FINAL = {
    "type": "final",
    "final": {
        "decision": "approve_in_principle",
        "trigger": None,
        "missing": None,
        "escalate_to": None,
        "line_dispositions": [],
        "approved_total": 0,
        "refused_total": 0,
        "evidence": ["CLM-8842"],
    },
}


class ParserTests(unittest.TestCase):
    def test_parses_action_block_and_final(self):
        action = parse_step(response({
            "type": "action_block",
            "reasoning_summary": "Need two independent facts",
            "actions": [
                {"call_id": "t01-c01", "tool": "get_claim", "args": {"case_id": "CLM-8842"}}
            ],
        }))
        final = parse_step(response(FINAL))
        self.assertIsInstance(action, ActionBlock)
        self.assertIsInstance(final, FinalDecision)

    def test_rejects_non_json(self):
        with self.assertRaises(StepParseError):
            parse_step("I think we should approve")


class LoopTests(unittest.TestCase):
    def test_parallel_action_block_produces_ordered_trace_and_run_result(self):
        backend = SequenceBackend([
            response({
                "type": "action_block",
                "reasoning_summary": "Read independent facts",
                "actions": [
                    {"call_id": "t01-c02", "tool": "hospital", "args": {"hospital_id": "H-114"}},
                    {"call_id": "t01-c01", "tool": "claim", "args": {"case_id": "CLM-8842"}},
                ],
            }),
            response(FINAL),
        ])
        tools = {
            "claim": lambda case_id: ToolResult(True, {"claim_id": case_id}),
            "hospital": lambda hospital_id: ToolResult(True, {"hospital_id": hospital_id}),
        }
        result = run_agent(
            "CLM-8842",
            backend=backend,
            model="scripted-careful",
            parallel_tools=True,
            autonomy="confirm",
            max_steps=4,
            budget_usd=0.05,
            guard_config=GuardConfig(),
            tool_registry=tools,
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.mode, "parallel")
        self.assertEqual(result.tool_calls, 2)
        self.assertEqual([x["action"]["call_id"] for x in result.tool_trace], ["t01-c01", "t01-c02"])
        self.assertEqual(result.tokens_in, 20)
        self.assertEqual(result.cost_usd, 0.002)

    def test_duplicate_action_halts_loudly(self):
        repeated = response({
            "type": "action_block",
            "reasoning_summary": "repeat",
            "actions": [
                {"call_id": "t01-c01", "tool": "claim", "args": {"case_id": "CLM-8842"}}
            ],
        })
        second = repeated.replace("t01-c01", "t02-c01")
        backend = SequenceBackend([repeated, second])
        result = run_agent(
            "CLM-8842",
            backend=backend,
            model="scripted-repeats",
            parallel_tools=False,
            autonomy="confirm",
            max_steps=4,
            budget_usd=0.05,
            guard_config=GuardConfig(),
            tool_registry={"claim": lambda case_id: ToolResult(True, {"claim_id": case_id})},
        )
        self.assertEqual(result.status, "halted")
        self.assertIn("DUPLICATE_ACTION", result.caps_fired)
        self.assertEqual(result.tool_calls, 1)

    def test_guard_hook_blocks_tool_before_execution(self):
        class BlockingGuard:
            def before_tool_call(self, action, state):
                return GuardDecision(False, "test block", "TEST_GUARD")

        backend = SequenceBackend([
            response({
                "type": "action_block",
                "reasoning_summary": "try read",
                "actions": [
                    {"call_id": "t01-c01", "tool": "claim", "args": {"case_id": "CLM-8842"}}
                ],
            }),
            response(FINAL),
        ])
        executed = []
        result = run_agent(
            "CLM-8842",
            backend=backend,
            model="scripted-guard",
            parallel_tools=False,
            autonomy="confirm",
            max_steps=3,
            budget_usd=0.05,
            guard_config=GuardConfig(),
            tool_registry={"claim": lambda case_id: executed.append(case_id)},
            guard_hooks=BlockingGuard(),
        )
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.tool_calls, 0)
        self.assertEqual(executed, [])
        self.assertEqual(result.tool_trace[0]["observation"]["error"]["code"], "TEST_GUARD")

    def _run_write_tool_capture(self):
        decision_payload = FINAL["final"]
        backend = SequenceBackend([
            response({
                "type": "action_block",
                "reasoning_summary": "Log the completed decision",
                "actions": [{
                    "call_id": "t01-c01",
                    "tool": "issue_decision_letter",
                    "args": {
                        "case_id": "CLM-8842",
                        "decision_record": decision_payload,
                        "autonomy": "suggest",
                        "run_id": "model-supplied-run-id",
                        "operator_approved": False,
                    },
                }],
            }),
            response(FINAL),
        ])
        captured = {}

        def capture_write(**kwargs):
            captured.update(kwargs)
            return ToolResult(True, {"logged": True, "log_id": "test", "gate_result": "LOGGED"})

        result = run_agent(
            "CLM-8842",
            backend=backend,
            model="scripted-write",
            parallel_tools=True,
            autonomy="confirm",
            max_steps=3,
            budget_usd=0.05,
            guard_config=GuardConfig(),
            tool_registry={"issue_decision_letter": capture_write},
            operator_approved=True,
        )
        return result, captured

    def test_loop_injects_trusted_run_id_into_write_tool(self):
        """The model cannot choose or replace the run identifier."""
        result, captured = self._run_write_tool_capture()

        self.assertEqual(result.status, "completed")
        self.assertEqual(captured["run_id"], result.run_id)
        self.assertNotEqual(captured["run_id"], "model-supplied-run-id")
        self.assertEqual(captured["autonomy"], "confirm")
        self.assertTrue(captured["operator_approved"])

    def test_loop_converts_write_tool_decision_dict_to_final_decision(self):
        """Nested JSON arguments are validated before the write tool receives them."""
        _, captured = self._run_write_tool_capture()

        self.assertIsInstance(captured["decision_record"], FinalDecision)
        self.assertEqual(captured["decision_record"].decision, "approve_in_principle")

    def test_real_problem_a_registry_connects_to_loop(self):
        """The shared loop can execute Xiaohua's exported get_claim tool."""
        backend = SequenceBackend([
            response({
                "type": "action_block",
                "reasoning_summary": "Read the real claim fixture",
                "actions": [{
                    "call_id": "t01-c01",
                    "tool": "get_claim",
                    "args": {"case_id": "CLM-8842"},
                }],
            }),
            response(FINAL),
        ])
        result = run_agent(
            "CLM-8842",
            backend=backend,
            model="scripted-real-tools",
            parallel_tools=True,
            autonomy="confirm",
            max_steps=3,
            budget_usd=0.05,
            guard_config=GuardConfig(),
            tool_registry=TOOLS,
        )

        observation = result.tool_trace[0]["observation"]
        self.assertEqual(result.status, "completed")
        self.assertTrue(observation["ok"])
        self.assertEqual(observation["data"]["claim_id"], "CLM-8842")

    def test_real_write_tool_is_fail_closed_in_unapproved_confirm_mode(self):
        """The integrated loop/tool path must return a gate result without writing."""
        backend = SequenceBackend([
            response({
                "type": "action_block",
                "reasoning_summary": "Attempt the gated local write",
                "actions": [{
                    "call_id": "t01-c01",
                    "tool": "issue_decision_letter",
                    "args": {
                        "case_id": "CLM-8842",
                        "decision_record": FINAL["final"],
                        "operator_approved": True,
                    },
                }],
            }),
            response(FINAL),
        ])
        result = run_agent(
            "CLM-8842",
            backend=backend,
            model="scripted-real-write",
            parallel_tools=True,
            autonomy="confirm",
            max_steps=3,
            budget_usd=0.05,
            guard_config=GuardConfig(),
            tool_registry=TOOLS,
            operator_approved=False,
        )

        observation = result.tool_trace[0]["observation"]
        self.assertTrue(observation["ok"])
        self.assertFalse(observation["data"]["logged"])
        self.assertEqual(observation["data"]["gate_result"], "CONFIRMATION_REQUIRED")

    def test_real_write_tool_logs_loop_run_id_in_act_mode(self):
        """The complete write path records the loop's trusted run ID in isolated JSONL."""
        backend = SequenceBackend([
            response({
                "type": "action_block",
                "reasoning_summary": "Write the completed decision",
                "actions": [{
                    "call_id": "t01-c01",
                    "tool": "issue_decision_letter",
                    "args": {
                        "case_id": "CLM-8842",
                        "decision_record": FINAL["final"],
                        "run_id": "untrusted-model-value",
                    },
                }],
            }),
            response(FINAL),
        ])

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "decision_log.jsonl"
            with patch("src.tools.problem_a.DECISION_LOG_PATH", log_path):
                result = run_agent(
                    "CLM-8842",
                    backend=backend,
                    model="scripted-real-write",
                    parallel_tools=True,
                    autonomy="act",
                    max_steps=3,
                    budget_usd=0.05,
                    guard_config=GuardConfig(),
                    tool_registry=TOOLS,
                )

            record = json.loads(log_path.read_text(encoding="utf-8").strip())

        self.assertEqual(result.status, "completed")
        self.assertEqual(record["run_id"], result.run_id)
        self.assertNotEqual(record["run_id"], "untrusted-model-value")
        self.assertEqual(record["autonomy"], "act")


if __name__ == "__main__":
    unittest.main()
