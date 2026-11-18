-- Purpose: ordered treatment-class pathway per patient; grain is patient.
SELECT patient_id, GROUP_CONCAT(treatment_class, ' -> ') AS treatment_sequence,
       COUNT(*) AS line_count, SUM(duration_days) AS total_treatment_days
FROM (
  SELECT te.patient_id, te.treatment_line, t.treatment_class, te.duration_days
  FROM treatment_events te JOIN treatments t USING(treatment_id)
  ORDER BY te.patient_id, te.treatment_line
) GROUP BY patient_id;
