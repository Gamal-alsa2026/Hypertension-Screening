# Decision Log

Every important research or design decision is recorded here with its reasoning.
Decisions can be revised, but never silently: add a new entry that supersedes the old one.

| ID | Status | Meaning |
|----|--------|---------|
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

## D-004 — Primary development dataset
- **Date:** —
- **Status:** Open
- **Candidate:** NHANES 2017–2018 (see `docs/datasets.md`).