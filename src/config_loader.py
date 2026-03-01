"""Configuration loader for Consumer360."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_settings(config_path: str = "config/settings.yaml") -> dict:
    load_dotenv(ROOT_DIR / ".env")
    path = ROOT_DIR / config_path
    with path.open("r", encoding="utf-8") as f:
        settings = yaml.safe_load(f)

    sql_cfg = settings.get("data_source", {}).get("sql", {})
    env_var = sql_cfg.get("connection_env_var")
    if env_var:
        sql_cfg["connection_string"] = os.getenv(env_var, "")

    return settings
