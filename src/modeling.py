"""
Shared modelling code: predictor sets, pipelines and evaluation.

Follows docs/decisions.md:
  D-010  predictor sets (Model A, Model B)
  D-011  imputation inside the pipeline, repeated stratified CV,
         threshold at 80% sensitivity from out-of-fold predictions
  D-012  models trained without survey weights
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import (RandomizedSearchCV, RepeatedStratifiedKFold,
                                     StratifiedKFold)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, SplineTransformer, StandardScaler
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"

OUTCOME = "outcome_140_90"

# D-010
MODEL_A = ["age", "female", "waist", "smoking", "sitting_min_day", "diabetes"]
LABS = ["hba1c", "total_chol", "hdl", "creatinine"]
MODEL_B = MODEL_A + LABS

SPLINE_COLS = ["age", "waist"]   # allowed to be non-linear (D-011)
TARGET_SENSITIVITY = 0.80        # D-011
RANDOM_STATE = 42


def load(period: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / f"cohort_{period}.csv")


# ---------- pipeline ----------

def make_logistic(predictors: list[str]) -> Pipeline:
    """Impute -> splines for age/waist + scale the rest -> logistic regression."""
    numeric = [c for c in predictors if c != "smoking"]

    parts = [("num", "passthrough", numeric)]
    if "smoking" in predictors:
        parts.append(("smoking", Pipeline([
            ("fill", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(drop=["never"], sparse_output=False)),
        ]), ["smoking"]))
    encode = ColumnTransformer(parts, verbose_feature_names_out=False)

    impute = IterativeImputer(max_iter=10, random_state=RANDOM_STATE)

    spline = [c for c in SPLINE_COLS if c in predictors]
    shape = ColumnTransformer(
        [
            ("spline", SplineTransformer(n_knots=4, degree=3), spline),
        ],
        remainder=StandardScaler(),
        verbose_feature_names_out=False,
    )

    pipe = Pipeline([
        ("encode", encode),
        ("impute", impute),
        ("shape", shape),
        ("model", LogisticRegression(C=np.inf, max_iter=5000)),
    ])
    pipe.set_output(transform="pandas")
    return pipe


# ---------- metrics ----------

def calibration_slope(y: np.ndarray, p: np.ndarray, w: np.ndarray | None = None) -> float:
    """Slope of a logistic regression of the outcome on logit(p). Ideal = 1."""
    p = np.clip(p, 1e-6, 1 - 1e-6)
    logit = np.log(p / (1 - p)).reshape(-1, 1)
    return LogisticRegression(C=np.inf).fit(logit, y, sample_weight=w).coef_[0, 0]


def metrics(y: np.ndarray, p: np.ndarray, w: np.ndarray | None = None) -> dict:
    """w = optional survey weights (D-012). None = unweighted."""
    return {
        "roc_auc": roc_auc_score(y, p, sample_weight=w),
        "pr_auc": average_precision_score(y, p, sample_weight=w),
        "brier": brier_score_loss(y, p, sample_weight=w),
        "cal_slope": calibration_slope(y, p, w),
        # observed / expected cases. Ideal = 1
        "obs_exp": np.average(y, weights=w) / np.average(p, weights=w),
    }


def threshold_for_sensitivity(y: np.ndarray, p: np.ndarray,
                              target: float = TARGET_SENSITIVITY) -> float:
    """Highest threshold that still reaches the target sensitivity."""
    positives = np.sort(p[y == 1])[::-1]
    k = int(np.ceil(target * len(positives)))
    return positives[k - 1]


def at_threshold(y: np.ndarray, p: np.ndarray, t: float,
                 w: np.ndarray | None = None) -> dict:
    """w = optional survey weights (D-012). None = unweighted."""
    w = np.ones(len(y)) if w is None else np.asarray(w, dtype=float)
    flag = p >= t
    tp = w[flag & (y == 1)].sum()
    fp = w[flag & (y == 0)].sum()
    fn = w[~flag & (y == 1)].sum()
    tn = w[~flag & (y == 0)].sum()
    precision = tp / (tp + fp) if tp + fp else np.nan
    sensitivity = tp / (tp + fn)
    return {
        "threshold": t,
        "sensitivity": sensitivity,
        "specificity": tn / (tn + fp),
        "precision": precision,
        "f1": 2 * precision * sensitivity / (precision + sensitivity),
        "referred_pct": w[flag].sum() / w.sum() * 100,
        "screen_per_case": w[flag].sum() / tp if tp else np.nan,
    }



# ---------- cross-validation ----------

def cross_validate(make_model, predictors: list[str], df: pd.DataFrame,
                   n_splits: int = 5, n_repeats: int = 10,
                   outcome: str = OUTCOME, verbose: bool = False) -> dict:
    """Repeated stratified CV (D-011).

    Returns:
      folds:      metrics per fold
      thresholds: per repeat, threshold for 80% sensitivity from out-of-fold
                  predictions, with sensitivity/specificity/referral at it
    """
    X = df[predictors]
    y = df[outcome].to_numpy()
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats,
                                 random_state=RANDOM_STATE)

    fold_rows, oof = [], np.full((n_repeats, len(y)), np.nan)
    for i, (train, test) in enumerate(cv.split(X, y)):
        repeat = i // n_splits
        model = make_model(predictors).fit(X.iloc[train], y[train])
        p = model.predict_proba(X.iloc[test])[:, 1]
        oof[repeat, test] = p
        fold_rows.append({"repeat": repeat, **metrics(y[test], p)})
        if verbose and (i + 1) % n_splits == 0:
            print(f"  repeat {repeat + 1}/{n_repeats} done", flush=True)

    threshold_rows = []
    for r in range(n_repeats):
        t = threshold_for_sensitivity(y, oof[r])
        threshold_rows.append({"repeat": r, **at_threshold(y, oof[r], t)})

    return {"folds": pd.DataFrame(fold_rows),
            "thresholds": pd.DataFrame(threshold_rows)}


def summarise(result: dict) -> pd.DataFrame:
    """Mean and 2.5 / 97.5 percentiles across folds or repeats."""
    rows = {}
    for key in ["folds", "thresholds"]:
        d = result[key].drop(columns="repeat")
        for col in d.columns:
            rows[col] = {"mean": d[col].mean(),
                         "low": d[col].quantile(0.025),
                         "high": d[col].quantile(0.975)}
    return pd.DataFrame(rows).T


# ---------- tree models (D-011) ----------

def _tree_preprocess(predictors: list[str]) -> list:
    """Same encoding and imputation as the logistic pipeline, no splines/scaling
    (trees do not need them)."""
    numeric = [c for c in predictors if c != "smoking"]
    parts = [("num", "passthrough", numeric)]
    if "smoking" in predictors:
        parts.append(("smoking", Pipeline([
            ("fill", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(drop=["never"], sparse_output=False)),
        ]), ["smoking"]))
    return [
        ("encode", ColumnTransformer(parts, verbose_feature_names_out=False)),
        ("impute", IterativeImputer(max_iter=10, random_state=RANDOM_STATE)),
    ]


def _tuned(pipe: Pipeline, grid: dict, n_iter: int = 8) -> RandomizedSearchCV:
    """Hyperparameters tuned by an inner 3-fold CV on the training fold only
    (nested CV, D-011). Selection by ROC-AUC."""
    return RandomizedSearchCV(
        pipe, grid, n_iter=n_iter, scoring="roc_auc",
        cv=StratifiedKFold(3, shuffle=True, random_state=RANDOM_STATE),
        random_state=RANDOM_STATE, n_jobs=-1,
    )


def make_random_forest(predictors: list[str]) -> RandomizedSearchCV:
    pipe = Pipeline(_tree_preprocess(predictors) + [
        ("model", RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE)),
    ])
    grid = {
        "model__min_samples_leaf": [10, 20, 40, 80],
        "model__max_features": ["sqrt", 0.5, 1.0],
        "model__max_depth": [4, 6, 8, None],
    }
    return _tuned(pipe, grid)


def make_xgboost(predictors: list[str]) -> RandomizedSearchCV:
    pipe = Pipeline(_tree_preprocess(predictors) + [
        ("model", XGBClassifier(n_estimators=300, eval_metric="logloss",
                                random_state=RANDOM_STATE, n_jobs=1)),
    ])
    grid = {
        "model__max_depth": [2, 3, 4],
        "model__learning_rate": [0.01, 0.03, 0.1],
        "model__min_child_weight": [5, 10, 20],
        "model__subsample": [0.7, 1.0],
        "model__colsample_bytree": [0.7, 1.0],
    }
    return _tuned(pipe, grid)