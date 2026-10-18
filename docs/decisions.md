# Decision Log

Every important research or design decision is recorded here with its reasoning.
Decisions can be revised, but never silently: add a new entry that supersedes the old one.

| Status | Meaning |
|--------|---------|
| Accepted | Decision is in force |
| Open | Still under discussion |
| Superseded | Replaced by a later decision |

---

## D-001 — Prediction task: screening for current undiagnosed hypertension
- **Date:** 2026-10-18
- **Status:** Accepted
- **Decision:** The first task is cross-sectional screening: identifying adults who may currently have undiagnosed elevated blood pressure. It is not prediction of future hypertension incidence or cardiovascular events.
- **Reasoning:** These are different tasks that need different data and outcome definitions. Incidence and event prediction require longitudinal follow-up data, which we do not have yet.
- **Consequences:** Outcome definition, study population and allowed predictors must all match a screening setting.

## D-002 — Data files are never committed to Git
- **Date:** 2026-10-18
- **Status:** Accepted
- **Decision:** Raw and processed data live in `data/raw` and `data/processed`, which are excluded by `.gitignore`. The repository contains code that downloads and processes data, not the data itself.
- **Reasoning:** Keeps the repository small and reproducible, and ensures that any future restricted or patient-level data (for example from Yemen) can never be published by accident.

## D-003 — Outcome definition and study population
- **Date:** 2026-10-18
- **Status:** Accepted

### Study population
Adults who have never been told they have hypertension:
- Age ≥20 years.
- `BPQ020` = No (never told by a doctor they have high blood pressure).
- Excluded: `BPQ020` = Yes, Refused or Don't know; pregnant participants; participants without at least the 2nd oscillometric reading.

### Blood pressure value
- Mean of the 2nd and 3rd oscillometric readings.
- If the 3rd reading is missing, use the 2nd reading alone.
- If only the 1st reading is available, exclude the participant.

### Outcome
- **Positive (undiagnosed elevated BP):** systolic ≥140 mmHg or diastolic ≥90 mmHg.
- **Negative:** below both thresholds.

### Reasoning
- **Population:** The research question is about people who do not know they have hypertension. Including diagnosed or treated participants would teach the model the characteristics of known patients (and their care) rather than of hidden cases.
- **Threshold 140/90:** Used by WHO and European guidelines and by WHO STEPS surveys, so it matches the definition likely to be found in regional or Yemeni data. Whether Yemen's national guidelines use this threshold has not been verified.
- **Readings 2 and 3:** The 1st reading is often raised by stress or insufficient rest. Averaging two readings reduces random error. This matches the WHO STEPS method.
- **Age ≥20:** NHANES family-history and cardiovascular questions are asked only from age 20. Using ≥20 avoids structurally missing data. Hypertension at 18–19 is uncommon, so few positive cases are lost.

### Planned sensitivity analysis
- Repeat the analysis with the 130/80 threshold (ACC/AHA 2017) to measure how much the results depend on the threshold.

### Known limitations
- A single-visit measurement indicates elevated blood pressure at the survey, not clinically confirmed chronic hypertension.
- Participants taking BP-lowering drugs for other conditions (e.g. heart disease) may be labelled negative incorrectly. To be checked later using the NHANES prescription medication file.
- The model is not developed or validated for ages 18–19.

## D-004 — Development and temporal validation data
- **Date:** 2026-10-18
- **Status:** Accepted
- **Decision:** Develop on NHANES 2017–March 2020 pre-pandemic data. Use NHANES 2021–2023 as a held-out temporal validation set.
- **Reasoning:** The pre-pandemic file roughly doubles the BP sample compared to 2017–2018 alone (11,656 vs 7,132 records). 2021–2023 uses the same oscillometric device, so it allows a fair test on data the model has never seen.
- **Limitations:** Requires the combined pre-pandemic weights. Temporal validation is within the same country and survey, so it does not replace external validation in other populations (Phase 4).

## D-005 — Blood pressure measurement method
- **Date:** 2026-10-18
- **Status:** Accepted
- **Decision:** Use oscillometric blood pressure readings only.
- **Reasoning:** It is the only method available across all selected periods, auscultatory measurement was discontinued after 2017–2018, and field screening (including in Yemen) is far more likely to use automated devices than mercury sphygmomanometers.

## D-006 — Predictor sets: Model A (no lab) and Model B (with lab)
- **Date:** 2026-10-18
- **Status:** Accepted, predictor list updated by D-007
- **Decision:** Develop and compare two models on the same study population.
  - **Model A (no laboratory):** age, sex, BMI, waist circumference, smoking, physical activity, diagnosed diabetes, family history of diabetes, family history of heart attack or angina before age 50.
  - **Model B (Model A + laboratory):** adds HbA1c, total cholesterol, HDL cholesterol. Creatinine / eGFR to be added if availability is confirmed.
