
import pandas as pd
from pathlib import Path

# Read Bronze orders data
df = pd.read_csv("data/orders.csv")

print("Total orders before cleaning:", len(df))

# Convert order_date into datetime
df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="coerce"
)

# Separate valid and invalid dates
valid_orders = df[df["order_date"].notna()].copy()
invalid_orders = df[df["order_date"].isna()].copy()

print("Valid orders:", len(valid_orders))
print("Invalid orders:", len(invalid_orders))

# Create folders
Path("data/silver").mkdir(parents=True, exist_ok=True)
Path("data/quarantine").mkdir(parents=True, exist_ok=True)

# Save valid orders
valid_orders.to_csv(
    "data/silver/orders.csv",
    index=False
)

# Save invalid orders
invalid_orders.to_csv(
    "data/quarantine/invalid_orders.csv",
    index=False
)

print("Silver orders file created!")
print("Invalid orders moved to quarantine!")
