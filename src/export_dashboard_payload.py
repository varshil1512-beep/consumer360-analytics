"""Export analytics reports into a single frontend payload JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def export_dashboard_payload(report_dir: Path, frontend_data_dir: Path) -> Path:
    frontend_data_dir.mkdir(parents=True, exist_ok=True)

    def records(name: str) -> list[dict]:
        df = _read_csv(report_dir / name)
        if df.empty:
            return []
        # Browser JSON.parse fails on NaN; convert all missing values to null.
        df = df.astype(object).where(pd.notna(df), None)
        return df.to_dict(orient="records")

    payload = {
        "sales_trend": records("sales_trend.csv"),
        "revenue_by_region": records("revenue_by_region.csv"),
        "top_products_revenue": records("top_products_revenue.csv"),
        "top_products_volume": records("top_products_volume.csv"),
        "rfm": records("customer_rfm_segments.csv"),
        "cohort": records("cohort_retention.csv"),
        "market_basket": records("market_basket_rules.csv"),
        "clv": records("customer_clv.csv"),
        "champions": records("campaign_champions.csv"),
        "churn_risk": records("campaign_churn_risk.csv"),
        "kpi_summary": {},
    }

    summary_path = report_dir / "kpi_summary.json"
    if summary_path.exists():
        payload["kpi_summary"] = json.loads(summary_path.read_text(encoding="utf-8"))

    out_path = frontend_data_dir / "dashboard_payload.json"
    out_path.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    return out_path
