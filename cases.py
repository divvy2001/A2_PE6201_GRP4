"""Five Problem A evaluation cases contributed by Liang Luwen."""

from __future__ import annotations

# These cases deliberately reuse shipped reference records so that the
# contribution changes only the work queue, not the underlying policy rules.
EXTRA_PROCEDURES = []
EXTRA_HOSPITALS = []
EXTRA_POLICIES = []
EXTRA_MEMBERS = []
EXTRA_PREAUTHORISATIONS = []
EXTRA_DECIDED = []
EXTRA_REQUIRED_DOCS = {}

EXTRA_CLAIMS = [
    # CLM-9051 — Low-cost, one-line ordinary baseline.
    {
        "claim_id": "CLM-9051",
        "member_id": "M-5502",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-21",
        "narrative": "Routine blood test after a general consultation.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "80053", "amount": 45},
        ],
    },

    # CLM-9052 — Two covered lines, no pre-authorisation branch.
    {
        "claim_id": "CLM-9052",
        "member_id": "M-5502",
        "hospital_id": "H-114",
        "date_of_service": "2026-10-22",
        "narrative": "Outpatient consultation followed by an MRI investigation.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "99213", "amount": 160},
            {"code": "70553", "amount": 540},
        ],
    },

    # CLM-9053 — Four-line ordinary claim with one valid pre-authorisation.
    # 27447 requires both discharge_summary and a current pre-authorisation;
    # PA-5702 is valid for M-5502 on this service date.
    {
        "claim_id": "CLM-9053",
        "member_id": "M-5502",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-23",
        "narrative": (
            "Planned knee replacement with routine blood work, consultation, "
            "and MRI during the same episode of care."
        ),
        "documents": ["itemised_bill", "discharge_summary"],
        "lines": [
            {"code": "27447", "amount": 6000},
            {"code": "80053", "amount": 90},
            {"code": "99213", "amount": 180},
            {"code": "70553", "amount": 620},
        ],
    },

    # CLM-9054 — Exact annual-limit boundary.
    # POL-4102 has 600 remaining (6000 - 5400), so a claim total of exactly
    # 600 must NOT trigger annual_limit_exceeded. The workflow says greater
    # than the remaining limit, not greater-than-or-equal-to.
    {
        "claim_id": "CLM-9054",
        "member_id": "M-3390",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-24",
        "narrative": "Outpatient consultation costing exactly the remaining annual limit.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "99213", "amount": 600},
        ],
    },

    # CLM-9055 — Multi-line request-document case.
    # 45378 requires itemised_bill, which is deliberately absent. The other
    # line is independently resolvable and should still be recorded.
    {
        "claim_id": "CLM-9055",
        "member_id": "M-5502",
        "hospital_id": "H-114",
        "date_of_service": "2026-10-25",
        "narrative": "Consultation and day colonoscopy; supporting invoice not attached.",
        "documents": [],
        "lines": [
            {"code": "99213", "amount": 180},
            {"code": "45378", "amount": 1100},
        ],
    },
]
