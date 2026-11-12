
import pandas as pd
from pathlib import Path

data_folder = Path("data")

files = [
    "customers.csv",
    "products.csv",
    "orders.csv",
    "sales.csv",
    "payments.csv"
]

for file in files:
    print("\n" + "=" * 50)
    print("FILE:", file)

    df = pd.read_csv(data_folder / file)

    print("Total Rows:", len(df))
    print("Total Columns:", len(df.columns))

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nNULL Values:")
    print(df.isnull().sum())

    print("\nDuplicate Rows:", df.duplicated().sum())

    print("\nData Types:")
    print(df.dtypes)
