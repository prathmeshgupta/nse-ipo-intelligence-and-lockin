# NSE IPO Intelligence & Anchor Lock-In Expiry Dataset

[![Weekly Update](https://github.com/prathmeshgupta/nse-ipo-intelligence-and-lockin/actions/workflows/update.yml/badge.svg)](https://github.com/prathmeshgupta/nse-ipo-intelligence-and-lockin/actions/workflows/update.yml)
[![Format: Parquet](https://img.shields.io/badge/Format-Apache%20Parquet-blue.svg)](output/ipo_issues.parquet)
[![Format: CSV](https://img.shields.io/badge/Format-CSV-green.svg)](output/ipo_issues.csv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An institutional quantitative dataset capturing **Initial Public Offerings (IPOs)** across the National Stock Exchange of India (NSE). Tracks bidding subscription multiples across Qualified Institutional Buyers (QIB), Non-Institutional/HNI (NII), and Retail categories, price bands, issue sizes, anchor allocations, and calculated **30-day (50% quota) and 90-day (remaining 50% quota) anchor investor lock-in expiration dates**.

In Indian equity quantitative strategies, upcoming anchor lock-in expiries generate predictable pre-expiry selling pressure and short-horizon post-lockin mean reversion.

---

## Dataset Schema (`output/ipo_issues.parquet` / `.csv`)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `symbol` | `string` | NSE Listed/Bidding Trading Symbol (e.g. `HYUNDAI`, `BAJAJHFL`, `BONFIG`) |
| `company_name` | `string` | Official corporate entity name |
| `issue_start_date` | `string` | ISO-8601 Issue Open Date (`YYYY-MM-DD`) |
| `issue_end_date` | `string` | ISO-8601 Issue Close Date (`YYYY-MM-DD`) |
| `listing_date` | `string` | ISO-8601 Exchange Listing Date (`YYYY-MM-DD`) |
| `price_band_low` | `float64` | Lower floor price of bidding band in INR |
| `price_band_high` | `float64` | Upper cap price of bidding band in INR |
| `issue_size_shares` | `int64` | Total volume of equity shares offered |
| `qib_subscription_x` | `float64` | Qualified Institutional Buyer subscription multiple (e.g. `209.36`x) |
| `nii_subscription_x` | `float64` | Non-Institutional / HNI subscription multiple |
| `retail_subscription_x` | `float64` | Retail Individual Investor subscription multiple |
| `total_subscription_x` | `float64` | Overall issue subscription multiple |
| `anchor_shares_allotted`| `int64` | Shares allocated to anchor institutional investors |
| `anchor_lockin_30d_date`| `string` | ISO-8601 30-Day Lock-In Expiry Date (50% anchor shares released) |
| `anchor_lockin_90d_date`| `string` | ISO-8601 90-Day Lock-In Expiry Date (remaining 50% shares released) |
| `status` | `string` | Issue status (`Active`, `Closed`, `Listed`) |
| `source` | `string` | Data source identifier (`NSE_IPO_API`, `NSE_IPO_HISTORICAL`) |

---

## Quick Start (Python / Polars / DuckDB)

```python
import polars as pl

# Read directly from GitHub Raw Parquet
url = "https://github.com/prathmeshgupta/nse-ipo-intelligence-and-lockin/raw/main/output/ipo_issues.parquet"
df = pl.read_parquet(url)

# Filter for blockbuster institutional demand (> 50x QIB subscription)
blockbusters = df.filter(pl.col("qib_subscription_x") >= 50.0)
print(blockbusters.select(["symbol", "company_name", "price_band_high", "qib_subscription_x", "anchor_lockin_30d_date"]))
```
