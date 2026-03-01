# Consumer360 Dashboard

## Launch UI
```powershell
streamlit run app.py
```

## Recommended Flow
1. Run weekly pipeline first: `python -m src.main --run-date 2026-02-27`
2. Launch dashboard: `streamlit run app.py`
3. Use sidebar filters (region + segment) for targeted views.

## UI Highlights
- Executive KPI hero and premium cards
- Revenue trend + regional mix
- RFM bubble map and segment revenue bars
- Cohort retention heatmap
- CLV top customer leaderboard
- Champion and Churn-Risk campaign action tables

## Mobile and Desktop
- Wide responsive layout using Streamlit columns/tabs
- Tables and charts adapt to screen width automatically
