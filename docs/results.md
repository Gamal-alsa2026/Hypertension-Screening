# Results Log

Results are recorded as they are produced, including results that do not favour the models.
All results below are from 2017–2020 (development data), unweighted, using repeated stratified 5-fold cross-validation with 10 repeats (D-011). The 2021–2023 validation data has not been used yet.

---

## R-001 — Logistic regression vs simple age baselines
- **Date:** 2026-10-21
- **Notebooks:** `notebooks/04_logistic_cv.ipynb`, `notebooks/05_baselines.ipynb`
- **Outcome:** undiagnosed BP ≥140/90 (D-003). Sensitivity fixed at 80% (D-011).

| Approach | ROC-AUC | Calibration slope | Observed / expected | Specificity | Referred | Screened per case |
|---|---|---|---|---|---|---|
| Rule: refer everyone aged ≥43 | 0.733 | – | – | 0.526 | 52.0% | 4.7 |
| Logistic: age only | 0.733 | 0.99 | 1.00 | 0.537 | 50.9% | 4.7 |
| Logistic: age + sex | 0.736 | 0.99 | 1.00 | 0.535 | 51.0% | 4.7 |
| **Model A** (no lab) | 0.744 | 0.96 | 1.00 | 0.556 | 49.2% | 4.6 |
| **Model B** (with lab) | 0.748 | 0.94 | 1.00 | 0.563 | 48.6% | 4.5 |

### Findings
- **Age carries most of the information.** Model A improves ROC-AUC by 0.011 over age alone and reduces referrals by about 3 percentage points compared with a simple age rule.
- **Laboratory data adds almost nothing** (Model B vs A: +0.004 ROC-AUC). By the simplicity rule in D-011, Model A is preferred over Model B.
- **Calibration is good** for all logistic models (slope 0.94–0.99, observed/expected 1.00).
- At 80% sensitivity, about half of the population is referred for BP measurement.

### Interpretation (to be tested)
1. People with strong risk factors (e.g. obesity, diabetes) may already have been diagnosed and are excluded by D-003, leaving undiagnosed cases that are harder to distinguish. → Test by refitting on all adults, including diagnosed participants.
2. Important predictors are missing or unusable: physical activity, family history, salt intake, khat.

### Implications
- A simple age-based rule performs almost as well as the models in this data.
- The practical value of a model is in prioritising BP measurement where devices or staff are limited, not in replacing measurement.
- Whether other factors relevant in Yemen add information beyond age can only be answered with Yemeni data.

## R-002 — Why the models add little over age: undiagnosed vs all adults
- **Date:** 2026-10-21
- **Notebook:** `notebooks/06_all_adults.ipynb`
- **Purpose:** Explanatory analysis only, testing interpretation 1 of R-001. Not a screening model.
- **Data:** 2017–2020. "All adults" adds participants already told they have hypertension (`BPQ020` = Yes). Outcome for all adults: diagnosed **or** measured BP ≥140/90 (47.3% positive, n = 7,551).

| | ROC-AUC undiagnosed | ROC-AUC all adults | Gain over age, undiagnosed | Gain over age, all adults |
|---|---|---|---|---|
| Age only | 0.733 | 0.770 | – | – |
| Age + sex | 0.736 | 0.770 | 0.002 | 0.000 |
| Model A | 0.744 | 0.801 | 0.011 | 0.031 |
| Model B | 0.748 | 0.804 | 0.014 | 0.033 |

| Median / % | Never told (n = 4,597) | Diagnosed (n = 2,954) |
|---|---|---|
| Age | 43 | 62 |
| Waist (cm) | 95.9 | 105.5 |
| Diabetes | 7.7% | 27.7% |
| HbA1c | 5.5 | 5.8 |

### Findings
- The gain of Model A over age is about three times larger when diagnosed participants are included (0.031 vs 0.011).
- Diagnosed participants are older, have larger waists and much more diabetes.
- This supports interpretation 1: people with clear risk factors are more likely to have been diagnosed already, so the remaining undiagnosed cases are harder to distinguish from age alone.

### Caveats
- Part of the stronger association in all adults may reflect **detection**, not disease: people with diabetes visit doctors more often, so their hypertension is more likely to be found.
- Diagnosed participants may have changed weight or lifestyle after diagnosis.

### Hypothesis for Yemen (untested)
- In settings with low diagnosis rates, such as Yemen (see NCD-RisC estimates), the undiagnosed population may resemble "all adults" more than the US undiagnosed population does. Risk factors may then add more information beyond age than they do in NHANES. This can only be tested with Yemeni data.

## R-003 — Logistic regression vs random forest vs XGBoost
- **Date:** 2026-10-21
- **Notebook:** `notebooks/07_model_comparison.ipynb`
- **Setup:** Repeated stratified 5-fold CV × 10 (D-011). Tree models tuned with nested 3-fold randomized search (8 settings) inside each training fold.

