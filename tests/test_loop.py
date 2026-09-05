import json
import unittest

from src.agent.loop import run_agent
from src.agent.parser import StepParseError, parse_step
from src.schemas import ActionBlock, FinalDecision, GuardConfig, GuardDecision, ModelResponse, ToolResult


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


if __name__ == "__main__":
    unittest.main()
