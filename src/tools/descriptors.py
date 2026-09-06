"""Versioned tool descriptors owned by Miao Jiaxuan."""

from __future__ import annotations

from src.tools.base import ToolSpec


TOOL_ORDER = (
    "get_claim",
    "lookup_policy",
    "check_coverage",
    "get_preauthorisation",
    "get_hospital_status",
    "check_duplicate_claim",
    "issue_decision_letter",
)


_SHARED_SPECS = {
    "get_claim": ToolSpec(
        name="get_claim",
        signature="get_claim(case_id: str)",
        what="Retrieve the facts for one claim. This is the starting tool for every run.",
        input_contract="case_id must be one non-empty claim ID string.",
        return_contract=(
            "ToolResult. On success, data contains exactly one claim with "
            "claim_id, member_id, hospital_id, date_of_service, narrative, "
            "complete documents, and complete lines. No full reference table "
            "is returned."
        ),
        fails_when=("INVALID_ARGUMENT", "CLAIM_NOT_FOUND"),
        irreversible=False,
    ),
    "lookup_policy": ToolSpec(
        name="lookup_policy",
        signature="lookup_policy(member_id: str)",
        what=(
            "Retrieve the policy linked to one member and calculate the "
            "remaining annual limit."
        ),
        input_contract="member_id must be one non-empty member ID string.",
        return_contract=(
            "ToolResult. On success, data contains exactly one member-policy "
            "result with member_id, policy_id, product, status, start_date, "
            "end_date, annual_limit, used_to_date, remaining_limit, and the "
            "complete exclusions list."
        ),
        fails_when=(
            "INVALID_ARGUMENT",
            "MEMBER_NOT_FOUND",
            "POLICY_NOT_FOUND",
        ),
        irreversible=False,
    ),
    "check_coverage": ToolSpec(
        name="check_coverage",
        signature=(
            "check_coverage(member_id: str, procedure_code: str, "
            "attached_documents: list[str])"
        ),
        what=(
            "Check one procedure for policy exclusion, pre-authorisation "
            "requirement, and required-document presence."
        ),
        input_contract=(
            "member_id and procedure_code must be non-empty strings; "
            "attached_documents must be the claim's complete document list."
        ),
        return_contract=(
            "ToolResult. On success, data is one fixed-shape result containing "
            "procedure_code, description, excluded, exclusion_rule, "
            "requires_preauth, required_document, and document_present."
        ),
        fails_when=("INVALID_ARGUMENT", "NOT_FOUND"),
        irreversible=False,
    ),
    "get_hospital_status": ToolSpec(
        name="get_hospital_status",
        signature="get_hospital_status(hospital_id: str)",
        what="Retrieve panel-network status for one hospital.",
        input_contract="hospital_id must be one non-empty hospital ID string.",
        return_contract=(
            "ToolResult. On success, data contains exactly one hospital with "
            "hospital_id, name, panel, and country."
        ),
        fails_when=("INVALID_ARGUMENT", "HOSPITAL_NOT_FOUND"),
        irreversible=False,
    ),
    "check_duplicate_claim": ToolSpec(
        name="check_duplicate_claim",
        signature=(
            "check_duplicate_claim(member_id: str, hospital_id: str, "
            "date_of_service: str, lines: list[dict])"
        ),
        what=(
            "Check whether member, hospital, service date, and the complete "
            "line-item set all match an earlier decided claim."
        ),
        input_contract=(
            "member_id and hospital_id are non-empty strings; date_of_service "
            "uses YYYY-MM-DD; lines is the complete claim line list."
        ),
        return_contract=(
            "ToolResult. On success, data contains duplicate, prior_claim_id, "
            "and matched_fields. At most one prior_claim_id is returned."
        ),
        fails_when=("INVALID_ARGUMENT",),
        irreversible=False,
    ),
    "issue_decision_letter": ToolSpec(
        name="issue_decision_letter",
        signature=(
            "issue_decision_letter(case_id: str, "
            "decision_record: FinalDecision, autonomy: str)"
        ),
        what=(
            "Append at most one gated decision record to a local JSONL file. "
            "It does not contact a real member or insurance system."
        ),
        input_contract=(
            "case_id is non-empty; decision_record follows FinalDecision; "
            "autonomy is supplied and enforced by the trusted runtime."
        ),
        return_contract=(
            "ToolResult. Data contains logged, log_id, and gate_result. "
            "AUTONOMY_BLOCKED, CONFIRMATION_REQUIRED, FACTS_INCOMPLETE, and "
            "RUN_ID_REQUIRED are safe non-writing outcomes."
        ),
        fails_when=("INVALID_ARGUMENT",),
        irreversible=True,
    ),
}


# v1 is deliberately harder for the model:
# it receives a list and must infer date validity itself.
V1_PREAUTHORISATION_SPEC = ToolSpec(
    name="get_preauthorisation",
    signature=(
        "get_preauthorisation(member_id: str, procedure_code: str, "
        "date_of_service: str)"
    ),
    what="Look up a possibly relevant pre-authorisation record.",
    input_contract=(
        "member_id and procedure_code are non-empty strings; "
        "date_of_service uses YYYY-MM-DD."
    ),
    return_contract=(
        "ToolResult. On success, data contains records: a list of zero or one "
        "object with preauth_id, valid_from, and valid_to. The model must work "
        "out whether a record exists and whether the service date is valid."
    ),
    fails_when=("INVALID_ARGUMENT", "NOT_FOUND"),
    irreversible=False,
)


# v2 makes the important decision facts explicit.
V2_PREAUTHORISATION_SPEC = ToolSpec(
    name="get_preauthorisation",
    signature=(
        "get_preauthorisation(member_id: str, procedure_code: str, "
        "date_of_service: str)"
    ),
    what=(
        "Return whether a relevant pre-authorisation exists and whether it "
        "is valid on the service date."
    ),
    input_contract=(
        "member_id and procedure_code are non-empty strings; "
        "date_of_service uses YYYY-MM-DD."
    ),
    return_contract=(
        "ToolResult. On success, data is one fixed-shape object containing "
        "found, preauth_id, valid, valid_from, and valid_to. At most one "
        "relevant record is exposed."
    ),
    fails_when=("INVALID_ARGUMENT", "NOT_FOUND"),
    irreversible=False,
)


def _build_version(preauthorisation_spec: ToolSpec) -> dict[str, ToolSpec]:
    specs = dict(_SHARED_SPECS)
    specs["get_preauthorisation"] = preauthorisation_spec
    return {name: specs[name] for name in TOOL_ORDER}


V1_TOOL_SPECS = _build_version(V1_PREAUTHORISATION_SPEC)
V2_TOOL_SPECS = _build_version(V2_PREAUTHORISATION_SPEC)


def get_tool_specs(version: str = "v2") -> dict[str, ToolSpec]:
    """Return the seven descriptors for one prompt version."""
    if version == "v1":
        return dict(V1_TOOL_SPECS)
    if version == "v2":
        return dict(V2_TOOL_SPECS)
    raise ValueError("version must be 'v1' or 'v2'")


def render_tool_specs(version: str = "v2") -> str:
    """Convert descriptors into readable text for a model prompt."""
    sections = []

    for spec in get_tool_specs(version).values():
        sections.append(
            "\n".join(
                [
                    f"Name: {spec.name}",
                    f"Signature: {spec.signature}",
                    f"What: {spec.what}",
                    f"Input: {spec.input_contract}",
                    f"Returns: {spec.return_contract}",
                    f"Fails when: {', '.join(spec.fails_when)}",
                    f"Irreversible: {spec.irreversible}",
                ]
            )
        )

    return "\n\n".join(sections)
