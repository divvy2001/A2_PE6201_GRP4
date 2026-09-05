"""Problem A tool implementations for the agent."""

from __future__ import annotations

from src.schemas import ErrorDetail, ToolResult
from datetime import date
import json
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path

from src.schemas import ErrorDetail, FinalDecision, ToolResult
from src.tools.base import ToolSpec
from src.tools.registry import ToolRegistry
from src.tools.data_store import (
    DataStoreError,
    get_claim_by_id,
    get_member_by_id,
    get_policy_by_id,
    get_procedure_by_code,
    get_required_document_for_procedure,
    get_preauthorisation_candidates,
    get_hospital_by_id,
    find_duplicate_claim,
)


def get_claim(case_id: str) -> ToolResult:
    """Return the claim facts for one claim ID."""
    if not isinstance(case_id, str) or not case_id.strip():
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="INVALID_ARGUMENT",
                message="case_id must be a non-empty string",
            ),
        )

    try:
        claim = get_claim_by_id(case_id)
    except DataStoreError:
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="CLAIM_NOT_FOUND",
                message=f"No claim found for {case_id}",
            ),
        )

    return ToolResult(ok=True, data=claim)

def lookup_policy(member_id: str) -> ToolResult:
    """Return the policy facts linked to one member ID."""
    if not isinstance(member_id, str) or not member_id.strip():
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="INVALID_ARGUMENT",
                message="member_id must be a non-empty string",
            ),
        )

    try:
        member = get_member_by_id(member_id)
    except DataStoreError:
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="MEMBER_NOT_FOUND",
                message=f"No member found for {member_id}",
            ),
        )

    try:
        policy = get_policy_by_id(member["policy_id"])
    except DataStoreError:
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="POLICY_NOT_FOUND",
                message=f"No policy found for member {member_id}",
            ),
        )

    data = {"member_id": member_id, **policy}
    data["remaining_limit"] = data["annual_limit"] - data["used_to_date"]
    return ToolResult(ok=True, data=data)

def check_coverage(
    member_id: str,
    procedure_code: str,
    attached_documents: list[str],
) -> ToolResult:
    """Check coverage, exclusions, and document requirements for one procedure."""
    if (
        not isinstance(member_id, str)
        or not member_id.strip()
        or not isinstance(procedure_code, str)
        or not procedure_code.strip()
        or not isinstance(attached_documents, list)
    ):
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="INVALID_ARGUMENT",
                message="member_id, procedure_code, and attached_documents are invalid",
            ),
        )

    try:
        member = get_member_by_id(member_id)
        policy = get_policy_by_id(member["policy_id"])
        procedure = get_procedure_by_code(procedure_code)
        required_document = get_required_document_for_procedure(procedure_code)
    except DataStoreError:
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="NOT_FOUND",
                message=f"Member or procedure was not found: {member_id}, {procedure_code}",
            ),
        )

    exclusion = next(
        (
            item
            for item in policy.get("exclusions", [])
            if item["code"] == procedure_code
        ),
        None,
    )
    excluded = exclusion is not None
    requires_preauth = bool(procedure.get("requires_preauthorisation", False))
    document_present = (
        required_document is None or required_document in attached_documents
    )

    return ToolResult(
        ok=True,
        data={
            "procedure_code": procedure_code,
            "description": procedure["description"],
            "excluded": excluded,
            "exclusion_rule": exclusion["rule"] if exclusion else None,
            "requires_preauth": requires_preauth,
            "required_document": required_document,
            "document_present": document_present,
        },
    )

