# Data dictionary

All identifiers and values are generated. Dates use ISO `YYYY-MM-DD`; money is synthetic USD; time durations are days.

| Table | Column(s) | Type | Definition / allowed values | Origin and analytical role | Limitations |
|---|---|---|---|---|---|
| patients | patient_id | TEXT | Unique `SYN-P#####` identifier | Generated primary key | Not a real person identifier |
| patients | age_at_diagnosis | INTEGER | 25–90 years | Generated baseline feature | Simplified distribution |
| patients | sex | TEXT | Female, Male | Generated demographic/filter | Binary synthetic encoding |
| patients | race_ethnicity | TEXT | White, Black, Asian, Hispanic, Other/Unknown | Generated demographic/filter | Coarse categories; not biological variables |
| patients | region | TEXT | Northeast, Midwest, South, West | Generated geography/filter | Broad US-style regions only |
| patients | insurance_type | TEXT | Commercial, Medicare, Medicaid, Other | Generated baseline feature | Not a coverage model |
| patients | synthetic_record | INTEGER | Always 1 | Explicit synthetic-data label | None |
| diagnoses | diagnosis_id | TEXT | Unique `DX#####` | Generated primary key | One diagnosis per patient |
| diagnoses | patient_id | TEXT | Foreign key to patients | Generated relationship | — |
| diagnoses | cancer_type | TEXT | Breast, Lung, Colorectal, Prostate, Melanoma | Generated disease/filter/model feature | Simplified disease taxonomy |
| diagnoses | diagnosis_date | TEXT/DATE | 2018–2023 | Generated cohort index date | No recurrence/earlier history |
| diagnoses | stage | TEXT | I, II, III, IV | Generated disease severity feature | Generic staging across cancers |
| diagnoses | biomarker_status | TEXT | Cancer-specific synthetic label; nullable | Generated baseline model feature | Not assay- or guideline-specific |
| diagnoses | ecog_status | REAL | Synthetic ECOG-like 0–3; nullable | Generated performance feature | Not clinically assessed |
| treatments | treatment_id | TEXT | TRT01–TRT06 | Generated reference key | Generalized treatment catalog |
| treatments | regimen_name | TEXT | Generalized regimen descriptor | Generated display field | No named drugs/doses |
| treatments | treatment_class | TEXT | Chemotherapy, immunotherapy, targeted, hormone, radiation, surgery | Generated pathway category | Classes are broad |
| treatment_events | treatment_event_id | TEXT | Unique `TE######` | Generated primary key | — |
| treatment_events | patient_id, treatment_id | TEXT | Valid foreign keys | Generated pathway relationships | — |
| treatment_events | treatment_line | INTEGER | Contiguous 1–3 | Generated/derived sequence order | Simplified line logic |
| treatment_events | treatment_start_date, treatment_end_date | TEXT/DATE | Start after diagnosis; end after start | Generated time relationships | No pauses/overlap |
| treatment_events | duration_days | INTEGER days | End minus start | Derived pathway duration | Approximate |
| outcomes | outcome_id | TEXT | Unique `OUT#####` | Generated primary key | — |
| outcomes | response_category | TEXT | Complete response, partial response, stable disease, progressive disease, unknown | Generated outcome | Simplified, not RECIST-validated |
| outcomes | responder | INTEGER | 1 for complete/partial; otherwise 0 | Derived binary model target | Collapses response nuance |
| outcomes | progression_event | INTEGER | 0/1 | Generated event | Synthetic association only |
| outcomes | progression_days | REAL days | Time to progression when event=1; nullable | Generated outcome | Not used as primary survival endpoint |
| outcomes | survival_days | INTEGER days | Diagnosis to death/censoring | Generated survival time | Administrative/random censoring |
| outcomes | death_event | INTEGER | 0 censored, 1 event | Generated event indicator | Synthetic mortality event |
| outcomes | last_followup_date | TEXT/DATE | Diagnosis plus survival_days | Derived censor/event date | No encounter-level follow-up |
| comorbidities | comorbidity_id | TEXT | Unique `CM#####` | Generated primary key | — |
| comorbidities | diabetes, cardiovascular_disease, chronic_kidney_disease, chronic_pulmonary_disease, smoking_history | INTEGER | 0/1 indicators | Generated baseline features | Coarse indicators only |
| comorbidities | comorbidity_count | INTEGER | Sum of four disease indicators | Derived burden feature | Unweighted count |
| utilization | utilization_id | TEXT | Unique `UTL#####` | Generated primary key | — |
| utilization | outpatient_visits, emergency_visits, inpatient_admissions | INTEGER counts | Non-negative utilization | Generated KPI/outcome context | No time-varying encounters |
| utilization | total_cost_usd | REAL synthetic USD | Non-negative total modeled cost | Generated utilization measure | Not economic evidence |
| mart_cohort | first_treatment_class, treatment_event_count, max_treatment_line | mixed | First ordered event and per-patient counts | SQL-derived model/pathway features | First class is not randomized |

