# Frontend Dashboard (React)

Consumer360 now uses a modern React frontend (Vite).

## Advanced Features
- Sidebar navigation and control center
- Region + segment + month-window filtering
- Customer spotlight search
- Strategic insight cards
- Campaign priority queue scoring
- CSV export actions for champions/churn lists

## Run Dev Server
```powershell
./run_frontend.ps1
```
Open: `http://localhost:5173`

## Build for Production
```powershell
./run_frontend.ps1 -Build
```

## Data Flow
1. Run analytics pipeline:
   - `python -m src.main --run-date 2026-02-27`
2. Pipeline writes `frontend/public/data/dashboard_payload.json`
3. Frontend fetches this payload for all charts and tables

## Why script instead of npm run?
Your path contains `&` (`Retail - Customer Behavior & RFM Analysis`), which can break `npm run` in Windows cmd contexts. The PowerShell launcher avoids that issue.
