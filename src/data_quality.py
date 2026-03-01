"""Data quality checks for Consumer360."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class QualityReport:
    passed: bool
    checks: dict


def run_quality_checks(df: pd.DataFrame) -> QualityReport:
    checks = {
        "non_empty": len(df) > 0,
        "positive_quantity": bool((df["quantity"] > 0).all()) if "quantity" in df.columns else False,
        "non_negative_price": bool((df["unit_price"] >= 0).all()) if "unit_price" in df.columns else False,
        "valid_dates": bool(df["order_date"].notna().all()) if "order_date" in df.columns else False,
        "customer_coverage": df["customer_id"].nunique() > 0 if "customer_id" in df.columns else False,
    }
    return QualityReport(passed=all(checks.values()), checks=checks)
