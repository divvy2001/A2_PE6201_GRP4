**Status:** Draft - to be aligned with `schemas.py`

## Shared ToolResult format

### Success

~~~json
{
  "ok": true,
  "data": {},
  "error": null
}
~~~

### Failure

~~~json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "CLAIM_NOT_FOUND",
    "message": "No claim found for CLM-9999"
  }
}
~~~

### Seven tool contracts

get_claim(case_id: str) -> ToolResult[data={
  claim_id, member_id, hospital_id, date_of_service,
  narrative, documents: list[str],
  lines: list[{code: str, amount: number}]
}]

lookup_policy(member_id: str) -> ToolResult[data={
  member_id, policy_id, product, status, start_date, end_date,
  annual_limit, used_to_date, remaining_limit,
  exclusions: list[{code, rule}]
}]

check_coverage(
  member_id: str, procedure_code: str, attached_documents: list[str]
) -> ToolResult[data={
  procedure_code, description, excluded: bool, exclusion_rule: str|null,
  requires_preauth: bool, required_document: str|null,
  document_present: bool
}]

get_preauthorisation(
  member_id: str, procedure_code: str, date_of_service: str
) -> ToolResult[data={
  found: bool, preauth_id: str|null, valid: bool,
  valid_from: str|null, valid_to: str|null
}]

get_hospital_status(hospital_id: str) -> ToolResult[data={
  hospital_id, name, panel: bool, country
}]

check_duplicate_claim(
  member_id: str, hospital_id: str, date_of_service: str,
  lines: list[{code: str, amount: number}]
) -> ToolResult[data={
  duplicate: bool, prior_claim_id: str|null,
  matched_fields: list[str]
}]
issue_decision_letter(
  case_id: str, decision_record: FinalDecision, autonomy: str
) -> ToolResult[data={
  logged: bool, log_id: str|null, gate_result: str
}]

# 仅在 logged=true 时 append 到 outputs/decision_log.jsonl：
{
  log_id, timestamp_utc, run_id, case_id, autonomy, decision_record
}

## Implementation rules and invariants

check_coverage must first resolve the member's policy and then check policy exclusions. An unknown procedure or member must return `NOT_FOUND`, not `excluded=false`.

No pre-authorisation record is still a successful query: return `ok=true` and `found=false`. If a record exists but is not valid for the date of service, return `valid=false` and retain the validity-window evidence.

For duplicate detection, normalise line items by sorting `(code, amount)` pairs first. Set `duplicate=true` only when member, hospital, date of service, and the complete set of line items all match.

issue_decision_letter` is the only write tool. It writes only a local JSONL record for demonstration purposes; it must not send an email or call a real insurance system, and it must not execute before all required facts have been established.