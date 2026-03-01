/* 02_clean_transactions.sql
   Cleanses raw transactions and materializes an analytics-ready staging table.
*/

IF OBJECT_ID('dbo.stg_sales_clean', 'U') IS NOT NULL DROP TABLE dbo.stg_sales_clean;

WITH normalized AS (
    SELECT
        CAST(NULLIF(LTRIM(RTRIM(invoice_id)), '') AS NVARCHAR(100)) AS invoice_id,
        CAST(NULLIF(LTRIM(RTRIM(customer_id)), '') AS NVARCHAR(100)) AS customer_id,
        CAST(NULLIF(LTRIM(RTRIM(product_id)), '') AS NVARCHAR(100)) AS product_id,
        COALESCE(NULLIF(LTRIM(RTRIM(product_name)), ''), 'Unknown Product') AS product_name,
        TRY_CONVERT(DATETIME2, order_datetime) AS order_datetime,
        TRY_CONVERT(INT, quantity) AS quantity,
        TRY_CONVERT(DECIMAL(18,4), unit_price) AS unit_price,
        COALESCE(NULLIF(LTRIM(RTRIM(region)), ''), 'Unknown') AS region
    FROM dbo.raw_transactions
),
validated AS (
    SELECT
        invoice_id,
        customer_id,
        product_id,
        product_name,
        order_datetime,
        quantity,
        unit_price,
        region,
        CAST(quantity * unit_price AS DECIMAL(18,4)) AS line_revenue
    FROM normalized
    WHERE invoice_id IS NOT NULL
      AND customer_id IS NOT NULL
      AND product_id IS NOT NULL
      AND order_datetime IS NOT NULL
      AND quantity IS NOT NULL AND quantity > 0
      AND unit_price IS NOT NULL AND unit_price >= 0
)
SELECT *
INTO dbo.stg_sales_clean
FROM validated;

CREATE INDEX IX_stg_sales_clean_customer_date ON dbo.stg_sales_clean(customer_id, order_datetime);
CREATE INDEX IX_stg_sales_clean_invoice ON dbo.stg_sales_clean(invoice_id);
