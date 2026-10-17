import re
import pandas as pd
from pathlib import Path

ISO_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def audit_quality():
    print("=" * 65)
    print(" NSE IPO INTELLIGENCE & ANCHOR LOCK-IN - DATA QUALITY AUDIT")
    print("=" * 65)

    root = Path(__file__).parent
    pq_path = root / "output" / "ipo_issues.parquet"
    csv_path = root / "output" / "ipo_issues.csv"

    assert pq_path.exists(), "ipo_issues.parquet missing"
    assert csv_path.exists(), "ipo_issues.csv missing"

    df_pq = pd.read_parquet(pq_path)
    df_csv = pd.read_csv(csv_path)

    # 1. Parity Check
    assert len(df_pq) == len(df_csv), f"Parity mismatch: Parquet ({len(df_pq)}) != CSV ({len(df_csv)})"
    print(f"Total IPO Issues Indexed: {len(df_pq)} [PASS - 100% Parity]")

    # 2. Key Identifier Completeness
    null_sym = df_pq["symbol"].isnull().sum()
    null_comp = df_pq["company_name"].isnull().sum()
    assert null_sym == 0, f"Found {null_sym} null symbols"
    assert null_comp == 0, f"Found {null_comp} null company names"
    print("Null Symbols & Company Names: 0 [PASS]")

    # 3. ISO-8601 Temporal Consistency
    date_cols = ["issue_start_date", "issue_end_date", "listing_date", "anchor_lockin_30d_date", "anchor_lockin_90d_date"]
    for c in date_cols:
        s = df_pq[c].astype(str)
        invalid = s[~s.str.match(ISO_REGEX)]
        assert len(invalid) == 0, f"Found non-ISO dates in {c}: {len(invalid)}"
        print(f"ISO-8601 Compliance ({c}): 100% PASS")

    # 4. Microstructure Bounds
    assert (df_pq["price_band_high"] >= df_pq["price_band_low"]).all(), "Price band high < low detected"
    assert (df_pq["price_band_low"] >= 0).all(), "Negative price detected"
    assert (df_pq["issue_size_shares"] >= 0).all(), "Negative issue size detected"
    assert (df_pq["anchor_shares_allotted"] >= 0).all(), "Negative anchor shares detected"
    print("Domain Bounds (Price bands, issue sizes, anchor allocations): [PASS]")

    # 5. Timeline Order Invariant
    for _, row in df_pq.iterrows():
        assert row["anchor_lockin_90d_date"] >= row["anchor_lockin_30d_date"], f"90d < 30d lockin for {row['symbol']}"
        assert row["anchor_lockin_30d_date"] >= row["listing_date"], f"30d lockin < listing date for {row['symbol']}"
    print("Timeline Invariant (Lockin 90D >= Lockin 30D >= Listing Date): [PASS]")

    # 6. Sample Breakdown
    print("\nRecent Issues & Anchor Lock-In Schedule:")
    for _, row in df_pq.head(5).iterrows():
        print(f"  • {row['symbol']:<10} | Price: Rs.{row['price_band_high']:<6} | 30D Lockin: {row['anchor_lockin_30d_date']} | 90D: {row['anchor_lockin_90d_date']}")

    print("=" * 65)
    print("ALL AUDIT CHECKS PASSED.")
    print("=" * 65)


if __name__ == "__main__":
    audit_quality()
