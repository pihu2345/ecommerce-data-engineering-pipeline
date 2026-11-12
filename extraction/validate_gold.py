
import pandas as pd
from pathlib import Path

gold_folder = Path("data/gold")

tables = {
    "daily_sales_summary.csv": "order_day",
    "product_performance.csv": "product_id",
    "customer_analytics.csv": "customer_id"
}

print("=" * 55)
print("          GOLD LAYER VALIDATION REPORT")
print("=" * 55)

for file, primary_key in tables.items():

    df = pd.read_csv(gold_folder / file)

    print("\nDataset:", file)
    print("Total rows:", len(df))
    print("Missing values:", df.isnull().sum().sum())
    print(
        "Duplicate primary keys:",
        df[primary_key].duplicated().sum()
    )

    print("Validation completed!")

print("\nAll Gold tables checked successfully!")
