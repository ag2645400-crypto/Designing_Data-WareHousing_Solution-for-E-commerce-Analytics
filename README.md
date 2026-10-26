# Designing a Data Warehousing Solution for E-commerce Analytics

## Overview

This academic project demonstrates how raw e-commerce order data can be cleaned, loaded into a MySQL data warehouse, and analyzed using SQL. The goal is to turn source records into consistent reporting data for sales, products, customers, and orders.

## Project Objectives

- Design a centralized warehouse using a star schema.
- Build a simple ETL pipeline: Extract, Transform, and Load.
- Clean duplicate and invalid source rows.
- Analyze sales performance by month, product, city, order status, and payment method.
- Prepare a foundation for a future Power BI dashboard.

## Architecture

CSV source data → Python + Pandas cleaning → MySQL warehouse → SQL analytics → (future) Power BI dashboard.

## Data Warehouse Design

The warehouse uses a star-schema style model:

- **fact_sales**: quantity, unit price, discount, gross sales, and net sales.
- **dim_customer**: customer ID, name, and city.
- **dim_product**: product ID, name, and category.
- **dim_date**: full date, day, month, quarter, and year.
- **dim_order**: order ID, payment method, and order status.

The current sample data is fictional and intended for learning and demonstration. Replace it with an approved dataset before drawing conclusions about a real business.

## Repository Structure

```text
.
├── data/
│   └── sample_ecommerce.csv
├── sql/
│   ├── schema.sql
│   └── analytics_queries.sql
├── etl.py
├── requirements.txt
└── README.md
```

## Setup and Run

### 1. Requirements

- Python 3.10 or newer
- MySQL Server and MySQL Workbench
- VS Code (recommended)

### 2. Create the database tables

Open `sql/schema.sql` in MySQL Workbench and execute the script. It creates the `ecommerce_dw` database and the five warehouse tables.

### 3. Install Python dependencies

From the project folder, run:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure database access

Set environment variables for your MySQL connection. For example, in Windows Command Prompt:

```bat
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=root
set DB_PASSWORD=your_mysql_password
set DB_NAME=ecommerce_dw
```

Use your own local MySQL password; do not commit passwords or secrets to GitHub.

### 5. Run the ETL pipeline

```bash
python etl.py
```

By default, the pipeline reads `data/sample_ecommerce.csv`, validates required columns, removes duplicate rows, cleans invalid values, and loads the resulting records into MySQL. The current starter pipeline rebuilds the fact table on each run, so rerunning it will not duplicate the fact rows.

### 6. Run analytics

Execute `sql/analytics_queries.sql` in MySQL Workbench to view sample reports.

## Source CSV Format

The source CSV should contain these columns:

`order_id, order_date, customer_id, customer_name, city, product_id, product_name, category, quantity, unit_price, discount, payment_method, order_status`

To load another file, set the `SOURCE_FILE` environment variable to its path before running `python etl.py`.

## Example Business Questions

- What are net sales by month?
- Which products generate the highest net sales?
- Which cities contribute most to sales?
- What is the distribution of completed, pending, and cancelled orders?
- Which payment methods are used most often?

## Tools and Technologies

- **Python** and **Pandas** — data cleaning and ETL
- **MySQL** — warehouse storage
- **MySQL Workbench** — schema and query execution
- **CSV** — sample source data
- **Power BI** — planned future dashboard

## Scope and Limitations

This is a student project starter implementation. The sample dataset is fictional, the data model is intentionally simple, and the ETL script is designed for local demonstration rather than production-scale workloads. Profit, inventory, shipping, and advanced customer segmentation are not included because the current source data does not provide the required fields.

## Author

**Aditya Gupta**
