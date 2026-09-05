# D2(a) Tool Selection and Rationale

**Owner:** XIAO XIAOHUA  
**Status:** Draft

## Design principle

We use the shortest defensible tool set. A tool is retained only when a
specific task fails without it, it is distinguishable from neighbouring tools,
and its prompt, cost, and safety overhead are justified.

## Final tool set

| Tool | What fails without it? | Confusable with another tool? | Cost or risk when never called | Decision |
|---|---|---|---|---|
| `get_claim` | No case facts: member, hospital, date, documents, or lines. | No; it is the only case entry point. | Prompt tokens on every turn; justified because every run starts here. | Retain |
| `lookup_policy` | Cannot verify policy status, dates, annual-limit headroom, or exclusions. | No; it combines the member-to-policy bridge and policy facts. | Prompt tokens on every turn; justified because it enables early exit for lapsed or invalid policies. | Retain |
| `check_coverage` | Cannot resolve each line's exclusion, pre-authorisation requirement, or required document. | Low; procedure and document checks are deliberately merged here to avoid sibling tools. | Reused for each line and adds prompt tokens; necessary because line-level decisions vary by procedure. | Retain |
| `get_preauthorisation` | Cannot verify a required pre-authorisation or whether it was valid on the service date. | No; it is only used after `check_coverage` identifies a pre-authorisation requirement. | Prompt tokens on every turn, but calls occur only for the conditional branch that needs evidence. | Retain |
| `get_hospital_status` | Cannot establish panel status or record the treatment location. | No; it is the only source of hospital network facts. | Prompt tokens on every turn; a small, bounded response prevents an unsupported approval. | Retain |
| `check_duplicate_claim` | Cannot detect a resubmitted claim that has a new claim ID but the same episode facts. | No; it performs a distinct four-field historical comparison. | Prompt tokens on every turn; justified because a false repeat decision is a high-risk error. | Retain |
| `issue_decision_letter` | Cannot complete the required gated action or produce the auditable decision record. | No; it is the only write tool. | Adds prompt and safety cost; retained as the single gated, local JSONL write with no real-world action. | Retain |


## Tools intentionally not added or merged

| Candidate tool | Decision | Rationale |
|---|---|---|
| `lookup_member` | Not exposed | It only bridges a member to a policy; this lookup is merged into `lookup_policy`. |
| `lookup_procedure` | Not exposed | Procedure facts are returned by `check_coverage`, avoiding an extra sibling tool. |
| `check_required_documents` | Not exposed | Required-document and document-presence checks are merged into `check_coverage`. |
| `web_search` | Not added | All required facts are in local fixture data; web access would reduce reproducibility without solving a required task. |