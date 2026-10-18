"""
Build the analysis dataset for each NHANES period.

Applies the study population and outcome from D-003 and derives the
predictors from D-006 / D-007. Special codes (refused, don't know) are
converted to missing. Implausible values are NOT removed here: they are
inspected first in notebooks/02_variables.ipynb.

Output: data/processed/cohort_<period>.csv (not committed, see D-002)

Usage (from the project root):
    python src/build_dataset.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"

PERIODS = {
    "2017-2020": {"prefix": "P_", "suffix": "", "exam_weight": "WTMECPRP"},
    "2021-2023": {"prefix": "", "suffix": "_L", "exam_weight": "WTMEC2YR"},
}

SPECIAL_CODES = [7, 9, 77, 99, 777, 999, 7777, 9999, 77777, 99999]


def read(period: str, component: str) -> pd.DataFrame:
    p = PERIODS[period]
    name = f"{p['prefix']}{component}{p['suffix']}"
    # SAS transport stores exact zero as a tiny float (e.g. 5.4e-79). Round it.
    df = pd.read_sas(RAW_DIR / period / f"{name}.xpt", format="xport").round(6)
    df.columns = [c.upper() for c in df.columns]
    return df


def clean_codes(s: pd.Series, codes=SPECIAL_CODES) -> pd.Series:
    """Turn refused / don't know codes into missing."""
    return s.where(~s.isin(codes))


def decode_bytes(s: pd.Series) -> pd.Series:
    return s.map(lambda v: v.decode().strip() if isinstance(v, bytes) else v).replace("", np.nan)


# ---------- population and outcome (D-003) ----------

def population_and_outcome(period: str) -> pd.DataFrame:
    w = PERIODS[period]["exam_weight"]
    demo = read(period, "DEMO")[["SEQN", "RIDAGEYR", "RIAGENDR", "RIDEXPRG",
                                 w, "SDMVSTRA", "SDMVPSU"]]
    bpq = read(period, "BPQ")[["SEQN", "BPQ020"]]
    bpxo = read(period, "BPXO")[["SEQN", "BPXOSY2", "BPXOSY3", "BPXODI2", "BPXODI3"]]

    df = demo.merge(bpq, on="SEQN", how="left").merge(bpxo, on="SEQN", how="left")
    df = df[(df["RIDAGEYR"] >= 20) & (df["RIDEXPRG"] != 1) & (df["BPQ020"] == 2)].copy()

    for c in ["BPXOSY2", "BPXOSY3", "BPXODI2", "BPXODI3"]:
        df[c] = df[c].where(df[c] > 0)
    df["sbp"] = df[["BPXOSY2", "BPXOSY3"]].mean(axis=1).where(df["BPXOSY2"].notna())
    df["dbp"] = df[["BPXODI2", "BPXODI3"]].mean(axis=1).where(df["BPXODI2"].notna())
    df = df[df["sbp"].notna() & df["dbp"].notna()]

    df["outcome_140_90"] = ((df["sbp"] >= 140) | (df["dbp"] >= 90)).astype(int)
    df["outcome_130_80"] = ((df["sbp"] >= 130) | (df["dbp"] >= 80)).astype(int)

    out = pd.DataFrame({
        "SEQN": df["SEQN"],
        "age": df["RIDAGEYR"],
        "female": (df["RIAGENDR"] == 2).astype(int),
        "sbp": df["sbp"],
        "dbp": df["dbp"],
        "outcome_140_90": df["outcome_140_90"],
        "outcome_130_80": df["outcome_130_80"],
        "exam_weight": df[w],
        "strata": df["SDMVSTRA"],
        "psu": df["SDMVPSU"],
    })
    return out


# ---------- predictors (D-006, D-007) ----------

def body(period: str) -> pd.DataFrame:
    bmx = read(period, "BMX")
    return pd.DataFrame({"SEQN": bmx["SEQN"], "bmi": bmx["BMXBMI"], "waist": bmx["BMXWAIST"]})


