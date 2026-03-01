"""Synthetic dataset generator for local validation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def build_sample_transactions(n_rows: int = 50000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    customers = [f"C{idx:05d}" for idx in range(1, 2501)]
    products = [f"P{idx:04d}" for idx in range(1, 301)]
    regions = ["North", "South", "East", "West"]

    product_names = {pid: f"Product {pid}" for pid in products}

    start = pd.Timestamp("2024-01-01")
    end = pd.Timestamp("2026-02-15")
    days = (end - start).days

    invoice_ids = [f"INV{idx:08d}" for idx in range(1, n_rows + 1)]
    customer_ids = rng.choice(customers, size=n_rows, replace=True)
    product_ids = rng.choice(products, size=n_rows, replace=True)
    quantities = rng.integers(1, 6, size=n_rows)
    unit_prices = np.round(rng.uniform(4.5, 180.0, size=n_rows), 2)
    regions_chosen = rng.choice(regions, size=n_rows, replace=True, p=[0.26, 0.24, 0.25, 0.25])
    order_dates = start + pd.to_timedelta(rng.integers(0, days + 1, size=n_rows), unit="D")

    df = pd.DataFrame(
        {
            "invoice_id": invoice_ids,
            "customer_id": customer_ids,
            "order_date": order_dates,
            "product_id": product_ids,
            "product_name": [product_names[p] for p in product_ids],
            "quantity": quantities,
            "unit_price": unit_prices,
            "region": regions_chosen,
        }
    )
    return df.sort_values("order_date").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sample transactions for Consumer360")
    parser.add_argument("--rows", type=int, default=50000)
    parser.add_argument("--out", type=str, default="data/transactions.csv")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = build_sample_transactions(n_rows=args.rows)
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()
