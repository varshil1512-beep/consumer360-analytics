# Power BI Build Guide (Consumer360)

## Recommended Data Model
- Import CSV outputs from `reports/`.
- Create dimensions:
  - `DimCustomer` from `customer_rfm_segments.csv`
  - `DimDate` derived from `sales_trend.csv` or source transactions
  - `DimRegion` from unique region values
- Facts:
  - `sales_trend.csv`
  - `revenue_by_region.csv`
  - `cohort_retention.csv`
  - `market_basket_rules.csv`
  - `customer_clv.csv`

## Core DAX Measures
```DAX
Total Revenue = SUMX('sales_trend', 'sales_trend'[total_revenue])

Previous Month Revenue =
CALCULATE(
    [Total Revenue],
    DATEADD('DimDate'[Date], -1, MONTH)
)

MoM Growth % =
DIVIDE([Total Revenue] - [Previous Month Revenue], [Previous Month Revenue], 0)

Champion Customers =
CALCULATE(
    DISTINCTCOUNT('DimCustomer'[customer_id]),
    'DimCustomer'[segment] = "Champions"
)

Churn Risk Customers =
CALCULATE(
    DISTINCTCOUNT('DimCustomer'[customer_id]),
    'DimCustomer'[segment] IN {"Churn Risk", "At Risk", "Hibernating"}
)
```

## RFM Matrix Visual
- Rows: `segment`
- Values: `COUNT(customer_id)`, `SUM(monetary)`
- Conditional formatting by segment risk/value.

## Cohort Heatmap
- Axis X: `cohort_index`
- Axis Y: `cohort_month`
- Value: `retention_rate`

## RLS Setup (Regional Managers)
Create role filter on `DimCustomer` and relevant fact tables:
```DAX
[region] = USERPRINCIPALNAME()
```
For mapping table approach, use a security bridge table (`UserRegionMap`).
