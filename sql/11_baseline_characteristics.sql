-- Purpose: category-level counts and percentages; grain is characteristic/value.
WITH cohort AS (SELECT * FROM mart_cohort), stacked AS (
  SELECT 'cancer_type' characteristic, cancer_type value FROM cohort UNION ALL
  SELECT 'stage', stage FROM cohort UNION ALL SELECT 'sex', sex FROM cohort UNION ALL
  SELECT 'region', region FROM cohort UNION ALL SELECT 'race_ethnicity', race_ethnicity FROM cohort
)
SELECT characteristic, value, COUNT(*) AS patient_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY characteristic), 2) AS percent
FROM stacked GROUP BY characteristic, value;
