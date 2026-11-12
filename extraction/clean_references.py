
import pandas as pd
from pathlib import Path

silver = Path("data/silver")
quarantine = Path("data/quarantine")
quarantine.mkdir(parents=True, exist_ok=True)

# Load Silver datasets
sales = pd.read_csv(silver / "sales.csv")
payments = pd.read_csv(silver / "payments.csv")
orders = pd.read_csv(silver / "orders.csv")
products = pd.read_csv(silver / "products.csv")

# Valid Order IDs and Product IDs
valid_orders = set(orders["order_id"])
valid_products = set(products["product_id"])

# Check Sales references
order_exists = sales["order_id"].isin(valid_orders)
product_exists = sales["product_id"].isin(valid_products)

sales["quarantine_reason"] = ""

sales.loc[~order_exists, "quarantine_reason"] += "Missing order; "
sales.loc[~product_exists, "quarantine_reason"] += "Missing product; "

invalid_sales = sales[~(order_exists & product_exists)].copy()
valid_sales = sales[order_exists & product_exists].copy()

# Remove temporary reason column from valid data
valid_sales = valid_sales.drop(columns=["quarantine_reason"])

# Save Sales outputs
invalid_sales.to_csv(
    quarantine / "invalid_sales_references.csv", index=False
)
valid_sales.to_csv(silver / "sales.csv", index=False)

# Check Payments references
payment_valid = payments["order_id"].isin(valid_orders)

invalid_payments = payments[~payment_valid].copy()
valid_payments = payments[payment_valid].copy()

# Save Payments outputs
invalid_payments.to_csv(
    quarantine / "invalid_payments_references.csv", index=False
)
valid_payments.to_csv(silver / "payments.csv", index=False)

print("=" * 50)
print("REFERENTIAL INTEGRITY CLEANING REPORT")
print("=" * 50)

print("Sales before:", len(sales))
print("Invalid sales:", len(invalid_sales))
print("Valid sales:", len(valid_sales))

print("Payments before:", len(payments))
print("Invalid payments:", len(invalid_payments))
print("Valid payments:", len(valid_payments))

print("\nReference cleaning completed!")
