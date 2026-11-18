-- Purpose: utilization by cancer/stage; grain is cancer type and stage.
SELECT cancer_type, stage, COUNT(*) patient_count,
       ROUND(AVG(outpatient_visits), 2) mean_outpatient_visits,
       ROUND(AVG(emergency_visits), 2) mean_emergency_visits,
       ROUND(AVG(inpatient_admissions), 2) mean_inpatient_admissions,
       ROUND(AVG(total_cost_usd), 2) mean_total_cost_usd
FROM mart_cohort GROUP BY cancer_type, stage;
