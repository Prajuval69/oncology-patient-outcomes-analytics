# Testing Specification

Use pytest.

Test:
- synthetic data generation
- schema integrity
- key uniqueness
- date consistency
- missingness handling
- SQL outputs
- cohort counts
- KPI calculations
- treatment-line derivation
- survival input validity
- model pipeline
- metric calculation
- dashboard import/startup components where practical

Include edge cases:
- empty cohort
- single-category subgroup
- all-censored survival subset
- missing optional values
- duplicated source rows
- invalid date ordering

Tests should be deterministic.
