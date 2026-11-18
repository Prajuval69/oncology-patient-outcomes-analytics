# Data Quality Validation Rules

Implement checks such as:
- patient_id not null
- unique patient identifiers
- diagnosis date <= treatment start
- treatment start <= treatment end
- valid stage categories
- valid response categories
- non-negative utilization/costs
- non-negative survival/follow-up time
- event indicator in {0,1}
- no impossible age values
- no duplicate treatment event IDs
- required foreign keys resolve

Return machine-readable validation results with pass/fail status and severity.
