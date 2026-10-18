"""
Download the NHANES component files needed for this project.

Files are saved to data/raw/<period>/ and are NOT committed to Git (see D-002).
Running the script again skips files that are already downloaded.

Usage (from the project root):
    python src/download_nhanes.py
"""

from pathlib import Path

import requests

BASE_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public"

# Component files per period (see docs/decisions.md D-003 to D-006).
PERIODS = {
    # Development data: 2017 - March 2020 pre-pandemic (D-004)
    "2017-2020": {
        "year_folder": "2017",
        "files": [
            "P_DEMO",   # demographics, age, sex, pregnancy, survey weights
            "P_BPXO",   # oscillometric blood pressure (outcome)
            "P_BPQ",    # BP / cholesterol questionnaire (population definition)
            "P_BMX",    # body measures: BMI, waist
            "P_SMQ",    # smoking
            "P_PAQ",    # physical activity
            "P_DIQ",    # diabetes
            "P_MCQ",    # medical conditions, family history
            "P_GHB",    # HbA1c
            "P_TCHOL",  # total cholesterol
            "P_HDL",    # HDL cholesterol
            "P_BIOPRO", # biochemistry profile (creatinine) - to be verified
        ],
    },
    # Temporal validation data: August 2021 - August 2023 (D-004)
    "2021-2023": {
        "year_folder": "2021",
        "files": [
            "DEMO_L",
            "BPXO_L",
            "BPQ_L",
            "BMX_L",
            "SMQ_L",
            "PAQ_L",
            "DIQ_L",
            "MCQ_L",
            "GHB_L",
            "TCHOL_L",
            "HDL_L",
            "BIOPRO_L",
        ],
    },
}

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def is_xpt(content: bytes) -> bool:
    """SAS transport files start with a fixed header. CDC returns an HTML page
    instead when a file does not exist, so we check before saving."""
    return content.startswith(b"HEADER RECORD")


def download_file(name: str, year_folder: str, out_dir: Path) -> str:
    out_path = out_dir / f"{name}.xpt"
    if out_path.exists():
        return "already downloaded"

    url = f"{BASE_URL}/{year_folder}/DataFiles/{name}.xpt"
    response = requests.get(url, timeout=120)

    if response.status_code != 200:
        return f"FAILED (HTTP {response.status_code})"
    if not is_xpt(response.content):
        return "FAILED (not an XPT file - may not exist for this period)"

    out_path.write_bytes(response.content)
    size_mb = len(response.content) / 1_000_000
    return f"ok ({size_mb:.1f} MB)"


def main() -> None:
    failed = []
    for period, info in PERIODS.items():
        out_dir = RAW_DIR / period
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n=== {period} ===")
        for name in info["files"]:
            status = download_file(name, info["year_folder"], out_dir)
            print(f"  {name:<10} {status}")
            if status.startswith("FAILED"):
                failed.append(f"{period}/{name}")

    print("\nDone.")
    if failed:
        print("Not downloaded:", ", ".join(failed))


if __name__ == "__main__":
    main()