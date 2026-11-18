-- Purpose: single-row portfolio KPI summary; grain is full cohort.
SELECT COUNT(*) patients, COUNT(*) diagnoses,
       SUM(treatment_event_count) treatment_events,
       ROUND(100.0 * AVG(responder), 2) response_rate_percent,
       ROUND(100.0 * AVG(progression_event), 2) progression_rate_percent,
       ROUND(AVG(survival_days), 1) mean_followup_days,
       ROUND(AVG(outpatient_visits), 2) mean_outpatient_visits,
       ROUND(AVG(inpatient_admissions), 2) mean_inpatient_admissions,
       ROUND(AVG(total_cost_usd), 2) mean_total_cost_usd
FROM mart_cohort;
