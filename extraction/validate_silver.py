
import pandas as pd
from pathlib import Path

silver_folder = Path("data/silver")

datasets = {
    "customers.csv": "customer_id",
    "products.csv": "product_id",
    "orders.csv": "order_id",
    "sales.csv": "sale_id",
    "payments.csv": "payment_id"
}

print("=" * 55)
print("       SILVER LAYER VALIDATION REPORT")
print("=" * 55)

for file, primary_key in datasets.items():

    file_path = silver_folder / file

    print("\nDataset:", file)

    if not file_path.exists():
        print("ERROR: File not found!")
        continue

    df = pd.read_csv(file_path)

    print("Total rows:", len(df))
    print("Missing values:", df.isnull().sum().sum())
    print("Duplicate primary keys:",
          df[primary_key].duplicated().sum())

    print("Validation completed!")

print("\nAll dataset checks completed.")
