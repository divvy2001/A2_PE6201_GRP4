"""Five Problem A evaluation cases contributed by Li Zihao."""

from __future__ import annotations


EXTRA_PROCEDURES = []
EXTRA_HOSPITALS = []
EXTRA_POLICIES = []
EXTRA_MEMBERS = []
EXTRA_PREAUTHORISATIONS = []


EXTRA_CLAIMS = [
    # CLM-9041 — The payable total is exactly equal to the policy remainder.
    {
        "claim_id": "CLM-9041",
        "member_id": "M-3390",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-21",
        "narrative": "Outpatient consultation and diagnostic testing.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "99213", "amount": 180},
            {"code": "80053", "amount": 90},
            {"code": "70553", "amount": 330},
        ],
    },
    # CLM-9042 — Two excluded lines and one covered line in one decision.
    {
        "claim_id": "CLM-9042",
        "member_id": "M-2214",
        "hospital_id": "H-114",
        "date_of_service": "2026-10-22",
        "narrative": "MRI investigation with two cosmetic procedures during the same visit.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "70553", "amount": 500},
            {"code": "31255", "amount": 250},
            {"code": "15823", "amount": 400},
        ],
    },
    # CLM-9043 — A pre-authorisation exists for the procedure and date, but it
    # belongs to another member (PA-5521 belongs to M-2214, not M-5502).
    {
        "claim_id": "CLM-9043",
        "member_id": "M-5502",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-23",
        "narrative": "Lumbar spinal fusion following persistent back pain.",
        "documents": ["itemised_bill", "discharge_summary"],
        "lines": [
            {"code": "62480", "amount": 1800},
        ],
    },
    # CLM-9044 — Same member, hospital, service date and procedure as CLM-8710,
    # but the amount differs, so the complete line items do not match.
    {
        "claim_id": "CLM-9044",
        "member_id": "M-2214",
        "hospital_id": "H-114",
        "date_of_service": "2026-08-20",
        "narrative": "A separate appendix claim with a corrected billed amount.",
        "documents": ["itemised_bill", "discharge_summary"],
        "lines": [
            {"code": "47120", "amount": 1499},
        ],
    },
    # CLM-9045 — PA-5521 is valid through 2026-10-31, inclusive.
    {
        "claim_id": "CLM-9045",
        "member_id": "M-2214",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-31",
        "narrative": "Lumbar spinal fusion performed on the final day of the authorisation period.",
        "documents": ["itemised_bill", "discharge_summary"],
        "lines": [
            {"code": "62480", "amount": 1000},
        ],
    },
]


EXTRA_DECIDED = []
EXTRA_REQUIRED_DOCS = {}
