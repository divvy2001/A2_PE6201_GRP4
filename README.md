# Problem A case contribution — LIANG LUWEN

Owner: LIANG LUWEN

This folder contains five additional Problem A evaluation cases. The labels
were defined before model evaluation. No shipped record is edited or deleted.
All five cases reuse existing members, policies, hospitals, procedures,
required-document rules, and pre-authorisations.

## Assigned cases

| Case ID | Family | Expected decision | Purpose |
|---|---|---|---|
| CLM-9051 | ordinary low-cost single line | approve_in_principle | Short, low-cost baseline |
| CLM-9052 | ordinary two line | approve_in_principle | Two independent covered lines |
| CLM-9053 | four line + valid pre-auth | approve_in_principle | Longer trajectory with one pre-auth branch |
| CLM-9054 | exact remaining limit | approve_in_principle | Boundary: claim total == remaining limit |
| CLM-9055 | missing required document, multi-line | request_document | Ask path while retaining already-resolved line evidence |

## Why these cases

The set deliberately varies trajectory length (one, two, and four lines),
adds an exact annual-limit boundary that is not present in the shipped cases,
and includes a request-document case where another line is already resolvable.
This supports both D4 coverage and the later D6 turn/token/cost analysis.

## Integration

Merge `EXTRA_CLAIMS` from `cases.py` into the shared Problem A fixture
generator and append `labels.json` to `reference_data/expected_outcomes_A.json`.
No supporting-table additions are required.

After integration, run:

```bash
python reference_data/make_fixtures_A.py
python reference_data/check_my_data.py
python -m unittest discover -s tests -v
```

Then add scripted trajectories when the team expands `Evals/scripted_cases.py`.
