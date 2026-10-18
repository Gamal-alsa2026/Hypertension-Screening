# Dataset Evaluation Log

Each data source is assessed with the same template so they can be compared fairly.

**Type:** Individual-level (one row per participant) · Aggregated (summary statistics) · Synthetic / unknown
**Possible role:** Development · External validation · Background only · Not suitable

---

## Template

### Name
- **Source / link:**
- **Type:**
- **Population and country:**
- **Sample size:**
- **Blood pressure:** measured / self-reported / none — protocol:
- **Key variables:** demographics · anthropometrics · lifestyle · medical history · medication · laboratory
- **Access and license:**
- **Known limitations:**
- **Possible role:**
- **Status:**

---

## A. HYDY Study — Yemen
- **Source / link:** https://pmc.ncbi.nlm.nih.gov/articles/PMC3425947/
- **Type:** Individual-level data exists, but we only have the published supplementary tables.
- **Population and country:** Yemen, population-based.
- **Sample size:** ~10,242 participants.
- **Key variables:** age, sex, region, urban/rural residence, smoking, physical activity, BMI, glucose, lipids.
- **Access and license:** Raw data not public. Consider contacting the authors.
- **Possible role:** External validation on the target population (if access is granted). Background otherwise.
- **Status:** Not requested yet.

## B. WHO Global Health Observatory — Yemen
- **Type:** Aggregated (country, year, sex).
- **Possible role:** Background only.
- **Status:** Downloaded.

## C. NCD-RisC Hypertension Estimates — Yemen
- **Type:** Aggregated, modelled estimates 1990–2019 by year and sex (prevalence, diagnosis, treatment, control).
- **Possible role:** Background only.
- **Status:** Downloaded.

## D. Small clinical Excel dataset (~91 records)
- **Type:** Individual-level, source unknown.
- **Known limitations:** Very small, appears to contain already-diagnosed patients, provenance and sampling unverified.
- **Possible role:** Not suitable for training.
- **Status:** Set aside until provenance is verified.

## E. "Hypertension Analysis" and "Trajectory Analysis" CSVs (~197k and ~133k rows)
- **Type:** Unclear. Origin and variable definitions not confirmed; may be synthetic.
- **Known limitations:** Appear focused on pregnancy, environmental exposures and BP trajectories, not general adult screening.
- **Possible role:** Not suitable until original documentation is found.
- **Status:** Set aside.

## F. NIAID Data Discovery Portal
- **Source / link:** https://data.niaid.nih.gov/
- **Findings:** Datasets found had selected clinical populations, unclear provenance, or restricted access.
- **Status:** No candidate selected.

## G. NHANES — USA
- **Source / link:** https://wwwn.cdc.gov/nchs/nhanes/
- **Type:** Individual-level, nationally representative survey with complex sampling design (weights, strata, PSUs). Components are joined on `SEQN`.
- **Access and license:** Public.
- **Possible role:** Development (2017–March 2020) and temporal validation (2021–2023).
- **Status:** Selected (see D-004, D-005).

### Blood pressure measurement
- **Oscillometric** (Omron HEM-907XL): 3 readings, 60 s apart, after 5 min seated rest. Available 2017–2018, 2017–March 2020 (`P_BPXO`) and 2021–2023 (`BPXO_L`).
- **Auscultatory** (mercury, physician): 2017–2018 only (`BPX_J`). Discontinued after 2017–2018.
- In 2017–2018 the same participants were measured with both methods in random order (methodology study).

### Sample sizes (BP exam files, all ages ≥8, before restricting to adults)
| Period | File | Records |
|--------|------|---------|
| 2017–2018 | BPXO_J | 7,132 (6,143 with a first systolic reading) |
| 2017–March 2020 | P_BPXO | 11,656 |
| 2021–2023 | BPXO_L | 7,801 |

### Diagnosis and medication (BPQ)
- `BPQ020`: ever told by a doctor you have hypertension.
- `BPQ030`, `BPQ040A`, `BPQ050A`: asked **only** if `BPQ020` = Yes (skip pattern).
-  **Leakage risk:** these variables reveal prior diagnosis. Use them only to define the study population, never as predictors.

### Laboratory
- Fasting glucose (`GLU_J`): morning fasting subsample only. 2017–2018: 2,711 valid with non-zero fasting weight `WTSAF2YR`. Using fasting labs roughly halves the sample.
- Non-fasting labs (HbA1c, total cholesterol, HDL, creatinine): availability and sample size **to be verified**.

### Weights
- 2017–March 2020 must be analysed as one combined sample with its own pre-pandemic weights. 2019–2020 cannot be analysed alone.
- 2021–2023 uses its own cycle weights.

### Missing blood pressure (checked 2026-10-18, `notebooks/01_missing_bp.ipynb`)
Among eligible participants (adults ≥20, not pregnant, `BPQ020` = No):

| Period | Eligible | Not examined | Examined, no BP | Final cohort |
|--------|----------|--------------|-----------------|--------------|
| 2017–2020 | 5,578 | 427 | 554 | 4,597 |
| 2021–2023 | 4,815 | 1,105 | 123 | 3,587 |

- 2017–2020: all 554 "examined, no BP" are from 2019–March 2020 (none from 2017–2018). 548 of them have no BP reading at all and no arm recorded, so the measurement was not performed. The reason is not documented in the sources checked so far.
- These 554 have similar age to the final cohort (45.5 vs 45.3) but more women (60% vs 50%).
- Only 6 had a 1st reading, too few to judge whether their BP differed.
- 2021–2023: most missing participants were not examined. They are younger than the final cohort (26.7% vs 33.5% aged ≥60), so the validation cohort is slightly older.
- MEC exam weights adjust for not attending the exam, but not for a missing component within the exam.

### Known limitations
- US population only. Temporal validation is not a substitute for external validation in other populations.
- Single-visit measurement (3 readings), not clinically confirmed chronic hypertension.
- Hypertension prevalence 2017–2018 (adults ≥20, age-adjusted): 31.0% at 140/90 vs 46.6% at 130/80. Threshold choice strongly changes the outcome.

- 12% of examined eligible participants in 2017–2020 have no BP measurement (all from 2019–2020, reason unknown). Possible selection bias cannot be ruled out.

## H. WHO STEPS Microdata
- **Source / link:** https://extranet.who.int/ncdsmicrodata/
- **Type:** Individual-level (where released). Step 1 questionnaire, Step 2 physical measurements including BP, Step 3 biochemistry.
- **Access and license:** Varies by country, usually requires a request.
- **Possible role:** External validation, especially from countries in the region.
- **Status:** Availability per country not yet checked.