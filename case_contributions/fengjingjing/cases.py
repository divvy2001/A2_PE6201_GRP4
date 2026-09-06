"""Five evaluation cases contributed by Feng Jingjing."""

EXTRA_PROCEDURES = []
EXTRA_HOSPITALS = []
EXTRA_POLICIES = []
EXTRA_MEMBERS = []
EXTRA_PREAUTHORISATIONS = []

EXTRA_CLAIMS = [
    {
        "claim_id": "CLM-9031",
        "member_id": "M-5502",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-11",
        "narrative": "Routine MRI examination following a medical consultation.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "70553", "amount": 500},
        ],
    },

    {
        "claim_id": "CLM-9032",
        "member_id": "M-5502",
        "hospital_id": "H-114",
        "date_of_service": "2026-10-12",
        "narrative": "Several diagnostic and outpatient procedures were performed during the same episode of care.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "99213", "amount": 150},
            {"code": "80053", "amount": 80},
            {"code": "70553", "amount": 500},
            {"code": "45378", "amount": 1000},
        ],
    },

    {
        "claim_id": "CLM-9033",
        "member_id": "M-6118",
        "hospital_id": "H-207",
        "date_of_service": "2026-10-13",
        "narrative": "Lumbar spinal fusion following persistent lower back pain.",
        "documents": ["itemised_bill", "discharge_summary"],
        "lines": [
            {"code": "62480", "amount": 1500},
        ],
    },

    {
        "claim_id": "CLM-9034",
        "member_id": "M-2214",
        "hospital_id": "H-114",
        "date_of_service": "2026-08-21",
        "narrative": "Appendix treatment following a separate admission.",
        "documents": ["itemised_bill", "discharge_summary"],
        "lines": [
            {"code": "47120", "amount": 1500},
        ],
    },

    {
        "claim_id": "CLM-9035",
        "member_id": "M-5502",
        "hospital_id": "H-207",
        "date_of_service": "2026-05-25",
        "narrative": "Routine outpatient consultation before the policy effective date.",
        "documents": ["itemised_bill"],
        "lines": [
            {"code": "99213", "amount": 180},
        ],
    },
]

EXTRA_DECIDED = []
EXTRA_REQUIRED_DOCS = {}
