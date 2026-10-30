"""Load a CSV source file into the MySQL e-commerce data warehouse.

Set DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, and DB_NAME environment variables.
Default source: data/sample_ecommerce.csv
"""
import os
from pathlib import Path
import pandas as pd
import mysql.connector

ROOT = Path(__file__).resolve().parent
SOURCE_FILE = Path(os.getenv("SOURCE_FILE", ROOT / "data" / "sample_ecommerce.csv"))
REQUIRED_COLUMNS = [
    "order_id", "order_date", "customer_id", "customer_name", "city",
    "product_id", "product_name", "category", "quantity", "unit_price",
    "discount", "payment_method", "order_status",
]


def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ecommerce_dw"),
    )


def clean_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    df = pd.read_csv(path)
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing)}")

    report = {"rows_read": len(df)}

    df = df[REQUIRED_COLUMNS].copy()
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = before - len(df)

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    for column in ["quantity", "unit_price", "discount"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Count each kind of invalid row before dropping them.
    report["invalid_date"] = int(df["order_date"].isna().sum())
    report["missing_quantity"] = int(df["quantity"].isna().sum())
    report["non_positive_quantity"] = int((df["quantity"] <= 0).sum())

    # Reject rows that cannot produce a valid sales fact.
    before = len(df)
    df = df.dropna(subset=[
        "order_id", "order_date", "customer_id", "product_id",
        "quantity", "unit_price",
    ])
    df = df[(df["quantity"] > 0) & (df["unit_price"] >= 0)]
    report["invalid_rows_removed"] = before - len(df)

    df["discount"] = df["discount"].fillna(0).clip(lower=0)
    df["quantity"] = df["quantity"].astype(int)

    text_columns = [
        "order_id", "customer_id", "customer_name", "city", "product_id",
        "product_name", "category", "payment_method", "order_status",
    ]
    for column in text_columns:
        df[column] = df[column].fillna("Unknown").astype(str).str.strip()
        df.loc[df[column] == "", column] = "Unknown"

    report["rows_clean"] = len(df)
    df.attrs["report"] = report
    return df


def load_data(df: pd.DataFrame) -> int:
    connection = connect_db()
    cursor = connection.cursor()
    try:
        # Rebuild the fact table on each run so rerunning this starter ETL
        # does not duplicate sales. Dimension keys remain stable.
        cursor.execute("DELETE FROM fact_sales")

        for row in df.itertuples(index=False):
            date = row.order_date.date()
            date_key = int(date.strftime("%Y%m%d"))

            cursor.execute(
                """INSERT INTO dim_customer (customer_id, customer_name, city)
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                     customer_name = VALUES(customer_name), city = VALUES(city)""",
                (row.customer_id, row.customer_name, row.city),
            )
            cursor.execute("SELECT customer_key FROM dim_customer WHERE customer_id=%s",
                           (row.customer_id,))
            customer_key = cursor.fetchone()[0]

            cursor.execute(
                """INSERT INTO dim_product (product_id, product_name, category)
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                     product_name = VALUES(product_name), category = VALUES(category)""",
                (row.product_id, row.product_name, row.category),
            )
            cursor.execute("SELECT product_key FROM dim_product WHERE product_id=%s",
                           (row.product_id,))
            product_key = cursor.fetchone()[0]

            cursor.execute(
                """INSERT INTO dim_date
                   (date_key, full_date, day_number, month_number, month_name,
                    quarter_number, year_number)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE full_date=VALUES(full_date)""",
                (date_key, date, date.day, date.month, date.strftime("%B"),
                 ((date.month - 1) // 3) + 1, date.year),
            )

            cursor.execute(
                """INSERT INTO dim_order (order_id, payment_method, order_status)
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                     payment_method=VALUES(payment_method),
                     order_status=VALUES(order_status)""",
                (row.order_id, row.payment_method, row.order_status),
            )
            cursor.execute("SELECT order_key FROM dim_order WHERE order_id=%s",
                           (row.order_id,))
            order_key = cursor.fetchone()[0]

            gross_sales = round(float(row.quantity) * float(row.unit_price), 2)
            net_sales = round(max(0.0, gross_sales - float(row.discount)), 2)
            cursor.execute(
                """INSERT INTO fact_sales
                   (order_id, customer_key, product_key, date_key, order_key,
                    quantity, unit_price, discount, gross_sales, net_sales)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (row.order_id, customer_key, product_key, date_key, order_key,
                 int(row.quantity), float(row.unit_price), float(row.discount),
                 gross_sales, net_sales),
            )

        connection.commit()
        return len(df)
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def main():
    df = clean_data(SOURCE_FILE)
    report = df.attrs["report"]
    print("--- Data Quality Report ---")
    print(f"Rows read from CSV      : {report['rows_read']}")
    print(f"Duplicates removed      : {report['duplicates_removed']}")
    print(f"Invalid dates           : {report['invalid_date']}")
    print(f"Missing quantity        : {report['missing_quantity']}")
    print(f"Non-positive quantity   : {report['non_positive_quantity']}")
    print(f"Invalid rows removed    : {report['invalid_rows_removed']}")
    print(f"Clean rows              : {report['rows_clean']}")
    print("---------------------------")
    loaded = load_data(df)
    print(f"ETL completed successfully. Loaded {loaded} sales rows from {SOURCE_FILE}")


if __name__ == "__main__":
    main()