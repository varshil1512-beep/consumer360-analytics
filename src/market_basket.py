"""Market basket analysis using association rule mining."""

from __future__ import annotations

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules


def build_market_basket_rules(
    df: pd.DataFrame,
    min_support: float = 0.01,
    min_confidence: float = 0.2,
    min_lift: float = 1.0,
) -> pd.DataFrame:
    basket = (
        df.groupby(["invoice_id", "product_name"])["quantity"]
        .sum()
        .unstack(fill_value=0)
        .gt(0).astype(int)
    )

    if basket.empty:
        return pd.DataFrame(
            columns=[
                "antecedents",
                "consequents",
                "support",
                "confidence",
                "lift",
                "leverage",
                "conviction",
            ]
        )

    frequent_sets = apriori(basket.astype(bool), min_support=min_support, use_colnames=True)
    if frequent_sets.empty:
        return pd.DataFrame(columns=["antecedents", "consequents", "support", "confidence", "lift"])

    rules = association_rules(frequent_sets, metric="confidence", min_threshold=min_confidence)
    if rules.empty:
        return pd.DataFrame(columns=["antecedents", "consequents", "support", "confidence", "lift"])

    rules = rules[rules["lift"] >= min_lift].copy()
    rules["antecedents"] = rules["antecedents"].apply(lambda s: ", ".join(sorted(list(s))))
    rules["consequents"] = rules["consequents"].apply(lambda s: ", ".join(sorted(list(s))))

    cols = ["antecedents", "consequents", "support", "confidence", "lift", "leverage", "conviction"]
    return rules[cols].sort_values(["lift", "confidence"], ascending=False)
