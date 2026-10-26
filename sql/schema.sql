-- E-commerce Analytics Data Warehouse
-- Run this script in MySQL Workbench.

CREATE DATABASE IF NOT EXISTS ecommerce_dw;
USE ecommerce_dw;

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(150),
    city VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(200),
    category VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day_number TINYINT NOT NULL,
    month_number TINYINT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter_number TINYINT NOT NULL,
    year_number SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_order (
    order_key INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL UNIQUE,
    payment_method VARCHAR(80),
    order_status VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    date_key INT NOT NULL,
    order_key INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    discount DECIMAL(12,2) NOT NULL DEFAULT 0,
    gross_sales DECIMAL(14,2) NOT NULL,
    net_sales DECIMAL(14,2) NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_customer FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_sales_product FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    CONSTRAINT fk_sales_date FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    CONSTRAINT fk_sales_order FOREIGN KEY (order_key) REFERENCES dim_order(order_key),
    INDEX idx_fact_sales_order (order_id),
    INDEX idx_fact_sales_date (date_key)
);
