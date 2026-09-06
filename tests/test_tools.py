import unittest

from src.schemas import FinalDecision, ToolResult
from src.tools.base import ToolSpec
from src.tools.data_store import (
    DataStoreError,
    find_duplicate_claim,
    get_claim_by_id,
)
from src.tools.problem_a import (
    build_problem_a_registry,
    check_coverage,
    check_duplicate_claim,
    get_claim,
    get_hospital_status,
    get_preauthorisation,
    lookup_policy,
    TOOLS,
    issue_decision_letter,
)
from src.tools.registry import ToolRegistry

def _demo_tool(case_id: str) -> ToolResult:
    """A small fake tool used only to test registry behaviour."""
    return ToolResult(ok=True, data={"case_id": case_id})

class DataStoreTests(unittest.TestCase):
    """Tests for safe reads from Problem A reference data."""

    def test_get_known_claim(self) -> None:
        """A known claim ID should return the matching claim record."""
        claim = get_claim_by_id("CLM-8842")

        self.assertEqual(claim["claim_id"], "CLM-8842")
        self.assertEqual(claim["member_id"], "M-2214")

    def test_unknown_claim_returns_clear_error(self) -> None:
        """An unknown claim ID should raise a clear structured error."""
        with self.assertRaisesRegex(DataStoreError, "CLAIM_NOT_FOUND"):
            get_claim_by_id("CLM-9999")

    def test_true_duplicate_matches_prior_claim(self) -> None:
        """A real duplicate should match the correct historical claim."""
        claim = get_claim_by_id("CLM-8933")

        prior_claim = find_duplicate_claim(
            claim["member_id"],
            claim["hospital_id"],
            claim["date_of_service"],
            claim["lines"],
        )

        self.assertIsNotNone(prior_claim)
        self.assertEqual(prior_claim["claim_id"], "CLM-8710")

    def test_date_near_miss_is_not_duplicate(self) -> None:
        """A claim differing only in service date must not be a duplicate."""
        claim = get_claim_by_id("CLM-8850")

        prior_claim = find_duplicate_claim(
            claim["member_id"],
            claim["hospital_id"],
            claim["date_of_service"],
            claim["lines"],
        )

        self.assertIsNone(prior_claim)

    def test_line_items_near_miss_is_not_duplicate(self) -> None:
        """A claim with different line items must not be a duplicate."""
        claim = get_claim_by_id("CLM-8960")

        prior_claim = find_duplicate_claim(
            claim["member_id"],
            claim["hospital_id"],
            claim["date_of_service"],
            claim["lines"],
        )

        self.assertIsNone(prior_claim)

    def test_registry_exposes_loop_ready_mapping(self) -> None:
        """A registered tool should be callable with named arguments."""
        spec = ToolSpec(
            name="get_claim",
            signature="get_claim(case_id: str)",
            what="Retrieve one claim.",
            input_contract="case_id: non-empty string",
            return_contract="Bounded claim facts.",
            fails_when=("CLAIM_NOT_FOUND",),
            irreversible=False,
        )

        registry = ToolRegistry()
        registry.register(spec, _demo_tool)

        tools = registry.as_mapping()
        result = tools["get_claim"](case_id="CLM-8842")

        self.assertTrue(result.ok)
        self.assertEqual(result.data["case_id"], "CLM-8842")

    def test_get_claim_returns_structured_success_and_failure(self) -> None:
        """The public tool returns ToolResult for both outcomes."""
        success = get_claim("CLM-8842")
        self.assertTrue(success.ok)
        self.assertEqual(success.data["claim_id"], "CLM-8842")
        self.assertIsNone(success.error)

        failure = get_claim("CLM-9999")
        self.assertFalse(failure.ok)
        self.assertEqual(failure.error.code, "CLAIM_NOT_FOUND")

    def test_lookup_policy_returns_member_policy_and_remaining_limit(self) -> None:
        """The policy tool follows the member-to-policy relationship."""
        success = lookup_policy("M-2214")
        self.assertTrue(success.ok)
        self.assertEqual(success.data["policy_id"], "POL-3310")
        self.assertEqual(success.data["remaining_limit"], 9200)

        failure = lookup_policy("M-9999")
        self.assertFalse(failure.ok)
        self.assertEqual(failure.error.code, "MEMBER_NOT_FOUND")

    def test_check_coverage_returns_coverage_facts(self) -> None:
        """Coverage checks return facts and reject an unknown procedure."""
        claim = get_claim("CLM-8842").data
        procedure_code = claim["lines"][0]["code"]

        success = check_coverage(
            member_id="M-2214",
            procedure_code=procedure_code,
            attached_documents=claim["documents"],
        )
        self.assertTrue(success.ok)
        self.assertEqual(success.data["procedure_code"], procedure_code)
        self.assertIn("excluded", success.data)
        self.assertIn("document_present", success.data)

        failure = check_coverage("M-2214", "PROC-9999", [])
        self.assertFalse(failure.ok)
        self.assertEqual(failure.error.code, "NOT_FOUND")

    def test_check_coverage_reads_true_preauthorisation_flag(self) -> None:
        """Procedure 62480 is explicitly marked as requiring pre-authorisation."""
        result = check_coverage("M-2214", "62480", [])

        self.assertTrue(result.ok)
        self.assertTrue(result.data["requires_preauth"])

    def test_get_preauthorisation_returns_query_evidence(self) -> None:
        """Pre-authorisation queries return evidence without crashing the run."""
        claim = get_claim("CLM-8842").data
        procedure_code = claim["lines"][0]["code"]

        result = get_preauthorisation(
            member_id="M-2214",
            procedure_code=procedure_code,
            date_of_service=claim["date_of_service"],
        )
        self.assertTrue(result.ok)
        self.assertIn("found", result.data)
        self.assertIn("valid", result.data)

        not_found = get_preauthorisation(
            member_id="M-9999",
            procedure_code=procedure_code,
            date_of_service=claim["date_of_service"],
        )
        self.assertFalse(not_found.ok)
        self.assertEqual(not_found.error.code, "NOT_FOUND")

        invalid_date = get_preauthorisation("M-2214", procedure_code, "not-a-date")
        self.assertFalse(invalid_date.ok)
        self.assertEqual(invalid_date.error.code, "INVALID_ARGUMENT")

    def test_get_hospital_status_returns_network_facts(self) -> None:
        """The hospital tool returns panel status for the claim hospital."""
        claim = get_claim("CLM-8842").data

        success = get_hospital_status(claim["hospital_id"])
        self.assertTrue(success.ok)
        self.assertEqual(success.data["hospital_id"], claim["hospital_id"])
        self.assertIn("panel", success.data)

        failure = get_hospital_status("H-9999")
        self.assertFalse(failure.ok)
        self.assertEqual(failure.error.code, "HOSPITAL_NOT_FOUND")

    def test_check_duplicate_claim_returns_full_match_evidence(self) -> None:
        """A duplicate requires all four comparison facts to match."""
        duplicate_claim = get_claim("CLM-8933").data

        duplicate = check_duplicate_claim(
            member_id=duplicate_claim["member_id"],
            hospital_id=duplicate_claim["hospital_id"],
            date_of_service=duplicate_claim["date_of_service"],
            lines=duplicate_claim["lines"],
        )
        self.assertTrue(duplicate.ok)
        self.assertTrue(duplicate.data["duplicate"])
        self.assertEqual(duplicate.data["prior_claim_id"], "CLM-8710")
        self.assertEqual(
            duplicate.data["matched_fields"],
            ["member_id", "hospital_id", "date_of_service", "lines"],
        )

        near_miss_claim = get_claim("CLM-8850").data
        near_miss = check_duplicate_claim(
            member_id=near_miss_claim["member_id"],
            hospital_id=near_miss_claim["hospital_id"],
            date_of_service=near_miss_claim["date_of_service"],
            lines=near_miss_claim["lines"],
        )
        self.assertTrue(near_miss.ok)
        self.assertFalse(near_miss.data["duplicate"])

    def test_problem_a_registry_contains_the_seven_approved_tools(self) -> None:
        """The final registry exposes exactly the agreed Problem A tool set."""
        registry = build_problem_a_registry()
        tools = registry.as_mapping()

        expected_names = {
            "get_claim",
            "lookup_policy",
            "check_coverage",
            "get_preauthorisation",
            "get_hospital_status",
            "check_duplicate_claim",
            "issue_decision_letter",
        }

        self.assertEqual(set(tools), expected_names)
        self.assertEqual(set(TOOLS), expected_names)
        self.assertTrue(registry.get_spec("issue_decision_letter").irreversible)

    def test_public_tools_reject_invalid_arguments(self) -> None:
        """Every public tool should reject clearly invalid input safely."""
        results = [
            get_claim(""),
            lookup_policy(""),
            check_coverage("", "", "not-a-list"),
            get_preauthorisation("", "", "not-a-date"),
            get_hospital_status(""),
            check_duplicate_claim("", "", "", []),
            issue_decision_letter("", None, "act"),
        ]

        for result in results:
            self.assertFalse(result.ok)
            self.assertEqual(result.error.code, "INVALID_ARGUMENT")

    def test_confirm_mode_requires_trusted_operator_approval(self) -> None:
        """Confirm mode must fail closed before the local JSONL write."""
        decision = FinalDecision.from_dict({
            "decision": "approve_in_principle",
            "trigger": None,
            "missing": None,
            "escalate_to": None,
            "line_dispositions": [],
            "approved_total": 0,
            "refused_total": 0,
            "evidence": ["CLM-8842"],
        })

        result = issue_decision_letter(
            "CLM-8842",
            decision,
            "confirm",
            run_id="test-run",
            operator_approved=False,
        )

        self.assertTrue(result.ok)
        self.assertFalse(result.data["logged"])
        self.assertEqual(result.data["gate_result"], "CONFIRMATION_REQUIRED")

    def test_issue_decision_letter_rejects_unknown_autonomy(self) -> None:
        """Unexpected autonomy text must never reach the write path."""
        decision = FinalDecision.from_dict({
            "decision": "approve_in_principle",
            "trigger": None,
            "missing": None,
            "escalate_to": None,
            "line_dispositions": [],
            "approved_total": 0,
            "refused_total": 0,
            "evidence": ["CLM-8842"],
        })

        result = issue_decision_letter(
            "CLM-8842",
            decision,
            "unknown",
            run_id="test-run",
            operator_approved=True,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, "INVALID_ARGUMENT")

    def test_get_claim_response_has_documented_shape(self) -> None:
        """get_claim exposes only its documented claim fields."""
        result = get_claim("CLM-8842")

        self.assertTrue(result.ok)
        self.assertEqual(
            set(result.data),
            {
                "claim_id",
                "member_id",
                "hospital_id",
                "date_of_service",
                "narrative",
                "documents",
                "lines",
            },
        )

    def test_lookup_policy_response_has_documented_shape(self) -> None:
        """lookup_policy exposes only its documented policy fields."""
        result = lookup_policy("M-2214")

        self.assertTrue(result.ok)
        self.assertEqual(
            set(result.data),
            {
                "member_id",
                "policy_id",
                "product",
                "status",
                "start_date",
                "end_date",
                "annual_limit",
                "used_to_date",
                "remaining_limit",
                "exclusions",
            },
        )

    def test_check_coverage_response_has_documented_shape(self) -> None:
        """check_coverage exposes one fixed-shape coverage result."""
        claim = get_claim("CLM-8842").data
        procedure_code = claim["lines"][0]["code"]

        result = check_coverage(
            "M-2214",
            procedure_code,
            claim["documents"],
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            set(result.data),
            {
                "procedure_code",
                "description",
                "excluded",
                "exclusion_rule",
                "requires_preauth",
                "required_document",
                "document_present",
            },
        )

    def test_get_preauthorisation_response_has_documented_shape(self) -> None:
        """get_preauthorisation exposes one fixed-shape evidence result."""
        claim = get_claim("CLM-8842").data
        procedure_code = claim["lines"][0]["code"]

        result = get_preauthorisation(
            "M-2214",
            procedure_code,
            claim["date_of_service"],
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            set(result.data),
            {
                "found",
                "preauth_id",
                "valid",
                "valid_from",
                "valid_to",
            },
        )

    def test_get_hospital_status_response_has_documented_shape(self) -> None:
        """get_hospital_status exposes only documented hospital fields."""
        claim = get_claim("CLM-8842").data
        result = get_hospital_status(claim["hospital_id"])

        self.assertTrue(result.ok)
        self.assertEqual(
            set(result.data),
            {"hospital_id", "name", "panel", "country"},
        )

    def test_check_duplicate_claim_response_has_documented_shape(self) -> None:
        """check_duplicate_claim exposes one fixed-shape duplicate result."""
        claim = get_claim("CLM-8933").data

        result = check_duplicate_claim(
            claim["member_id"],
            claim["hospital_id"],
            claim["date_of_service"],
            claim["lines"],
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            set(result.data),
            {"duplicate", "prior_claim_id", "matched_fields"},
        )

    def test_issue_decision_letter_response_has_documented_shape(self) -> None:
        """The gated write tool exposes a fixed-shape blocked result."""
        decision = FinalDecision.from_dict(
            {
                "decision": "approve_in_principle",
                "trigger": None,
                "missing": None,
                "escalate_to": None,
                "line_dispositions": [],
                "approved_total": 0,
                "refused_total": 0,
                "evidence": [],
            }
        )

        result = issue_decision_letter(
            case_id="CLM-8842",
            decision_record=decision,
            autonomy="suggest",
            run_id="shape-test",
            operator_approved=False,
        )

        self.assertTrue(result.ok)
        self.assertEqual(
            set(result.data),
            {"logged", "log_id", "gate_result"},
        )
