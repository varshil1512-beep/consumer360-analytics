# Brand Customization

Update `config/brand.yaml` to match client identity.

## Main keys
- `product_name`: dashboard title
- `company_name`: owner/team label
- `tagline`: hero subtitle
- `primary_color`, `secondary_color`, `accent_color`: chart and highlight palette
- `font_display`, `font_body`: typography style
- `logo_path`: local logo file path (optional)

## Stakeholder Views in Dashboard
- `CMO View`: revenue, segment mix, growth narrative
- `Retention View`: churn-risk, cohort retention, priority list
- `Regional View`: region-filtered campaign list and KPIs

## Launch
```powershell
streamlit run app.py
```
