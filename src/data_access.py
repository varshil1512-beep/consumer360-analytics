"""Data access layer for CSV/SQL ingestion."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from src.config_loader import ROOT_DIR


REQUIRED_COLUMNS = {
    "invoice_id",
    "customer_id",
    "order_date",
    "quantity",
    "unit_price",
    "region",
    "product_id",
    "product_name",
}


def _normalize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "order_datetime" in df.columns and "order_date" not in df.columns:
        df["order_date"] = df["order_datetime"]

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    df = df.dropna(subset=["invoice_id", "customer_id", "product_id", "order_date", "quantity", "unit_price"])
    df = df[(df["quantity"] > 0) & (df["unit_price"] >= 0)]

    for c in ["invoice_id", "customer_id", "product_id", "product_name", "region"]:
        df[c] = df[c].astype(str).str.strip()

    df["revenue"] = df["quantity"] * df["unit_price"]
    return df


def load_transactions(settings: dict) -> pd.DataFrame:
    mode = settings["data_source"]["mode"].lower()

    if mode == "csv":
        csv_path = ROOT_DIR / settings["data_source"]["csv_path"]
        if not csv_path.exists():
            raise FileNotFoundError(
                f"CSV source not found at {csv_path}. Add data or switch to SQL mode."
            )
        df = pd.read_csv(csv_path)
        return _normalize_transactions(df)

    if mode == "sql":
        sql_cfg = settings["data_source"]["sql"]
        conn = sql_cfg.get("connection_string", "")
        table = sql_cfg["table_name"]
        if not conn:
            raise ValueError("SQL connection string is empty. Set it in .env.")

        engine = create_engine(conn)
        query = f"SELECT * FROM {table}"  # nosec B608 - controlled config source
        df = pd.read_sql(query, con=engine)
        return _normalize_transactions(df)

    raise ValueError(f"Unsupported data source mode: {mode}")
