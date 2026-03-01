"""Core KPI calculations for Consumer360."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class KPIArtifacts:
    sales_trend: pd.DataFrame
    top_products_volume: pd.DataFrame
    top_products_revenue: pd.DataFrame
    revenue_by_region: pd.DataFrame
    summary: dict


def compute_kpis(df: pd.DataFrame) -> KPIArtifacts:
    base = df.copy()
    base["order_month"] = base["order_date"].dt.to_period("M").dt.to_timestamp()

    sales_trend = (
        base.groupby("order_month", as_index=False)
        .agg(total_orders=("invoice_id", "nunique"), total_revenue=("revenue", "sum"))
        .sort_values("order_month")
    )
    sales_trend["mom_growth_pct"] = sales_trend["total_revenue"].pct_change().fillna(0.0) * 100

    top_products_volume = (
        base.groupby(["product_id", "product_name"], as_index=False)
        .agg(units_sold=("quantity", "sum"))
        .sort_values("units_sold", ascending=False)
        .head(20)
    )

    top_products_revenue = (
        base.groupby(["product_id", "product_name"], as_index=False)
        .agg(product_revenue=("revenue", "sum"))
        .sort_values("product_revenue", ascending=False)
        .head(20)
    )

    revenue_by_region = (
        base.groupby("region", as_index=False)
        .agg(region_revenue=("revenue", "sum"), active_customers=("customer_id", "nunique"))
        .sort_values("region_revenue", ascending=False)
    )

    summary = {
        "total_revenue": float(base["revenue"].sum()),
        "total_orders": int(base["invoice_id"].nunique()),
        "total_customers": int(base["customer_id"].nunique()),
        "avg_order_value": float(base.groupby("invoice_id")["revenue"].sum().mean()),
    }

    return KPIArtifacts(
        sales_trend=sales_trend,
        top_products_volume=top_products_volume,
        top_products_revenue=top_products_revenue,
        revenue_by_region=revenue_by_region,
        summary=summary,
    )


def write_kpi_outputs(kpis: KPIArtifacts, report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    kpis.sales_trend.to_csv(report_dir / "sales_trend.csv", index=False)
    kpis.top_products_volume.to_csv(report_dir / "top_products_volume.csv", index=False)
    kpis.top_products_revenue.to_csv(report_dir / "top_products_revenue.csv", index=False)
    kpis.revenue_by_region.to_csv(report_dir / "revenue_by_region.csv", index=False)
    with (report_dir / "kpi_summary.json").open("w", encoding="utf-8") as f:
        json.dump(kpis.summary, f, indent=2)
