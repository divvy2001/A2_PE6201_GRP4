# Problem A case contribution — XIAO XIAOHUA

This folder contains five additional Problem A evaluation cases owned by
'xiao_xiaohua'.

## Files

- 'cases.py' — new fixture rows to be merged into the shared Problem A data.
- 'labels.json' — expected decisions and required evidence for each case.

## Assigned cases

| Case ID | Family | Expected decision |
|---|---|---|
| CLM-9011| ordinary short | approve_in_principle |
| CLM-9012| multi-line | approve_in_principle |
| CLM-9013| missing required document | request_document |
| CLM-9014| expired pre-authorisation | request_document` |
| CLM-9015| true duplicate | 'escalate' |

'CLM-9015' is paired with the added historical claim 'CLM-8715'. The two
records match on member, hospital, date of service, and complete line items.

## Validation

After these rows and labels are merged into the shared fixture data:

1. Regenerate the fixture JSON files.
2. Run 'reference_data/check_my_data.py'.
3. Run the scripted evaluation cases against the merged data.

Do not edit or delete shipped reference-data records.