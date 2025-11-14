The script analyses and produces scores for six data quality dimensions:

- Completeness
- Uniqueness
- Validity
- Conformity
- Consistency
- Timeliness

The script will:

- Load `test_data/grant_applications.csv`
- Apply all configured data quality rules
- Print the per-dimension scores
- Save the scores to `dq_dimension_scores.csv`

## Output

The main output file is:

- `dq_dimension_scores.csv`

Columns:

- `dimension_name`
- `score`
- `passed_rows`
- `failed_rows`
- `total_rows`

Rules can be extended in `config/dq_rules.yaml` and add new functions in `dq_runner.py` for additional checks.
