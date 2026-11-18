-- Purpose: one row per eligible synthetic patient with baseline, first-treatment, outcome, and utilization fields.
WITH first_treatment AS (
  SELECT te.*, t.treatment_class, t.regimen_name,
         ROW_NUMBER() OVER (PARTITION BY te.patient_id ORDER BY te.treatment_line, te.treatment_start_date) AS rn
  FROM treatment_events te JOIN treatments t USING (treatment_id)
), line_counts AS (
  SELECT patient_id, COUNT(*) AS treatment_event_count, MAX(treatment_line) AS max_treatment_line
  FROM treatment_events GROUP BY patient_id
)
SELECT p.*, d.diagnosis_id, d.cancer_type, d.diagnosis_date, d.stage, d.biomarker_status, d.ecog_status,
       c.diabetes, c.cardiovascular_disease, c.chronic_kidney_disease, c.chronic_pulmonary_disease,
       c.smoking_history, c.comorbidity_count,
       ft.treatment_id AS first_treatment_id, ft.regimen_name AS first_regimen, ft.treatment_class AS first_treatment_class,
       ft.treatment_start_date AS first_treatment_start_date,
       lc.treatment_event_count, lc.max_treatment_line,
       o.response_category, o.responder, o.progression_event, o.progression_days, o.survival_days, o.death_event, o.last_followup_date,
       u.outpatient_visits, u.emergency_visits, u.inpatient_admissions, u.total_cost_usd
FROM patients p
JOIN diagnoses d USING (patient_id)
JOIN comorbidities c USING (patient_id)
JOIN outcomes o USING (patient_id)
JOIN utilization u USING (patient_id)
JOIN first_treatment ft ON p.patient_id = ft.patient_id AND ft.rn = 1
JOIN line_counts lc USING (patient_id);
