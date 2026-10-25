# Yemen Hypertension Screening 

An independent research project on whether simple, low-cost information can identify adults with **undiagnosed hypertension**, with the long-term goal of supporting screening in Yemen.

> **Research prototype.** This is not a diagnostic tool and must not be used for clinical decisions. Hypertension is diagnosed by confirmed blood pressure measurement.

---

## Research question
Can demographic, lifestyle, clinical and laboratory data identify adults who have elevated blood pressure but have never been told they have hypertension?

## Why
Hypertension is common in Yemen and many cases are undiagnosed. Where blood pressure devices, staff or visits are limited, a simple questionnaire-based risk score could help prioritise who should be measured first.

## Current status
| Phase | Status |
|---|---|
| 1. Data selection and study design |  Done |
| 2. Data understanding and cleaning |  Done |
| 3. Model development (internal validation) |  Done |
| 4. Validation |  Temporal validation done; external validation needed |
| 5. Clinical expansion |  Not started |
| 6. Adaptation to Yemen |  Seeking Yemeni data and collaborators |

---

## Data
**NHANES** (US National Health and Nutrition Examination Survey), public individual-level data with measured blood pressure.

| | Period | Participants | Undiagnosed elevated BP |
|---|---|---|---|
| Development | 2017 – March 2020 | 4,597 | 13.5% |
| Temporal validation | 2021 – 2023 | 3,587 | 10.6% |

- **Population:** adults ≥20 years, not pregnant, never told by a doctor they have hypertension.
- **Outcome:** mean of the 2nd and 3rd oscillometric readings ≥140/90 mmHg (WHO / ESC threshold).
- Data files are downloaded by script and are **not** stored in this repository.

## Method
- **Model A (no laboratory tests):** age, sex, waist circumference, smoking, sitting time, diagnosed diabetes.
- **Model B:** Model A + HbA1c, total cholesterol, HDL cholesterol, creatinine.
- Logistic regression (with splines for age and waist) compared with random forest and XGBoost.
- Repeated stratified 5-fold cross-validation (×10) on 2017–2020; missing values imputed inside each training fold.
- Referral threshold fixed in advance at **80% sensitivity**.
- Final model chosen with pre-specified rules, then tested **once** on 2021–2023.

Every design choice and its reasoning is recorded in [`docs/decisions.md`](docs/decisions.md).

---

## Key results
Full results: [`docs/results.md`](docs/results.md)

**Final model:** logistic regression, Model A (no laboratory tests).

| | Internal CV (2017–2020) | Temporal validation (2021–2023) |
|---|---|---|
| ROC-AUC | 0.744 | 0.709 (95% CI 0.684–0.733) |
| Observed / expected cases | 1.00 | 0.70 |
| Calibration slope | 0.96 | 0.83 |
| Sensitivity at fixed threshold | 0.80 | 0.82 |
| People referred for BP measurement | 49% | 55% |

**Main findings**
1. **Age carries most of the information.** Model A improves only slightly on a simple rule such as "measure blood pressure in everyone aged ≥43" (ROC-AUC +0.01).
2. **Laboratory tests add almost nothing** for screening (+0.004 ROC-AUC).
3. **Complex models do not help.** Random forest and XGBoost perform the same as logistic regression, with worse calibration.
4. **Likely explanation:** people with clear risk factors (e.g. diabetes, obesity) are often already diagnosed in the US, so the remaining undiagnosed cases are harder to distinguish. Including diagnosed adults triples the gain over age (0.011 → 0.031).
5. **The model did not transport perfectly, even within the US.** Three years later it overestimated risk by about 40%. Recalibration fixed the risk estimates but not screening efficiency.
6. **The threshold matters.** With the 130/80 mmHg threshold, Model A adds clearly more beyond age (ROC-AUC +0.025 internally, +0.048 on 2021–2023), while age alone transports poorly. Risk factors such as waist, smoking and diabetes appear more informative for milder elevation.

## What this means for Yemen
- A model developed in one population **cannot be used in another without local validation and recalibration.**
- Diagnosis rates in Yemen are much lower than in the US. **Hypothesis:** risk factors may therefore add more information beyond age in Yemen than in NHANES. This can only be tested with Yemeni data.
- Important local factors such as **khat use** and **salt intake** are not available in NHANES.

## Limitations
- US data only; not validated outside the US.
- Single-visit measurement, not clinically confirmed chronic hypertension.
- Physical activity and family history could not be used (not measured consistently across periods).
- 12% of examined eligible participants in 2017–2020 had no BP measurement (reason undocumented).

---

## Repository structure
```
docs/
  decisions.md     Design decisions and reasoning (D-001 ...)
  datasets.md      Evaluation of all data sources considered
  results.md       All results, including unfavourable ones (R-001 ...)
notebooks/         Analyses, numbered in the order they were done
src/
  download_nhanes.py   Download NHANES files
  cohort_flow.py       Participant flow through inclusion criteria
  build_dataset.py     Build the analysis datasets
  modeling.py          Pipelines, cross-validation and metrics
data/              Local only, not committed
```

## Reproduce
```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/download_nhanes.py
python src/build_dataset.py
```
Then run the notebooks in order.

## Next steps
- External validation in other populations.
- Access to Yemeni data (e.g. population-based hypertension studies) for validation and recalibration.
- Pilot data collection in Yemen, including local factors such as khat use and salt intake.

## Author
Gamal Abdulnaser Al-Sabaeei, Applied Data Science & AI student, The Hague University of Applied Sciences.
This is a personal project carried out independently of my studies.
Interested in collaboration with researchers or health organisations working on hypertension in Yemen.
Contact: [LinkedIn](https://www.linkedin.com/in/gamal-al-sabaeei-65a7b9395/) · jamalalsa2021@gmail.com

## Disclaimer
Independent personal research project. It is not supervised, reviewed or endorsed by The Hague University of Applied Sciences or any other institution.
Not intended to diagnose hypertension or replace professional medical evaluation.