| Set | Model | ROC-AUC (2.5–97.5%) | PR-AUC | Brier | Cal. slope | Obs/Exp | Specificity | Referred | Screened per case |
|---|---|---|---|---|---|---|---|---|---|
| A | Logistic | 0.744 (0.702–0.775) | 0.283 | 0.107 | 0.96 | 1.00 | 0.556 | 49.2% | 4.56 |
| A | Random forest | 0.742 (0.708–0.772) | 0.295 | 0.107 | 1.15 | 1.00 | 0.545 | 50.1% | 4.65 |
| A | XGBoost | 0.743 (0.706–0.776) | 0.294 | 0.106 | 1.08 | 1.00 | 0.550 | 49.8% | 4.61 |
| B | Logistic | 0.748 (0.703–0.775) | 0.284 | 0.107 | 0.94 | 1.00 | 0.563 | 48.6% | 4.50 |
| B | Random forest | 0.744 (0.707–0.778) | 0.303 | 0.106 | 1.16 | 1.00 | 0.556 | 49.2% | 4.56 |
| B | XGBoost | 0.743 (0.702–0.773) | 0.296 | 0.106 | 1.13 | 1.00 | 0.553 | 49.5% | 4.58 |

### Findings
- All models have practically the same discrimination (differences < 0.006, well within fold-to-fold variation).
- Logistic regression has the best calibration slope (0.94–0.96). Tree models have slopes above 1 (1.08–1.16): their predicted risks are too close to the average.
- Tree models have slightly higher PR-AUC (about +0.01), a secondary metric.
- No sign of important non-linear effects or interactions beyond what logistic regression with splines captures.

## R-004 — Temporal validation on 2021–2023 (primary result)
- **Date:** 2026-10-25
- **Notebook:** `notebooks/08_temporal_validation.ipynb`
- **Pre-specified (D-013):** logistic regression, Model A, fitted on all 2017–2020 data. Thresholds fixed from 2017–2020 out-of-fold predictions (Model A: 0.106; Model B: 0.105; age rule: age ≥43). Run once; nothing was changed after seeing these results.
- **Data:** development n = 4,597 (13.5% positive); validation n = 3,587 (10.6% positive).

### Unweighted (primary)
| | ROC-AUC | PR-AUC | Brier | Cal. slope | Obs/Exp | Sensitivity | Specificity | Precision | Referred | Screened per case |
|---|---|---|---|---|---|---|---|---|---|---|
| **Model A (final)** | 0.709 | 0.191 | 0.095 | 0.83 | 0.70 | 0.822 | 0.479 | 0.158 | 55.3% | 6.3 |
| Model B | 0.717 | 0.201 | 0.094 | 0.84 | 0.69 | 0.827 | 0.478 | 0.159 | 55.4% | 6.3 |
| Age rule (≥43) | 0.700 | – | – | – | – | 0.832 | 0.445 | 0.151 | 58.4% | 6.6 |

Model A, bootstrap 95% intervals (1,000 resamples): ROC-AUC 0.684–0.733; calibration slope 0.71–0.95; observed/expected 0.64–0.76; sensitivity 0.78–0.86; referred 53.7–57.0%.

### Weighted with MEC exam weights (secondary)
| | ROC-AUC | Cal. slope | Obs/Exp | Sensitivity | Specificity | Referred |
|---|---|---|---|---|---|---|
| Model A (final) | 0.730 | 0.89 | 0.68 | 0.779 | 0.577 | 45.4% |
| Model B | 0.739 | 0.90 | 0.67 | 0.792 | 0.576 | 45.5% |
| Age rule | 0.716 | – | – | 0.770 | 0.547 | 48.1% |

### Calibration by predicted-risk decile (Model A, unweighted)
| Decile | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Predicted % | 2.6 | 3.9 | 5.6 | 7.8 | 10.7 | 14.3 | 18.0 | 22.4 | 28.2 | 38.5 |
| Observed % | 1.1 | 3.1 | 3.9 | 6.4 | 9.7 | 10.6 | 11.4 | 17.3 | 18.1 | 24.5 |

### Findings
- **Discrimination decreased** from 0.744 (internal CV) to 0.709. Ranking of risk transported moderately.
- **The model overestimates risk** by about 40% (observed/expected 0.70), most strongly in the highest-risk groups. The calibration slope of 0.83 shows predictions are too extreme.
- This matches the lower hypertension rate in 2021–2023, especially among older adults (D-010).
- Because risks are overestimated, the fixed threshold referred more people (55% vs 49% in development) and sensitivity was above target (82%).
- Model A still adds little over the age rule (+0.009 ROC-AUC). Model B again adds little over Model A (+0.008).

### Implications
- Even within the same country and survey, after about three years, the model needed recalibration. A model developed in NHANES cannot be assumed valid in another population, such as Yemen, without local validation and updating.
- Relative risk ranking is more transportable than absolute risk.