def smoking(period: str) -> pd.DataFrame:
    """never = <100 cigarettes in life; former = 100+ but not now; current = every day / some days."""
    smq = read(period, "SMQ")
    ever = clean_codes(smq["SMQ020"])
    now = clean_codes(smq["SMQ040"])
    status = pd.Series(np.nan, index=smq.index, dtype="object")
    status[ever == 2] = "never"
    status[(ever == 1) & (now == 3)] = "former"
    status[(ever == 1) & now.isin([1, 2])] = "current"
    return pd.DataFrame({"SEQN": smq["SEQN"], "smoking": status})


def diabetes(period: str) -> pd.DataFrame:
    """Diagnosed diabetes = DIQ010 == 1. Borderline (3) is counted as no."""
    diq = read(period, "DIQ")
    code = clean_codes(diq["DIQ010"])
    value = code.map({1: 1, 2: 0, 3: 0})
    return pd.DataFrame({"SEQN": diq["SEQN"], "diabetes": value})


def activity(period: str) -> pd.DataFrame:
    """Harmonised leisure-time activity (D-007):
    ltpa_min_week = moderate minutes/week + 2 x vigorous minutes/week
    (vigorous counted double, as in WHO activity guidelines);
    sitting_min_day = usual minutes sitting per day."""
    paq = read(period, "PAQ")
    sitting = clean_codes(paq["PAD680"], [7777, 9999])
    sitting = sitting.where(sitting <= 1200)  # >20 h/day is implausible (D-009)

    if period == "2017-2020":
        def weekly(flag, days, minutes):
            f = clean_codes(paq[flag], [7, 9])
            d = clean_codes(paq[days], [77, 99])
            m = clean_codes(paq[minutes], [7777, 9999])
            val = d * m
            return val.where(f == 1, np.where(f == 2, 0, np.nan))

        moderate = weekly("PAQ665", "PAQ670", "PAD675")
        vigorous = weekly("PAQ650", "PAQ655", "PAD660")
    else:
        per_week = {"D": 7.0, "W": 1.0, "M": 12 / 52, "Y": 1 / 52}

        def weekly(freq, unit, minutes):
            q = clean_codes(paq[freq], [7777, 9999])
            u = decode_bytes(paq[unit]).map(per_week)
            m = clean_codes(paq[minutes], [7777, 9999])
            val = q * u * m
            return val.where(q != 0, 0.0)

        moderate = weekly("PAD790Q", "PAD790U", "PAD800")
        vigorous = weekly("PAD810Q", "PAD810U", "PAD820")

    return pd.DataFrame({
        "SEQN": paq["SEQN"],
        "ltpa_min_week": moderate + 2 * vigorous,
        "sitting_min_day": sitting,
    })


def labs(period: str) -> pd.DataFrame:
    ghb = read(period, "GHB")[["SEQN", "LBXGH"]]
    tc = read(period, "TCHOL")[["SEQN", "LBXTC"]]
    hdl = read(period, "HDL")[["SEQN", "LBDHDD"]]
    bio = read(period, "BIOPRO")[["SEQN", "LBXSCR"]]
    df = ghb.merge(tc, on="SEQN", how="outer").merge(hdl, on="SEQN", how="outer") \
            .merge(bio, on="SEQN", how="outer")
    return df.rename(columns={"LBXGH": "hba1c", "LBXTC": "total_chol",
                              "LBDHDD": "hdl", "LBXSCR": "creatinine"})


def build(period: str) -> pd.DataFrame:
    df = population_and_outcome(period)
    for part in [body, smoking, diabetes, activity, labs]:
        df = df.merge(part(period), on="SEQN", how="left")
    df.insert(1, "period", period)
    return df


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for period in PERIODS:
        df = build(period)
        path = OUT_DIR / f"cohort_{period}.csv"
        df.to_csv(path, index=False)
        print(f"{period}: {len(df)} rows, {df.shape[1]} columns -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()