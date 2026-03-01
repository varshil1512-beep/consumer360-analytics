"""Consumer360 API service for dashboard and integrations."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_PATH = ROOT / "frontend" / "public" / "data" / "dashboard_payload.json"
QUALITY_PATH = ROOT / "reports" / "data_quality_report.json"

app = FastAPI(title="Consumer360 API", version="1.0.0")


def _load_payload() -> dict:
    if not PAYLOAD_PATH.exists():
        raise HTTPException(status_code=404, detail="Dashboard payload not found. Run pipeline first.")
    return json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "consumer360-api"}


@app.get("/payload")
def payload() -> dict:
    return _load_payload()


@app.get("/kpis")
def kpis() -> dict:
    payload = _load_payload()
    return payload.get("kpi_summary", {})


@app.get("/campaigns")
def campaigns() -> dict:
    payload = _load_payload()
    return {
        "champions": payload.get("champions", []),
        "churn_risk": payload.get("churn_risk", []),
    }


@app.get("/quality")
def quality() -> dict:
    if not QUALITY_PATH.exists():
        raise HTTPException(status_code=404, detail="Quality report not found. Run pipeline first.")
    return json.loads(QUALITY_PATH.read_text(encoding="utf-8"))
