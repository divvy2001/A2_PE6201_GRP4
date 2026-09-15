# Problem A case contribution — LI ZIHAO

Owner: LI ZIHAO

This folder contains six authored Problem A evaluation cases. They follow the
shared `EXTRA_*` contribution format and do not modify any supplied row. Five
are in the current formal evaluation set; `CLM-9043` is retained here as
contribution history after the team reduced the number of negative cases.

## Assigned cases

| Case ID | Family | Expected decision | What it tests |
|---|---|---|---|
| CLM-9041 | annual-limit exact boundary | `approve_in_principle` | A payable total exactly equal to the remaining limit is allowed. |
| CLM-9042 | multiple exclusions, partly payable | `approve_in_principle` | Two excluded lines and one covered line are recorded in one decision. |
| CLM-9043 | pre-authorisation wrong member | `request_document` | A pre-authorisation for the correct procedure and date cannot be reused for another member. |
| CLM-9044 | duplicate near-miss: amount | `approve_in_principle` | Matching member, hospital, date and code are insufficient when the line amount differs. |
| CLM-9045 | pre-authorisation end-date boundary | `approve_in_principle` | A pre-authorisation remains valid on its `valid_to` date. |
| CLM-9046 | policy end-date boundary | `approve_in_principle` | An active policy remains in period on its inclusive `end_date`. |

## Files

- `cases.py` contains the six authored claim records.
- `labels.json` contains the six labels fixed before agent evaluation.
- `README.md` records ownership and the intended decision boundaries.

## Integration

Merge the selected records into the shared fixture data and labels, then
validate the shared dataset:

```text
python reference_data/make_fixtures_A.py
python reference_data/check_my_data.py
python -m unittest discover -s tests -v
```

The formal v2 Gemini run should begin only after every member's cases have been
integrated and the team has frozen one shared commit and evaluation dataset.
