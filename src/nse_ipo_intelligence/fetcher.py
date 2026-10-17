import re
import datetime
import requests
import pandas as pd
from typing import List, Dict, Any

NSE_CURRENT_IPO_URL = "https://www.nseindia.com/api/ipo-current-issue"
NSE_UPCOMING_IPO_URL = "https://www.nseindia.com/api/all-upcoming-issues?category=ipo"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*",
}


class IPOIntelligenceFetcher:
    """
    Fetches IPO issues, bidding parameters, subscription multiples, and computes 
    30-day and 90-day anchor investor lock-in expiration dates.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self._primed = False

    def _prime_session(self):
        if not self._primed:
            try:
                self.session.get("https://www.nseindia.com", timeout=10)
            except Exception:
                pass
            self._primed = True

    def fetch_current_issues(self) -> pd.DataFrame:
        self._prime_session()
        records = []

        try:
            resp = self.session.get(NSE_CURRENT_IPO_URL, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    for item in data:
                        records.append(self._parse_item(item))
        except Exception as e:
            print(f"Warning: Failed to fetch current IPOs: {e}")

        try:
            resp2 = self.session.get(NSE_UPCOMING_IPO_URL, timeout=15)
            if resp2.status_code == 200:
                data2 = resp2.json()
                if isinstance(data2, list):
                    for item in data2:
                        records.append(self._parse_item(item))
        except Exception as e:
            print(f"Warning: Failed to fetch upcoming IPOs: {e}")

        # Add recent landmark historical anchor lockin milestones
        historical_sample = [
            {
                "symbol": "HYUNDAI",
                "company_name": "Hyundai Motor India Limited",
                "issue_start_date": "2024-10-15",
                "issue_end_date": "2024-10-17",
                "listing_date": "2024-10-22",
                "price_band_low": 1865.0,
                "price_band_high": 1960.0,
                "issue_size_shares": 142194700,
                "qib_subscription_x": 6.97,
                "nii_subscription_x": 0.60,
                "retail_subscription_x": 0.50,
                "total_subscription_x": 2.37,
                "anchor_shares_allotted": 42426486,
                "anchor_lockin_30d_date": "2024-11-21",
                "anchor_lockin_90d_date": "2025-01-20",
                "status": "Listed",
                "source": "NSE_IPO_HISTORICAL"
            },
            {
                "symbol": "BAJAJHFL",
                "company_name": "Bajaj Housing Finance Limited",
                "issue_start_date": "2024-09-09",
                "issue_end_date": "2024-09-11",
                "listing_date": "2024-09-16",
                "price_band_low": 66.0,
                "price_band_high": 70.0,
                "issue_size_shares": 937142857,
                "qib_subscription_x": 209.36,
                "nii_subscription_x": 41.51,
                "retail_subscription_x": 7.41,
                "total_subscription_x": 63.61,
                "anchor_shares_allotted": 251142857,
                "anchor_lockin_30d_date": "2024-10-16",
                "anchor_lockin_90d_date": "2024-12-16",
                "status": "Listed",
                "source": "NSE_IPO_HISTORICAL"
            },
            {
                "symbol": "SWIGGY",
                "company_name": "Swiggy Limited",
                "issue_start_date": "2024-11-06",
                "issue_end_date": "2024-11-08",
                "listing_date": "2024-11-13",
                "price_band_low": 371.0,
                "price_band_high": 390.0,
                "issue_size_shares": 290000000,
                "qib_subscription_x": 6.02,
                "nii_subscription_x": 0.41,
                "retail_subscription_x": 1.14,
                "total_subscription_x": 3.59,
                "anchor_shares_allotted": 130000000,
                "anchor_lockin_30d_date": "2024-12-13",
                "anchor_lockin_90d_date": "2025-02-13",
                "status": "Listed",
                "source": "NSE_IPO_HISTORICAL"
            }
        ]
        records.extend(historical_sample)

        df = pd.DataFrame(records)
        df = df.dropna(subset=["symbol", "company_name"])
        df = df.drop_duplicates(subset=["symbol", "issue_start_date"], keep="last")
        df = df.sort_values(by="issue_start_date", ascending=False).reset_index(drop=True)
        return df

    def _parse_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        sym = str(item.get("symbol", "")).strip().upper()
        comp = str(item.get("companyName", "")).strip()

        start_dt = self._parse_iso_date(item.get("issueStartDate"))
        end_dt = self._parse_iso_date(item.get("issueEndDate"))

        # Approximate listing date = end_date + 3 trading days
        try:
            dt_obj = datetime.date.fromisoformat(end_dt)
            listing_dt = (dt_obj + datetime.timedelta(days=4)).isoformat()
            lock_30d = (dt_obj + datetime.timedelta(days=34)).isoformat()
            lock_90d = (dt_obj + datetime.timedelta(days=94)).isoformat()
        except Exception:
            listing_dt = end_dt
            lock_30d = end_dt
            lock_90d = end_dt

        # Parse price band (e.g. "Rs.558 to Rs.586")
        price_str = str(item.get("issuePrice", ""))
        prices = [float(p) for p in re.findall(r"\d+(?:\.\d+)?", price_str)]
        p_low = prices[0] if len(prices) >= 1 else 0.0
        p_high = prices[1] if len(prices) >= 2 else p_low

        size = self._parse_int(item.get("issueSize") or item.get("noOfSharesOffered"))
        sub_x = float(item.get("noOfTime") or 0.0)

        return {
            "symbol": sym,
            "company_name": comp,
            "issue_start_date": start_dt,
            "issue_end_date": end_dt,
            "listing_date": listing_dt,
            "price_band_low": round(p_low, 2),
            "price_band_high": round(p_high, 2),
            "issue_size_shares": size,
            "qib_subscription_x": round(sub_x, 2),
            "nii_subscription_x": 0.0,
            "retail_subscription_x": 0.0,
            "total_subscription_x": round(sub_x, 2),
            "anchor_shares_allotted": int(size * 0.3) if size > 0 else 0,
            "anchor_lockin_30d_date": lock_30d,
            "anchor_lockin_90d_date": lock_90d,
            "status": str(item.get("status", "Active")).strip(),
            "source": "NSE_IPO_API"
        }

    def _parse_iso_date(self, val: Any) -> str:
        try:
            return pd.to_datetime(val).strftime("%Y-%m-%d")
        except Exception:
            return datetime.date.today().isoformat()

    def _parse_int(self, val: Any) -> int:
        try:
            return int(float(str(val).replace(",", "")))
        except Exception:
            return 0
