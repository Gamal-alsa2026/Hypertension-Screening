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

## D-003 — Outcome definition
- **Date:** —
- **Status:** Open
- **Questions to resolve:**
  - Blood pressure threshold: ≥140/90 mmHg (WHO / ESC) or ≥130/80 mmHg (ACC/AHA 2017)?
  - How many readings, and which ones (mean of readings 2–3, all readings)?
  - Are participants with a prior diagnosis or on antihypertensive medication excluded from the screening population?

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