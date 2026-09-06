"""Tests for prompt-version-aware tool return contracts."""

import unittest
from unittest.mock import patch

from Evals.evaluate import run_case
from src.schemas import ErrorDetail, RunResult, SCHEMA_VERSION, ToolResult
from src.tools.problem_a import TOOLS
from src.tools.versioned import get_versioned_tool_registry


class VersionedToolRegistryTests(unittest.TestCase):

    def test_v1_converts_found_preauthorisation_to_one_record(self) -> None:
        tool = get_versioned_tool_registry("v1")["get_preauthorisation"]

        result = tool("M-2214", "62480", "2025-02-10")

        self.assertTrue(result.ok)
        self.assertEqual(len(result.data["records"]), 1)
        self.assertEqual(
            set(result.data["records"][0]),
            {"preauth_id", "valid_from", "valid_to"},
        )
        self.assertNotIn("valid", result.data["records"][0])

    def test_v1_converts_absent_preauthorisation_to_empty_records(self) -> None:
        tool = get_versioned_tool_registry("v1")["get_preauthorisation"]

        result = tool("M-2214", "99213", "2025-02-10")

        self.assertTrue(result.ok)
        self.assertEqual(result.data, {"records": []})

    def test_v1_preserves_tool_failures(self) -> None:
        failure = ToolResult(
            ok=False,
            error=ErrorDetail(code="NOT_FOUND", message="missing"),
        )

        def failing_tool(*args: object, **kwargs: object) -> ToolResult:
            return failure

        registry = dict(TOOLS)
        registry["get_preauthorisation"] = failing_tool
        tool = get_versioned_tool_registry("v1", registry)[
            "get_preauthorisation"
        ]

        self.assertIs(tool("M-x", "P-x", "2025-01-01"), failure)

    def test_v2_retains_current_fixed_shape_and_handler(self) -> None:
        registry = get_versioned_tool_registry("v2")

        self.assertIs(registry["get_preauthorisation"], TOOLS["get_preauthorisation"])
        result = registry["get_preauthorisation"](
            "M-2214", "62480", "2025-02-10"
        )
        self.assertEqual(
            set(result.data),
            {"found", "preauth_id", "valid", "valid_from", "valid_to"},
        )

    def test_v1_changes_only_the_preauthorisation_handler(self) -> None:
        registry = get_versioned_tool_registry("v1")

        for name, handler in TOOLS.items():
            if name != "get_preauthorisation":
                self.assertIs(registry[name], handler)

    def test_registry_inputs_are_not_mutated(self) -> None:
        supplied = dict(TOOLS)
        original_handler = supplied["get_preauthorisation"]

        get_versioned_tool_registry("v1", supplied)

        self.assertIs(supplied["get_preauthorisation"], original_handler)

    def test_invalid_version_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            get_versioned_tool_registry("v3")

    def test_evaluation_passes_the_prompt_matching_registry_to_loop(self) -> None:
        captured: dict[str, object] = {}

        class Backend:
            name = "test"

        def fake_run_agent(case_id: str, **kwargs: object) -> RunResult:
            captured.update(kwargs)
            return RunResult(
                schema_version=SCHEMA_VERSION,
                run_id="run-test",
                case_id=case_id,
                backend="test",
                model="test-model",
                prompt_version="v1",
                mode="sequential",
                autonomy="suggest",
                trial=1,
                status="completed",
                final=None,
                error=None,
                turns=1,
                tool_calls=0,
                tokens_in=0,
                tokens_out=0,
                cost_usd=0.0,
                latency_ms=0.0,
            )

        case = {
            "case_id": "CLM-test",
            "negative": False,
            "family": "ordinary",
            "expected": {"expected_decision": "escalate"},
        }

        with (
            patch("Evals.evaluate.run_agent", side_effect=fake_run_agent),
            patch(
                "Evals.evaluate.evaluate_result",
                return_value={"code_passed": True},
            ),
        ):
            output = run_case(
                case,
                model="test-model",
                backend=Backend(),
                prompt_version="v1",
            )

        registry = captured["tool_registry"]
        preauth = registry["get_preauthorisation"](
            "M-2214", "62480", "2025-02-10"
        )
        self.assertIn("records", preauth.data)
        self.assertEqual(output["trials"][0]["result"]["run_id"], "run-test")


if __name__ == "__main__":
    unittest.main()
