/* 01_star_schema.sql
   Core star schema for Consumer360. Dialect: SQL Server style.
*/

IF OBJECT_ID('dbo.fact_sales', 'U') IS NOT NULL DROP TABLE dbo.fact_sales;
IF OBJECT_ID('dbo.dim_customer', 'U') IS NOT NULL DROP TABLE dbo.dim_customer;
IF OBJECT_ID('dbo.dim_product', 'U') IS NOT NULL DROP TABLE dbo.dim_product;
IF OBJECT_ID('dbo.dim_date', 'U') IS NOT NULL DROP TABLE dbo.dim_date;

CREATE TABLE dbo.dim_customer (
    customer_key INT IDENTITY(1,1) PRIMARY KEY,
    customer_id NVARCHAR(100) NOT NULL UNIQUE,
    signup_date DATE NULL,
    region NVARCHAR(100) NULL,
    city NVARCHAR(100) NULL,
    country NVARCHAR(100) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);

CREATE TABLE dbo.dim_product (
    product_key INT IDENTITY(1,1) PRIMARY KEY,
    product_id NVARCHAR(100) NOT NULL UNIQUE,
    product_name NVARCHAR(255) NOT NULL,
    category NVARCHAR(100) NULL,
    subcategory NVARCHAR(100) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);

CREATE TABLE dbo.dim_date (
    date_key INT PRIMARY KEY,   -- yyyymmdd
    calendar_date DATE NOT NULL UNIQUE,
    [year] INT NOT NULL,
    [quarter] INT NOT NULL,
    [month] INT NOT NULL,
    month_name NVARCHAR(20) NOT NULL,
    week_of_year INT NOT NULL,
    day_of_month INT NOT NULL,
    day_name NVARCHAR(20) NOT NULL
);

CREATE TABLE dbo.fact_sales (
    sales_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    invoice_id NVARCHAR(100) NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    date_key INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(18,4) NOT NULL,
    gross_amount AS (quantity * unit_price) PERSISTED,
    discount_amount DECIMAL(18,4) NOT NULL DEFAULT 0,
    net_amount AS ((quantity * unit_price) - discount_amount) PERSISTED,
    region NVARCHAR(100) NULL,
    load_dts DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_fact_sales_customer FOREIGN KEY (customer_key) REFERENCES dbo.dim_customer(customer_key),
    CONSTRAINT FK_fact_sales_product FOREIGN KEY (product_key) REFERENCES dbo.dim_product(product_key),
    CONSTRAINT FK_fact_sales_date FOREIGN KEY (date_key) REFERENCES dbo.dim_date(date_key)
);

CREATE INDEX IX_fact_sales_customer_date ON dbo.fact_sales(customer_key, date_key);
CREATE INDEX IX_fact_sales_product_date ON dbo.fact_sales(product_key, date_key);
CREATE INDEX IX_fact_sales_invoice ON dbo.fact_sales(invoice_id);