def get_preauthorisation(
    member_id: str,
    procedure_code: str,
    date_of_service: str,
) -> ToolResult:
    """Return pre-authorisation evidence for a procedure on a service date."""
    if (
        not isinstance(member_id, str)
        or not member_id.strip()
        or not isinstance(procedure_code, str)
        or not procedure_code.strip()
    ):
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="INVALID_ARGUMENT",
                message="member_id and procedure_code must be non-empty strings",
            ),
        )

    try:
        service_date = date.fromisoformat(date_of_service)
    except (TypeError, ValueError):
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="INVALID_ARGUMENT",
                message="date_of_service must use YYYY-MM-DD format",
            ),
        )

    try:
        get_member_by_id(member_id)
        get_procedure_by_code(procedure_code)
        candidates = get_preauthorisation_candidates(member_id, procedure_code)
    except DataStoreError:
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="NOT_FOUND",
                message=f"Member or procedure was not found: {member_id}, {procedure_code}",
            ),
        )

    if not candidates:
        return ToolResult(
            ok=True,
            data={
                "found": False,
                "preauth_id": None,
                "valid": False,
                "valid_from": None,
                "valid_to": None,
            },
        )

    preauth = candidates[0]
    valid_from = date.fromisoformat(preauth["valid_from"])
    valid_to = date.fromisoformat(preauth["valid_to"])
    valid = valid_from <= service_date <= valid_to

    return ToolResult(
        ok=True,
        data={
            "found": True,
            "preauth_id": preauth["preauth_id"],
            "valid": valid,
            "valid_from": preauth["valid_from"],
            "valid_to": preauth["valid_to"],
        },
    )

def get_hospital_status(hospital_id: str) -> ToolResult:
    """Return the network status and basic facts for one hospital."""
    if not isinstance(hospital_id, str) or not hospital_id.strip():
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="INVALID_ARGUMENT",
                message="hospital_id must be a non-empty string",
            ),
        )

    try:
        hospital = get_hospital_by_id(hospital_id)
    except DataStoreError:
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="HOSPITAL_NOT_FOUND",
                message=f"No hospital found for {hospital_id}",
            ),
        )

    return ToolResult(
        ok=True,
        data={
            "hospital_id": hospital["hospital_id"],
            "name": hospital["name"],
            "panel": hospital["panel"],
            "country": hospital["country"],
        },
    )

def check_duplicate_claim(
    member_id: str,
    hospital_id: str,
    date_of_service: str,
    lines: list[dict],
) -> ToolResult:
    """Check whether all claim facts match an earlier claim."""
    if (
        not isinstance(member_id, str)
        or not member_id.strip()
        or not isinstance(hospital_id, str)
        or not hospital_id.strip()
        or not isinstance(date_of_service, str)
        or not isinstance(lines, list)
    ):
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="INVALID_ARGUMENT",
                message="member_id, hospital_id, date_of_service, and lines are invalid",
            ),
        )

    try:
        prior_claim = find_duplicate_claim(
            member_id,
            hospital_id,
            date_of_service,
            lines,
        )
    except DataStoreError as error:
        return ToolResult(
            ok=False,
            error=ErrorDetail(code="INVALID_ARGUMENT", message=str(error)),
        )

    if prior_claim is None:
        return ToolResult(
            ok=True,
            data={
                "duplicate": False,
                "prior_claim_id": None,
                "matched_fields": [],
            },
        )

    return ToolResult(
        ok=True,
        data={
            "duplicate": True,
            "prior_claim_id": prior_claim["claim_id"],
            "matched_fields": [
                "member_id",
                "hospital_id",
                "date_of_service",
                "lines",
            ],
        },
    )


def issue_decision_letter(
    case_id: str,
    decision_record: FinalDecision,
    autonomy: str,
    *,
    run_id: str | None = None,
) -> ToolResult:
    """Write one gated local decision record for the demonstration only."""
    if not isinstance(case_id, str) or not case_id.strip():
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="INVALID_ARGUMENT",
                message="case_id must be a non-empty string",
            ),
        )

    if not isinstance(decision_record, FinalDecision):
        return ToolResult(
            ok=False,
            error=ErrorDetail(
                code="INVALID_ARGUMENT",
                message="decision_record must be a FinalDecision",
            ),
        )

    if autonomy == "suggest":
        return ToolResult(
            ok=True,
            data={
                "logged": False,
                "log_id": None,
                "gate_result": "AUTONOMY_BLOCKED",
            },
        )

    if decision_record.missing:
        return ToolResult(
            ok=True,
            data={
                "logged": False,
                "log_id": None,
                "gate_result": "FACTS_INCOMPLETE",
            },
        )

    if run_id is None:
        return ToolResult(
            ok=True,
            data={
                "logged": False,
                "log_id": None,
                "gate_result": "RUN_ID_REQUIRED",
            },
        )

    log_id = f"DEC-{case_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    log_path = Path(__file__).resolve().parents[2] / "outputs" / "decision_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "log_id": log_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "case_id": case_id,
        "autonomy": autonomy,
        "decision_record": asdict(decision_record),
    }

    with log_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")

    return ToolResult(
        ok=True,
        data={
            "logged": True,
            "log_id": log_id,
            "gate_result": "LOGGED",
        },
    )


