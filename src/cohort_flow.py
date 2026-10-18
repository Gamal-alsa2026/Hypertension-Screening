"""
Count how many participants remain after each inclusion/exclusion step
defined in docs/decisions.md (D-003), for both NHANES periods.

This script only reads data/raw and prints counts. It does not save anything.

Usage (from the project root):
    python src/cohort_flow.py
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

PERIODS = {
    "2017-2020": {"demo": "P_DEMO", "bpq": "P_BPQ", "bpxo": "P_BPXO"},
    "2021-2023": {"demo": "DEMO_L", "bpq": "BPQ_L", "bpxo": "BPXO_L"},
}

NEEDED_COLUMNS = {
    "demo": ["SEQN", "RIDAGEYR", "RIDEXPRG"],
    "bpq": ["SEQN", "BPQ020"],
    "bpxo": ["SEQN", "BPXOSY2", "BPXODI2", "BPXOSY3", "BPXODI3"],
}

SBP_THRESHOLD = 140
DBP_THRESHOLD = 90


def read_xpt(period: str, name: str) -> pd.DataFrame:
    df = pd.read_sas(RAW_DIR / period / f"{name}.xpt", format="xport")
    # SAS transport stores exact zero as a tiny float (e.g. 5.4e-79). Round it.
    return df.round(6)


def check_columns(df: pd.DataFrame, kind: str, name: str) -> None:
    missing = [c for c in NEEDED_COLUMNS[kind] if c not in df.columns]
    if missing:
        raise SystemExit(f"{name}: missing expected columns {missing}")


def bp_value(sbp2, sbp3, dbp2, dbp3):
    """Mean of readings 2 and 3; reading 2 alone if 3 is missing (D-003).
    Readings of 0 are treated as missing."""
    sbp2, sbp3 = sbp2.where(sbp2 > 0), sbp3.where(sbp3 > 0)
    dbp2, dbp3 = dbp2.where(dbp2 > 0), dbp3.where(dbp3 > 0)
    sbp = pd.concat([sbp2, sbp3], axis=1).mean(axis=1, skipna=True)
    dbp = pd.concat([dbp2, dbp3], axis=1).mean(axis=1, skipna=True)
    # Require reading 2 itself to be present (D-003).
    sbp = sbp.where(sbp2.notna())
    dbp = dbp.where(dbp2.notna())
    return sbp, dbp


def flow(period: str, files: dict) -> None:
    demo = read_xpt(period, files["demo"])
    bpq = read_xpt(period, files["bpq"])
    bpxo = read_xpt(period, files["bpxo"])
    for kind, df in [("demo", demo), ("bpq", bpq), ("bpxo", bpxo)]:
        check_columns(df, kind, files[kind])

    df = demo[NEEDED_COLUMNS["demo"]].merge(bpq[NEEDED_COLUMNS["bpq"]], on="SEQN", how="left")
    df = df.merge(bpxo[NEEDED_COLUMNS["bpxo"]], on="SEQN", how="left")

    steps = []

    def step(label, mask):
        nonlocal df
        before = len(df)
        df = df[mask]
        steps.append((label, len(df), before - len(df)))

    steps.append(("All participants in demographics file", len(df), 0))
    step("Age >= 20", df["RIDAGEYR"] >= 20)
    step("Not pregnant (RIDEXPRG != 1)", df["RIDEXPRG"] != 1)
    bpq020_counts = df["BPQ020"].map(
        {1: "Yes", 2: "No", 7: "Refused", 9: "Don't know"}
    ).fillna("Missing").value_counts()
    step("Never told hypertension (BPQ020 == 2)", df["BPQ020"] == 2)

    df = df.copy()
    df["SBP"], df["DBP"] = bp_value(df["BPXOSY2"], df["BPXOSY3"], df["BPXODI2"], df["BPXODI3"])
    step("Has BP from reading 2 (and 3 if available)", df["SBP"].notna() & df["DBP"].notna())

    print(f"\n=== {period} ===")
    print(f"{'Step':<46}{'Remaining':>10}{'Removed':>10}")
    for label, remaining, removed in steps:
        print(f"{label:<46}{remaining:>10}{removed:>10}")

    positive = (df["SBP"] >= SBP_THRESHOLD) | (df["DBP"] >= DBP_THRESHOLD)
    print(f"\nOutcome at {SBP_THRESHOLD}/{DBP_THRESHOLD} (unweighted):")
    print(f"  Positive: {positive.sum()} ({positive.mean():.1%})")
    print(f"  Negative: {(~positive).sum()}")

    alt = (df["SBP"] >= 130) | (df["DBP"] >= 80)
    print(f"Sensitivity threshold 130/80 (unweighted): {alt.sum()} ({alt.mean():.1%})")

    only_reading2 = df["BPXOSY3"].isna() | (df["BPXOSY3"] <= 0)
    print(f"Participants using reading 2 only: {only_reading2.sum()}")

    print("\nBPQ020 answers among adults >=20, not pregnant (before BPQ020 filter):")
    for answer, count in bpq020_counts.items():
        print(f"  {answer:<12}{count:>6}")


def main() -> None:
    for period, files in PERIODS.items():
        flow(period, files)
    print("\nNote: counts are unweighted. They describe the sample, not the US population.")


if __name__ == "__main__":
    main()