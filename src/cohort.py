"""Cohort retention analysis."""

from __future__ import annotations

import pandas as pd


def cohort_retention(df: pd.DataFrame) -> pd.DataFrame:
    frame = df[["customer_id", "order_date"]].copy()
    frame["order_month"] = frame["order_date"].dt.to_period("M").dt.to_timestamp()

    first_purchase = (
        frame.groupby("customer_id", as_index=False)["order_month"]
        .min()
        .rename(columns={"order_month": "cohort_month"})
    )

    frame = frame.merge(first_purchase, on="customer_id", how="left")
    frame["cohort_index"] = (
        (frame["order_month"].dt.year - frame["cohort_month"].dt.year) * 12
        + (frame["order_month"].dt.month - frame["cohort_month"].dt.month)
    )

    grouped = (
        frame.groupby(["cohort_month", "cohort_index"], as_index=False)
        .agg(active_customers=("customer_id", "nunique"))
    )

    cohort_size = (
        grouped[grouped["cohort_index"] == 0][["cohort_month", "active_customers"]]
        .rename(columns={"active_customers": "cohort_customers"})
    )

    result = grouped.merge(cohort_size, on="cohort_month", how="left")
    result["retention_rate"] = result["active_customers"] / result["cohort_customers"]
    return result.sort_values(["cohort_month", "cohort_index"])
