-- Purpose: SQL-native validation counts; grain is one validation rule.
SELECT 'null_patient_id' rule, COUNT(*) failures FROM patients WHERE patient_id IS NULL
UNION ALL SELECT 'duplicate_patient_id', COUNT(*) FROM (SELECT patient_id FROM patients GROUP BY patient_id HAVING COUNT(*) > 1)
UNION ALL SELECT 'diagnosis_after_treatment', COUNT(*) FROM diagnoses d JOIN treatment_events te USING(patient_id) WHERE date(d.diagnosis_date) > date(te.treatment_start_date)
UNION ALL SELECT 'treatment_date_order', COUNT(*) FROM treatment_events WHERE date(treatment_start_date) > date(treatment_end_date)
UNION ALL SELECT 'orphan_diagnosis', COUNT(*) FROM diagnoses d LEFT JOIN patients p USING(patient_id) WHERE p.patient_id IS NULL
UNION ALL SELECT 'orphan_treatment', COUNT(*) FROM treatment_events te LEFT JOIN patients p USING(patient_id) WHERE p.patient_id IS NULL;
