"""Tests for Miao Jiaxuan's versioned tool descriptors."""

import unittest

from src.agent.prompt_loader import load_prompt
from src.tools.descriptors import (
    TOOL_ORDER,
    V1_TOOL_SPECS,
    V2_TOOL_SPECS,
    get_tool_specs,
)


class DescriptorTests(unittest.TestCase):

    def test_both_versions_contain_exactly_seven_tools(self):
        self.assertEqual(tuple(V1_TOOL_SPECS), TOOL_ORDER)
        self.assertEqual(tuple(V2_TOOL_SPECS), TOOL_ORDER)
        self.assertEqual(len(V1_TOOL_SPECS), 7)
        self.assertEqual(len(V2_TOOL_SPECS), 7)

    def test_only_preauthorisation_descriptor_changes(self):
        changed = [
            name
            for name in TOOL_ORDER
            if V1_TOOL_SPECS[name] != V2_TOOL_SPECS[name]
        ]
        self.assertEqual(changed, ["get_preauthorisation"])

    def test_v2_makes_found_and_valid_explicit(self):
        contract = V2_TOOL_SPECS[
            "get_preauthorisation"
        ].return_contract

        self.assertIn("found", contract)
        self.assertIn("valid", contract)
        self.assertIn("At most one", contract)

    def test_only_decision_letter_is_irreversible(self):
        irreversible = [
            name
            for name, spec in V2_TOOL_SPECS.items()
            if spec.irreversible
        ]
        self.assertEqual(
            irreversible,
            ["issue_decision_letter"],
        )

    def test_prompts_are_not_empty_and_name_all_tools(self):
        for version in ("v1", "v2"):
            prompt = load_prompt(version)
            specs = get_tool_specs(version)

            for tool_name in specs:
                self.assertIn(tool_name, prompt)


if __name__ == "__main__":
    unittest.main()