def build_problem_a_registry() -> ToolRegistry:
    """Create the registry containing the seven approved Problem A tools."""
    registry = ToolRegistry()

    registry.register(
        ToolSpec(
            name="get_claim",
            signature="get_claim(case_id: str)",
            what="Retrieve one claim and its line items.",
            input_contract="case_id: non-empty string",
            return_contract="Claim facts or CLAIM_NOT_FOUND.",
            fails_when=("INVALID_ARGUMENT", "CLAIM_NOT_FOUND"),
            irreversible=False,
        ),
        get_claim,
    )
    registry.register(
        ToolSpec(
            name="lookup_policy",
            signature="lookup_policy(member_id: str)",
            what="Retrieve the member's linked policy and remaining limit.",
            input_contract="member_id: non-empty string",
            return_contract="Policy facts or member/policy lookup failure.",
            fails_when=("INVALID_ARGUMENT", "MEMBER_NOT_FOUND", "POLICY_NOT_FOUND"),
            irreversible=False,
        ),
        lookup_policy,
    )
    registry.register(
        ToolSpec(
            name="check_coverage",
            signature="check_coverage(member_id: str, procedure_code: str, attached_documents: list[str])",
            what="Check exclusions, pre-authorisation, and documents.",
            input_contract="Valid member ID, procedure code, and document list.",
            return_contract="Coverage facts or NOT_FOUND.",
            fails_when=("INVALID_ARGUMENT", "NOT_FOUND"),
            irreversible=False,
        ),
        check_coverage,
    )
    registry.register(
        ToolSpec(
            name="get_preauthorisation",
            signature="get_preauthorisation(member_id: str, procedure_code: str, date_of_service: str)",
            what="Retrieve pre-authorisation evidence and date validity.",
            input_contract="Valid member ID, procedure code, and YYYY-MM-DD date.",
            return_contract="Pre-authorisation evidence or failure.",
            fails_when=("INVALID_ARGUMENT", "NOT_FOUND"),
            irreversible=False,
        ),
        get_preauthorisation,
    )
    registry.register(
        ToolSpec(
            name="get_hospital_status",
            signature="get_hospital_status(hospital_id: str)",
            what="Retrieve hospital panel-network status.",
            input_contract="hospital_id: non-empty string",
            return_contract="Hospital facts or HOSPITAL_NOT_FOUND.",
            fails_when=("INVALID_ARGUMENT", "HOSPITAL_NOT_FOUND"),
            irreversible=False,
        ),
        get_hospital_status,
    )
    registry.register(
        ToolSpec(
            name="check_duplicate_claim",
            signature="check_duplicate_claim(member_id: str, hospital_id: str, date_of_service: str, lines: list[dict])",
            what="Compare all four duplicate-claim facts against prior claims.",
            input_contract="Member, hospital, service date, and complete lines.",
            return_contract="Duplicate evidence.",
            fails_when=("INVALID_ARGUMENT",),
            irreversible=False,
        ),
        check_duplicate_claim,
    )
    registry.register(
        ToolSpec(
            name="issue_decision_letter",
            signature="issue_decision_letter(case_id: str, decision_record: FinalDecision, autonomy: str)",
            what="Write one gated local demonstration decision record.",
            input_contract="Complete FinalDecision and trusted autonomy setting.",
            return_contract="Local logging result only; no real-world action.",
            fails_when=("INVALID_ARGUMENT",),
            irreversible=True,
        ),
        issue_decision_letter,
    )

    return registry

TOOLS = build_problem_a_registry().as_mapping()