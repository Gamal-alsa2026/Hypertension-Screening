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
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, SplineTransformer, StandardScaler

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

    encode = ColumnTransformer(
        [
            ("num", "passthrough", numeric),
            ("smoking", Pipeline([
                ("fill", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(drop=["never"], sparse_output=False)),
            ]), ["smoking"]),
        ],
        verbose_feature_names_out=False,
    )

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

def calibration_slope(y: np.ndarray, p: np.ndarray) -> float:
    """Slope of a logistic regression of the outcome on logit(p). Ideal = 1."""
    p = np.clip(p, 1e-6, 1 - 1e-6)
    logit = np.log(p / (1 - p)).reshape(-1, 1)
    return LogisticRegression(C=np.inf).fit(logit, y).coef_[0, 0]


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    return {
        "roc_auc": roc_auc_score(y, p),
        "pr_auc": average_precision_score(y, p),
        "brier": brier_score_loss(y, p),
        "cal_slope": calibration_slope(y, p),
        "obs_exp": y.mean() / p.mean(),   # observed / expected cases. Ideal = 1
    }


def threshold_for_sensitivity(y: np.ndarray, p: np.ndarray,
                              target: float = TARGET_SENSITIVITY) -> float:
    """Highest threshold that still reaches the target sensitivity."""
    positives = np.sort(p[y == 1])[::-1]
    k = int(np.ceil(target * len(positives)))
    return positives[k - 1]


def at_threshold(y: np.ndarray, p: np.ndarray, t: float) -> dict:
    flag = p >= t
    tp = (flag & (y == 1)).sum()
    fp = (flag & (y == 0)).sum()
    fn = (~flag & (y == 1)).sum()
    tn = (~flag & (y == 0)).sum()
    precision = tp / (tp + fp) if tp + fp else np.nan
    sensitivity = tp / (tp + fn)
    return {
        "threshold": t,
        "sensitivity": sensitivity,
        "specificity": tn / (tn + fp),
        "precision": precision,
        "f1": 2 * precision * sensitivity / (precision + sensitivity),
        "referred_pct": flag.mean() * 100,
        "screen_per_case": flag.sum() / tp if tp else np.nan,
    }


# ---------- cross-validation ----------

def cross_validate(make_model, predictors: list[str], df: pd.DataFrame,
                   n_splits: int = 5, n_repeats: int = 10) -> dict:
    """Repeated stratified CV (D-011).

    Returns:
      folds:      metrics per fold
      thresholds: per repeat, threshold for 80% sensitivity from out-of-fold
                  predictions, with sensitivity/specificity/referral at it
    """
    X = df[predictors]
    y = df[OUTCOME].to_numpy()
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats,
                                 random_state=RANDOM_STATE)

    fold_rows, oof = [], np.full((n_repeats, len(y)), np.nan)
    for i, (train, test) in enumerate(cv.split(X, y)):
        repeat = i // n_splits
        model = make_model(predictors).fit(X.iloc[train], y[train])
        p = model.predict_proba(X.iloc[test])[:, 1]
        oof[repeat, test] = p
        fold_rows.append({"repeat": repeat, **metrics(y[test], p)})

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