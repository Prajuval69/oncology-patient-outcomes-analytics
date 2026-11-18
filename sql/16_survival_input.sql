-- Purpose: analysis-ready overall-survival input; grain is patient.
SELECT patient_id, survival_days, death_event, cancer_type, stage, age_at_diagnosis, sex,
       ecog_status, comorbidity_count, first_treatment_class
FROM mart_cohort;
