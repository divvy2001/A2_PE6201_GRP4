"""Five evaluation cases contributed by Miao Jiaxuan."""

EXTRA_PROCEDURES = []

EXTRA_HOSPITALS = []

EXTRA_POLICIES = [
    {
        "policy_id": "POL-9025",
        "product": "Shield Plus",
        "status": "lapsed",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "annual_limit": 12000,
        "used_to_date": 1000,
        "exclusions": [],
    },
]

EXTRA_MEMBERS = [
    {
        "member_id": "M-9025",
        "name": "Miao Test Member",
        "policy_id": "POL-9025",
        "join_date": "2025-01-01",
    },
]

EXTRA_PREAUTHORISATIONS = []

EXTRA_CLAIMS = [
    {
        "claim_id": "CLM-9021",
        "member_id": "M-5502",
        "hospital_id": "H-114",
        "date_of_service": "2026-10-01",
        "narrative": "Routine blood test after a general consultation.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "80053", "amount": 90},
        ],
    },
    {
        "claim_id": "CLM-9022",
        "member_id": "M-2214",
        "hospital_id": "H-114",
        "date_of_service": "2026-10-02",
        "narrative": (
            "MRI investigation and a cosmetic skin procedure "
            "were completed during the same visit."
        ),
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "70553", "amount": 620},
            {"code": "31255", "amount": 250},
        ],
    },
    {
        "claim_id": "CLM-9023",
        "member_id": "M-5502",
        "hospital_id": "H-451",
        "date_of_service": "2026-10-03",
        "narrative": (
            "Routine consultation at a non-panel hospital. "
            "The member paid the hospital directly."
        ),
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "99213", "amount": 180},
        ],
    },
    {
        "claim_id": "CLM-9024",
        "member_id": "M-3390",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-04",
        "narrative": "Outpatient consultation close to the remaining annual limit.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "99213", "amount": 599},
        ],
    },
    {
        "claim_id": "CLM-9025",
        "member_id": "M-9025",
        "hospital_id": "H-114",
        "date_of_service": "2026-10-05",
        "narrative": "Appendix surgery under a policy currently marked as lapsed.",
        "documents": ["itemised_bill", "discharge_summary"],
        "lines": [
            {"code": "47120", "amount": 1500},
        ],
    },
]

EXTRA_DECIDED = []

EXTRA_REQUIRED_DOCS = {}
