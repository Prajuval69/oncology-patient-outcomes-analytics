-- Purpose: cancer-by-stage distribution; grain is cancer type and stage.
SELECT cancer_type, stage, COUNT(*) patient_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY cancer_type), 2) percent_within_cancer
FROM mart_cohort GROUP BY cancer_type, stage;