- **Reasoning:** Model A uses information that can be collected in any primary-care or field setting, including in Yemen. Comparing A and B directly answers whether laboratory data improves screening enough to justify its cost.
- **Excluded:**
  - Fasting-only labs (triglycerides, LDL): would roughly halve the sample.
  - Race/ethnicity: US-specific categories, not transferable to the target population.
  - Pulse from the BP examination: measured in the same session as the outcome.
  - Diagnosis and medication items from `BPQ`: used only to define the population (leakage).
  - History of heart failure, coronary heart disease, heart attack or stroke: these participants are usually under medical care and may take BP-lowering drugs. Excluded from the main models; may be examined in a sensitivity analysis.
- **Known gaps:**
  - NHANES has no question on family history of hypertension.
  - NHANES does not capture khat use, a factor relevant to blood pressure in Yemen. This makes validation on Yemeni data essential before any use there.

## D-007 — Harmonising predictors across periods
- **Date:** 2026-10-18
- **Status:** Accepted, physical activity part superseded by D-008
- **Context:** A variable check (`notebooks/02_variables.ipynb`) showed that two predictor groups from D-006 differ between periods:
  - Family history items (`MCQ300A`, `MCQ300C`) do not exist in 2021–2023 (`MCQ_L`).
  - The physical activity questionnaire changed. 2017–2020 (`P_PAQ`) covers work, transport and recreation. 2021–2023 (`PAQ_L`) covers leisure-time activity and sitting time only.
- **Decision:**
  1. Remove family history of diabetes and of early heart attack/angina from Models A and B.
  2. Replace physical activity with harmonised variables available in both periods: weekly minutes of leisure-time moderate and vigorous activity, and daily sitting time.
  3. Keep the study population at age ≥20 (D-003).
- **Reasoning:**
  - Every predictor must exist in both periods, otherwise the temporal validation does not test the same model.
  - Leisure-time activity and sitting time are the only activity measures common to both periods.
  - Age ≥20 is kept although family history no longer applies: hypertension at 18–19 is uncommon, the cardiovascular history items used in sensitivity analyses are asked from age 20, and changing the population again would reduce consistency.
- **Updated predictor sets:**
  - **Model A:** age, sex, BMI, waist circumference, smoking, leisure-time physical activity, sitting time, diagnosed diabetes.
  - **Model B:** Model A + HbA1c, total cholesterol, HDL cholesterol, creatinine.
- **Limitations:**
  - Family history of hypertension or diabetes is not used, although it is cheap to collect in practice. To be revisited with Yemeni data.
  - Work and transport activity is lost. In Yemen much physical activity comes from manual work and walking, so leisure-time activity may capture it poorly.
  - The two activity questionnaires are not worded identically; the harmonised variable is approximate.

## D-008 — Remove leisure-time physical activity from the models
- **Date:** 2026-10-18
- **Status:** Accepted
- **Context:** After harmonising (D-007), leisure-time activity still differs strongly between periods (`notebooks/02_variables.ipynb`):

  | | 2017–2020 | 2021–2023 |
  |---|---|---|
  | Median min/week | 50 | 208 |
  | Any leisure-time activity | 52.9% | 84.7% |
  | ≥150 min/week | 39.2% | 57.0% |

  Such a large shift in two years reflects the change in questionnaire wording (2017–2020: typical week, bouts of ≥10 continuous minutes; 2021–2023: frequency per day/week/month/year and minutes per session, no minimum bout), not a real change in behaviour.
- **Decision:** Remove leisure-time physical activity from Models A and B. Keep daily sitting time, which is comparable between periods (median 300 min/day in both).
- **Reasoning:** A predictor measured differently in development and validation data would make the temporal validation measure questionnaire differences rather than model performance.
- **Updated predictor sets:**
  - **Model A:** age, sex, BMI, waist circumference, smoking, sitting time, diagnosed diabetes.
  - **Model B:** Model A + HbA1c, total cholesterol, HDL cholesterol, creatinine.
- **Limitations:**
  - Physical activity is an established risk factor for hypertension and is not represented.
  - Future Yemeni data collection should include an activity measure suited to local life (work, walking, transport), not only leisure-time exercise.
- **Note:** `ltpa_min_week` is still produced by `src/build_dataset.py` for transparency but is not used as a predictor.


## D-009 — Implausible and extreme values
- **Date:** 2026-10-18
- **Status:** Accepted
- **Context:** Counts of extreme values were checked (`notebooks/02_variables.ipynb`). All affected fewer than 15 participants per rule and period (e.g. BMI >60: 12 and 4; creatinine >3: 3 and 0; sitting >20 h/day: 1 and 1).
- **Decision:**
  1. Measured values (BMI, waist, laboratory results, blood pressure) are kept as recorded. Extreme values are biologically possible and were measured by trained staff or a quality-controlled laboratory.
  2. Self-reported sitting time above 20 hours per day (1,200 minutes) is set to missing, as it is not compatible with sleep.
  3. Influence of extreme values on the models will be handled during preprocessing (Phase 3), not by deleting data.
- **Reasoning:** Removing extreme but real measurements would remove the participants at highest risk. Only clearly impossible self-reports are treated as errors.