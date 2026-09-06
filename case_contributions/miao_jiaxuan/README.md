# Miao Jiaxuan case contribution

Owner: MIAO JIAXUAN

Case IDs:

- CLM-9021: ordinary single-line claim
- CLM-9022: partly payable claim
- CLM-9023: non-panel hospital
- CLM-9024: one dollar below remaining limit
- CLM-9025: second lapsed-policy case

The contribution adds one new policy and one new member for CLM-9025.
No shipped row is modified.

Files:

- cases.py contains EXTRA_* records.
- labels.json contains labels written before agent evaluation.
- README.md explains the intended decision boundaries.

Integration:

Divyansh should merge the EXTRA_* values into
reference_data/make_fixtures_A.py and merge the labels into
reference_data/expected_outcomes_A.json.

After integration, run:

python reference_data/make_fixtures_A.py
python reference_data/check_my_data.py
python -m unittest discover -s tests -v
