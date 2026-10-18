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
- Age ≥18 years.
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

### Planned sensitivity analysis
- Repeat the analysis with the 130/80 threshold (ACC/AHA 2017) to measure how much the results depend on the threshold.

### Known limitations
- A single-visit measurement indicates elevated blood pressure at the survey, not clinically confirmed chronic hypertension.
- Participants taking BP-lowering drugs for other conditions (e.g. heart disease) may be labelled negative incorrectly. To be checked later using the NHANES prescription medication file.

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