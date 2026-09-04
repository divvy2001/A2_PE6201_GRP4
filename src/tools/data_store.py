from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "reference_data" / "data_A"


class DataStoreError(Exception):
    """Raised when reference data cannot be loaded safely."""


def load_json(filename: str) -> list[dict[str, Any]]:
    """Load one Problem A JSON table from the local reference-data folder."""
    path = DATA_DIR / filename

    if not path.exists():
        raise DataStoreError(f"DATA_FILE_NOT_FOUND: {filename}")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise DataStoreError(f"INVALID_JSON: {filename}") from error

    if not isinstance(data, list):
        raise DataStoreError(f"INVALID_DATA_SHAPE: {filename} must contain a list")

    return data

def find_duplicate_claim(
    member_id: str,
    hospital_id: str,
    date_of_service: str,
    lines: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return a prior claim only when all four duplicate fields match."""
    for field_name, value in {
        "member_id": member_id,
        "hospital_id": hospital_id,
        "date_of_service": date_of_service,
    }.items():
        if not isinstance(value, str) or not value.strip():
            raise DataStoreError(
                f"INVALID_ARGUMENT: {field_name} must be a non-empty string"
            )

    target_lines = _normalise_lines(lines)

    for prior_claim in load_json("decided_claims.json"):
        # All four fields must match; partial matches are deliberate near-misses.
        is_same_episode = (
            prior_claim.get("member_id") == member_id
            and prior_claim.get("hospital_id") == hospital_id
            and prior_claim.get("date_of_service") == date_of_service
            and _normalise_lines(prior_claim.get("lines", [])) == target_lines
        )

        if is_same_episode:
            return prior_claim

    return None

def _normalise_lines(lines: list[dict[str, Any]]) -> tuple[tuple[str, int | float], ...]:
    """Create an order-independent representation of claim line items."""
    if not isinstance(lines, list) or not lines:
        raise DataStoreError("INVALID_ARGUMENT: lines must be a non-empty list")

    normalised_lines: list[tuple[str, int | float]] = []

    for line in lines:
        if not isinstance(line, dict):
            raise DataStoreError("INVALID_ARGUMENT: every line must be an object")

        code = line.get("code")
        amount = line.get("amount")

        if not isinstance(code, str) or not code.strip():
            raise DataStoreError("INVALID_ARGUMENT: every line needs a procedure code")

        if not isinstance(amount, (int, float)):
            raise DataStoreError("INVALID_ARGUMENT: every line needs a numeric amount")

        normalised_lines.append((code, amount))

    return tuple(sorted(normalised_lines))

def get_preauthorisation_candidates(
    member_id: str, procedure_code: str
) -> list[dict[str, Any]]:
    """Return pre-authorisation records matching one member and procedure."""
    if not isinstance(member_id, str) or not member_id.strip():
        raise DataStoreError("INVALID_ARGUMENT: member_id must be a non-empty string")

    if not isinstance(procedure_code, str) or not procedure_code.strip():
        raise DataStoreError(
            "INVALID_ARGUMENT: procedure_code must be a non-empty string"
        )

    return [
        record
        for record in load_json("preauthorisations.json")
        if record.get("member_id") == member_id
        and record.get("procedure_code") == procedure_code
    ]

def get_required_document_for_procedure(procedure_code: str) -> str | None:
    """Return the required document for a procedure, if one is required."""
    if not isinstance(procedure_code, str) or not procedure_code.strip():
        raise DataStoreError(
            "INVALID_ARGUMENT: procedure_code must be a non-empty string"
        )

    for requirement in load_json("required_documents.json"):
        if requirement.get("procedure_code") == procedure_code:
            return requirement.get("document")

    return None

def get_procedure_by_code(procedure_code: str) -> dict[str, Any]:
    """Return one procedure by procedure code."""
    if not isinstance(procedure_code, str) or not procedure_code.strip():
        raise DataStoreError(
            "INVALID_ARGUMENT: procedure_code must be a non-empty string"
        )

    for procedure in load_json("procedures.json"):
        if procedure.get("code") == procedure_code:
            return procedure

    raise DataStoreError(f"PROCEDURE_NOT_FOUND: {procedure_code}")

def get_hospital_by_id(hospital_id: str) -> dict[str, Any]:
    """Return one hospital by hospital_id."""
    if not isinstance(hospital_id, str) or not hospital_id.strip():
        raise DataStoreError("INVALID_ARGUMENT: hospital_id must be a non-empty string")

    for hospital in load_json("hospitals.json"):
        if hospital.get("hospital_id") == hospital_id:
            return hospital

    raise DataStoreError(f"HOSPITAL_NOT_FOUND: {hospital_id}")

def get_policy_by_id(policy_id: str) -> dict[str, Any]:
    """Return one policy by policy_id."""
    if not isinstance(policy_id, str) or not policy_id.strip():
        raise DataStoreError("INVALID_ARGUMENT: policy_id must be a non-empty string")

    for policy in load_json("policies.json"):
        if policy.get("policy_id") == policy_id:
            return policy

    raise DataStoreError(f"POLICY_NOT_FOUND: {policy_id}")

def get_member_by_id(member_id: str) -> dict[str, Any]:
    """Return one member by member_id."""
    if not isinstance(member_id, str) or not member_id.strip():
        raise DataStoreError("INVALID_ARGUMENT: member_id must be a non-empty string")

    for member in load_json("members.json"):
        if member.get("member_id") == member_id:
            return member

    raise DataStoreError(f"MEMBER_NOT_FOUND: {member_id}")

def get_claim_by_id(claim_id: str) -> dict[str, Any]:
    """Return one claim by its claim_id."""
    if not isinstance(claim_id, str) or not claim_id.strip():
        raise DataStoreError("INVALID_ARGUMENT: claim_id must be a non-empty string")

    for claim in load_json("claims.json"):
        if claim.get("claim_id") == claim_id:
            return claim

    raise DataStoreError(f"CLAIM_NOT_FOUND: {claim_id}")

if __name__ == "__main__":
    # Smoke test: follow claim data and inspect its first procedure.
    claim = get_claim_by_id("CLM-8842")
    member = get_member_by_id(claim["member_id"])
    policy = get_policy_by_id(member["policy_id"])
    hospital = get_hospital_by_id(claim["hospital_id"])

    first_line = claim["lines"][0]
    procedure = get_procedure_by_code(first_line["code"])
    required_document = get_required_document_for_procedure(first_line["code"])
    # Find the line that requires pre-authorisation, if any.
    preauth_line = next(
        line
        for line in claim["lines"]
        if get_procedure_by_code(line["code"])["requires_preauth"]
    )

    preauth_candidates = get_preauthorisation_candidates(
        member["member_id"],
        preauth_line["code"],
    )
    remaining_limit = policy["annual_limit"] - policy["used_to_date"]

    # CLM-8933 is the shipped true-duplicate example.
    duplicate_case = get_claim_by_id("CLM-8933")
    duplicate_prior = find_duplicate_claim(
        duplicate_case["member_id"],
        duplicate_case["hospital_id"],
        duplicate_case["date_of_service"],
        duplicate_case["lines"],
    )

    print(f"Found claim: {claim['claim_id']}")
    print(f"Member: {member['member_id']}")
    print(f"Policy status: {policy['status']}")
    print(f"Remaining annual limit: {remaining_limit}")
    print(f"Hospital: {hospital['name']}")
    print(f"Panel hospital: {hospital['panel']}")
    print(f"Procedure: {procedure['description']}")
    print(f"Requires pre-authorisation: {procedure['requires_preauth']}")
    print(f"Required document: {required_document or 'None'}")
    print(f"Pre-authorisation candidates: {len(preauth_candidates)}")
    print(f"Duplicate prior claim: "
        f"{duplicate_prior['claim_id'] if duplicate_prior else 'None'}"
    )