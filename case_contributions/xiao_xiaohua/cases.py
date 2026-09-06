"""Problem A evaluation-case additions owned by XIAO XIAOHUA."""

from __future__ import annotations

EXTRA_CLAIMS = [
    # CLM-9011 — Ordinary short run: one covered consultation.
    {
        "claim_id": "CLM-9011",
        "member_id": "M-5502",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-01",
        "narrative": "Routine outpatient consultation after a minor fall.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "99213", "amount": 180},
        ],
    },
    # CLM-9012 — Multi-line run: four covered lines and a required document present.
    {
        "claim_id": "CLM-9012",
        "member_id": "M-5502",
        "hospital_id": "H-114",
        "date_of_service": "2026-10-02",
        "narrative": "Consultation and follow-up diagnostic tests after a fall.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "99213", "amount": 180},
            {"code": "80053", "amount": 90},
            {"code": "70553", "amount": 620},
            {"code": "45378", "amount": 1100},
        ],
    },
    # CLM-9013 — Missing-document case: 45378 requires itemised_bill.
    {
        "claim_id": "CLM-9013",
        "member_id": "M-5502",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-03",
        "narrative": "Day colonoscopy procedure; no supporting invoice was attached.",
        "documents": [],
        "lines": [
            {"code": "45378", "amount": 1150},
        ],
    },
    # CLM-9014 — Expired pre-authorisation: PA-5640 ended before service.
    {
        "claim_id": "CLM-9014",
        "member_id": "M-6118",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-04",
        "narrative": "Knee arthroscopy after an earlier approval had expired.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "29881", "amount": 1950},
        ],
    },
    # CLM-9015 — Second true duplicate: matches the new decided history record.
    {
        "claim_id": "CLM-9015",
        "member_id": "M-5502",
        "hospital_id": "H-114",
        "date_of_service": "2026-10-05",
        "narrative": "Resubmission of a consultation claim already decided.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "99213", "amount": 200},
        ],
    },
]
EXTRA_DECIDED = [
    # Historical record matched by CLM-9015 on member, hospital, date, and lines.
    {
        "claim_id": "CLM-8715",
        "member_id": "M-5502",
        "hospital_id": "H-114",
        "date_of_service": "2026-10-05",
        "lines": [
            {"code": "99213", "amount": 200},
        ],
        "decision": "approve_in_principle",
        "decided_on": "2026-10-06",
    },
]