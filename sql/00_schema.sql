CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL, description TEXT);
CREATE TABLE patients (
  patient_id TEXT PRIMARY KEY, age_at_diagnosis INTEGER NOT NULL CHECK(age_at_diagnosis BETWEEN 18 AND 100),
  sex TEXT NOT NULL, race_ethnicity TEXT NOT NULL, region TEXT NOT NULL,
  insurance_type TEXT NOT NULL, synthetic_record INTEGER NOT NULL CHECK(synthetic_record = 1)
);
CREATE TABLE diagnoses (
  diagnosis_id TEXT PRIMARY KEY, patient_id TEXT NOT NULL UNIQUE REFERENCES patients(patient_id),
  cancer_type TEXT NOT NULL, diagnosis_date TEXT NOT NULL,
  stage TEXT NOT NULL CHECK(stage IN ('I','II','III','IV')),
  biomarker_status TEXT, ecog_status REAL CHECK(ecog_status BETWEEN 0 AND 4 OR ecog_status IS NULL)
);
CREATE TABLE treatments (
  treatment_id TEXT PRIMARY KEY, regimen_name TEXT NOT NULL, treatment_class TEXT NOT NULL
);
CREATE TABLE treatment_events (
  treatment_event_id TEXT PRIMARY KEY, patient_id TEXT NOT NULL REFERENCES patients(patient_id),
  treatment_id TEXT NOT NULL REFERENCES treatments(treatment_id), treatment_line INTEGER NOT NULL CHECK(treatment_line >= 1),
  treatment_start_date TEXT NOT NULL, treatment_end_date TEXT NOT NULL, duration_days INTEGER NOT NULL CHECK(duration_days >= 0)
);
CREATE TABLE outcomes (
  outcome_id TEXT PRIMARY KEY, patient_id TEXT NOT NULL UNIQUE REFERENCES patients(patient_id),
  response_category TEXT NOT NULL CHECK(response_category IN ('Complete response','Partial response','Stable disease','Progressive disease','Unknown')),
  responder INTEGER NOT NULL CHECK(responder IN (0,1)), progression_event INTEGER NOT NULL CHECK(progression_event IN (0,1)),
  progression_days REAL, survival_days INTEGER NOT NULL CHECK(survival_days >= 0),
  death_event INTEGER NOT NULL CHECK(death_event IN (0,1)), last_followup_date TEXT NOT NULL
);
CREATE TABLE comorbidities (
  comorbidity_id TEXT PRIMARY KEY, patient_id TEXT NOT NULL UNIQUE REFERENCES patients(patient_id),
  diabetes INTEGER NOT NULL, cardiovascular_disease INTEGER NOT NULL, chronic_kidney_disease INTEGER NOT NULL,
  chronic_pulmonary_disease INTEGER NOT NULL, smoking_history INTEGER NOT NULL, comorbidity_count INTEGER NOT NULL CHECK(comorbidity_count >= 0)
);
CREATE TABLE utilization (
  utilization_id TEXT PRIMARY KEY, patient_id TEXT NOT NULL UNIQUE REFERENCES patients(patient_id),
  outpatient_visits INTEGER NOT NULL CHECK(outpatient_visits >= 0), emergency_visits INTEGER NOT NULL CHECK(emergency_visits >= 0),
  inpatient_admissions INTEGER NOT NULL CHECK(inpatient_admissions >= 0), total_cost_usd REAL NOT NULL CHECK(total_cost_usd >= 0)
);
CREATE INDEX idx_treatment_patient_line ON treatment_events(patient_id, treatment_line);
CREATE INDEX idx_diagnosis_cancer_stage ON diagnoses(cancer_type, stage);
