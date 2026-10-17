"""
Automated Weekly Dataset Updater for nse-ipo-intelligence-and-lockin
Can be executed locally or via GitHub Actions.
Zero credentials required.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
from nse_ipo_intelligence.fetcher import IPOIntelligenceFetcher

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILE = OUTPUT_DIR / "ipo_issues.csv"
PARQUET_FILE = OUTPUT_DIR / "ipo_issues.parquet"


def update():
    print("[1/3] Fetching latest IPO issues & bidding subscription multiples from NSE...")
    fetcher = IPOIntelligenceFetcher()
    new_df = fetcher.fetch_current_issues()
    print(f"      Retrieved {len(new_df)} IPO issues.")

    print("[2/3] Merging and saving updated IPO intelligence datasets...")
    if CSV_FILE.exists():
        existing_df = pd.read_csv(CSV_FILE)
        combined = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined = new_df.copy()

    combined = combined.drop_duplicates(subset=["symbol", "issue_start_date"], keep="last")
    combined = combined.sort_values(by="issue_start_date", ascending=False)

    combined.to_csv(CSV_FILE, index=False)
    combined.to_parquet(PARQUET_FILE, index=False)
    print(f"      Saved {len(combined)} records to {CSV_FILE.name} and {PARQUET_FILE.name}.")

    print("[3/3] Running automated quality audit...")
    from evaluate_quality import audit_quality
    audit_quality()
    print("Update complete successfully.")


if __name__ == "__main__":
    update()
