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
- **Type:** Individual-level, nationally representative survey with complex sampling design (weights, strata, PSUs).
- **Key variables:** demographics, examination (including measured BP), laboratory, questionnaires, medication. Components are joined on `SEQN`.
- **Access and license:** Public.
- **Possible role:** Development (primary candidate).
- **Status:** Cycle 2017–2018 under consideration. Detailed evaluation is the next step.

## H. WHO STEPS Microdata
- **Source / link:** https://extranet.who.int/ncdsmicrodata/
- **Type:** Individual-level (where released). Step 1 questionnaire, Step 2 physical measurements including BP, Step 3 biochemistry.
- **Access and license:** Varies by country, usually requires a request.
- **Possible role:** External validation, especially from countries in the region.
- **Status:** Availability per country not yet checked.