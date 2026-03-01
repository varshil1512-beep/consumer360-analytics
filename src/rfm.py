"""RFM scoring and segmentation."""

from __future__ import annotations

import pandas as pd


SEGMENT_RULES = {
    "Champions": lambda r, f, m: r >= 4 and f >= 4 and m >= 4,
    "Loyal Customers": lambda r, f, m: r >= 3 and f >= 4,
    "Potential Loyalist": lambda r, f, m: r >= 4 and f >= 2 and m >= 2,
    "New Customers": lambda r, f, m: r == 5 and f <= 2,
    "Promising": lambda r, f, m: r >= 3 and f <= 2 and m >= 2,
    "Need Attention": lambda r, f, m: r == 3 and f >= 2,
    "About To Sleep": lambda r, f, m: r == 2 and f >= 2,
    "At Risk": lambda r, f, m: r <= 2 and f >= 3 and m >= 3,
    "Churn Risk": lambda r, f, m: r == 1 and (f >= 2 or m >= 2),
    "Hibernating": lambda r, f, m: r <= 2 and f <= 2,
}


def _score_series(series: pd.Series, bins: int, ascending: bool) -> pd.Series:
    ranked = series.rank(method="first", ascending=True)
    scores = pd.qcut(ranked, q=bins, labels=False, duplicates="drop") + 1
    return scores if ascending else (bins + 1 - scores)


def calculate_rfm(df: pd.DataFrame, snapshot_date: pd.Timestamp, bins: int = 5) -> pd.DataFrame:
    grouped = (
        df.groupby("customer_id", as_index=False)
        .agg(
            last_order_date=("order_date", "max"),
            frequency=("invoice_id", "nunique"),
            monetary=("revenue", "sum"),
            region=("region", "last"),
        )
    )

    grouped["recency_days"] = (snapshot_date - grouped["last_order_date"]).dt.days

    grouped["r_score"] = _score_series(grouped["recency_days"], bins=bins, ascending=False)
    grouped["f_score"] = _score_series(grouped["frequency"], bins=bins, ascending=True)
    grouped["m_score"] = _score_series(grouped["monetary"], bins=bins, ascending=True)
    grouped["rfm_score"] = (
        grouped["r_score"].astype(str)
        + grouped["f_score"].astype(str)
        + grouped["m_score"].astype(str)
    )

    def classify(row: pd.Series) -> str:
        r, f, m = int(row["r_score"]), int(row["f_score"]), int(row["m_score"])
        for name, rule in SEGMENT_RULES.items():
            if rule(r, f, m):
                return name
        return "Others"

    grouped["segment"] = grouped.apply(classify, axis=1)
    return grouped.sort_values(["segment", "monetary"], ascending=[True, False])
