-- Purpose: event and patient counts by line and class; grain is line/class.
SELECT te.treatment_line, t.treatment_class, COUNT(*) treatment_events,
       COUNT(DISTINCT te.patient_id) patient_count, ROUND(AVG(te.duration_days), 1) mean_duration_days
FROM treatment_events te JOIN treatments t USING(treatment_id)
GROUP BY te.treatment_line, t.treatment_class;
