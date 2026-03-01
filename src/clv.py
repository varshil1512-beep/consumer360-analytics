"""Predictive CLV using lifetimes (BG/NBD + Gamma-Gamma)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def estimate_clv(
    df: pd.DataFrame,
    horizon_days: int = 90,
    discount_rate: float = 0.01,
) -> pd.DataFrame:
    try:
        from lifetimes import BetaGeoFitter, GammaGammaFitter
        from lifetimes.utils import summary_data_from_transaction_data
    except Exception:
        return _fallback_clv(df)

    tdf = df[["customer_id", "order_date", "revenue"]].copy()
    tdf["order_date"] = pd.to_datetime(tdf["order_date"]).dt.tz_localize(None)

    summary = summary_data_from_transaction_data(
        tdf,
        customer_id_col="customer_id",
        datetime_col="order_date",
        monetary_value_col="revenue",
        observation_period_end=tdf["order_date"].max(),
        freq="D",
    ).reset_index()

    if summary.empty:
        return _fallback_clv(df)

    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(summary["frequency"], summary["recency"], summary["T"])

    summary["predicted_purchases_90d"] = bgf.conditional_expected_number_of_purchases_up_to_time(
        horizon_days,
        summary["frequency"],
        summary["recency"],
        summary["T"],
    )

    positive = summary[summary["monetary_value"] > 0].copy()
    if positive.empty:
        summary["predicted_avg_order_value"] = np.nan
        summary["predicted_clv"] = np.nan
        return summary

    ggf = GammaGammaFitter(penalizer_coef=0.001)
    ggf.fit(positive["frequency"], positive["monetary_value"])

    positive["predicted_avg_order_value"] = ggf.conditional_expected_average_profit(
        positive["frequency"], positive["monetary_value"]
    )

    positive["predicted_clv"] = ggf.customer_lifetime_value(
        bgf,
        positive["frequency"],
        positive["recency"],
        positive["T"],
        positive["monetary_value"],
        time=horizon_days / 30.0,
        discount_rate=discount_rate,
        freq="D",
    )

    merged = summary.merge(
        positive[["customer_id", "predicted_avg_order_value", "predicted_clv"]],
        on="customer_id",
        how="left",
    )
    return merged


def _fallback_clv(df: pd.DataFrame) -> pd.DataFrame:
    agg = (
        df.groupby("customer_id", as_index=False)
        .agg(
            frequency=("invoice_id", "nunique"),
            monetary_value=("revenue", "mean"),
            total_revenue=("revenue", "sum"),
        )
        .copy()
    )
    agg["predicted_purchases_90d"] = agg["frequency"] * 0.5
    agg["predicted_avg_order_value"] = agg["monetary_value"]
    agg["predicted_clv"] = agg["predicted_purchases_90d"] * agg["predicted_avg_order_value"]
    return agg
