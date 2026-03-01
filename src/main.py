"""Weekly Consumer360 pipeline runner."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.clv import estimate_clv
from src.cohort import cohort_retention
from src.config_loader import ROOT_DIR, load_settings
from src.data_access import load_transactions
from src.data_quality import run_quality_checks
from src.export_dashboard_payload import export_dashboard_payload
from src.kpi import compute_kpis, write_kpi_outputs
from src.market_basket import build_market_basket_rules
from src.rfm import calculate_rfm


def run_pipeline(run_date: str | None = None) -> None:
    settings = load_settings()
    report_dir = ROOT_DIR / settings.get("report_dir", "reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    df = load_transactions(settings)
    quality = run_quality_checks(df)
    pd.Series(quality.checks).to_json(report_dir / "data_quality_report.json", indent=2)
    if not quality.passed:
        raise ValueError(f"Data quality checks failed: {quality.checks}")

    snapshot_date = pd.to_datetime(run_date) if run_date else df["order_date"].max()

    # 1) Core KPIs
    kpis = compute_kpis(df)
    write_kpi_outputs(kpis, report_dir)

    # 2) RFM segmentation
    rfm = calculate_rfm(df, snapshot_date=snapshot_date, bins=settings["rfm"]["score_bins"])
    rfm.to_csv(report_dir / "customer_rfm_segments.csv", index=False)

    # 3) Cohort retention
    cohort = cohort_retention(df)
    cohort.to_csv(report_dir / "cohort_retention.csv", index=False)

    # 4) Market basket rules
    mba = build_market_basket_rules(
        df,
        min_support=settings["market_basket"]["min_support"],
        min_confidence=settings["market_basket"]["min_confidence"],
        min_lift=settings["market_basket"]["min_lift"],
    )
    mba.to_csv(report_dir / "market_basket_rules.csv", index=False)

    # 5) CLV estimation
    clv = estimate_clv(
        df,
        horizon_days=settings["clv"]["horizon_days"],
        discount_rate=settings["clv"]["discount_rate"],
    )
    clv.to_csv(report_dir / "customer_clv.csv", index=False)

    # 6) Consumer360 action lists for campaigns
    champions = rfm[rfm["segment"] == "Champions"].copy()
    churn_risk = rfm[rfm["segment"].isin(["Churn Risk", "At Risk", "Hibernating"])].copy()
    champions.to_csv(report_dir / "campaign_champions.csv", index=False)
    churn_risk.to_csv(report_dir / "campaign_churn_risk.csv", index=False)

    # 7) Frontend payload for React dashboard
    export_dashboard_payload(report_dir=report_dir, frontend_data_dir=ROOT_DIR / "frontend" / "public" / "data")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Consumer360 weekly analytics pipeline")
    parser.add_argument("--run-date", type=str, default=None, help="Snapshot date, format YYYY-MM-DD")
    args = parser.parse_args()
    run_pipeline(run_date=args.run_date)
