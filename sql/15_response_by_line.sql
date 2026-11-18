-- Purpose: response observed at the patient endpoint summarized by maximum line reached.
SELECT max_treatment_line, COUNT(*) patient_count, SUM(responder) responders,
       ROUND(100.0 * AVG(responder), 2) response_rate_percent
FROM mart_cohort GROUP BY max_treatment_line;
