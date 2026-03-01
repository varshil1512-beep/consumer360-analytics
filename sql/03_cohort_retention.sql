/* 03_cohort_retention.sql
   Cohort base and retention table using SQL window/date functions.
*/

WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(CAST(order_datetime AS DATE)) AS first_purchase_date
    FROM dbo.stg_sales_clean
    GROUP BY customer_id
),
activity AS (
    SELECT
        s.customer_id,
        DATEFROMPARTS(YEAR(s.order_datetime), MONTH(s.order_datetime), 1) AS activity_month,
        DATEFROMPARTS(YEAR(fp.first_purchase_date), MONTH(fp.first_purchase_date), 1) AS cohort_month
    FROM dbo.stg_sales_clean s
    INNER JOIN first_purchase fp
        ON fp.customer_id = s.customer_id
    GROUP BY
        s.customer_id,
        DATEFROMPARTS(YEAR(s.order_datetime), MONTH(s.order_datetime), 1),
        DATEFROMPARTS(YEAR(fp.first_purchase_date), MONTH(fp.first_purchase_date), 1)
),
cohort_size AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_customers
    FROM activity
    GROUP BY cohort_month
),
retention AS (
    SELECT
        a.cohort_month,
        DATEDIFF(MONTH, a.cohort_month, a.activity_month) AS cohort_index,
        COUNT(DISTINCT a.customer_id) AS active_customers
    FROM activity a
    GROUP BY
        a.cohort_month,
        DATEDIFF(MONTH, a.cohort_month, a.activity_month)
)
SELECT
    r.cohort_month,
    r.cohort_index,
    cs.cohort_customers,
    r.active_customers,
    CAST(1.0 * r.active_customers / NULLIF(cs.cohort_customers, 0) AS DECIMAL(10,4)) AS retention_rate
FROM retention r
INNER JOIN cohort_size cs
    ON cs.cohort_month = r.cohort_month
ORDER BY r.cohort_month, r.cohort_index;
