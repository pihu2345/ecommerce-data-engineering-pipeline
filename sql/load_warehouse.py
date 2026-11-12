
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

gold_folder = BASE_DIR / "data" / "gold"
database_folder = BASE_DIR / "data" / "warehouse"

database_folder.mkdir(parents=True, exist_ok=True)

db_path = database_folder / "ecommerce.db"

# Connect to SQLite database
connection = sqlite3.connect(db_path)

# Gold CSV files
tables = {
    "daily_sales_summary": "daily_sales_summary.csv",
    "product_performance": "product_performance.csv",
    "customer_analytics": "customer_analytics.csv"
}

# Load CSV files into SQL tables
for table_name, file_name in tables.items():

    file_path = gold_folder / file_name

    df = pd.read_csv(file_path)

    df.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False
    )

    print(f"Loaded {table_name}: {len(df)} rows")

connection.close()

print("\nE-commerce Data Warehouse created successfully!")
