
import pandas as pd
from pathlib import Path

silver = Path("data/silver")
gold = Path("data/gold")

# Read Silver datasets
sales = pd.read_csv(silver / "sales.csv")
orders = pd.read_csv(silver / "orders.csv")

# Convert order date into datetime
orders["order_date"] = pd.to_datetime(
    orders["order_date"],
    errors="coerce"
)

# Join Sales with Orders
merged = sales.merge(
    orders[["order_id", "order_date"]],
    on="order_id",
    how="inner"
)

# Extract date
merged["order_day"] = merged["order_date"].dt.date

# Create daily sales summary
daily_sales = (
    merged.groupby("order_day")
    .agg(
        total_orders=("order_id", "nunique"),
        total_sales=("sale_id", "count"),
        total_quantity=("quantity", "sum"),
        total_revenue=("amount", "sum")
    )
    .reset_index()
)

# Save Gold table
daily_sales.to_csv(
    gold / "daily_sales_summary.csv",
    index=False
)

print("=" * 50)
print("GOLD LAYER - DAILY SALES SUMMARY")
print("=" * 50)

print("Total days:", len(daily_sales))
print("\nPreview:")
print(daily_sales.head(10))

print("\nTotal revenue:", daily_sales["total_revenue"].sum())

print("\nGold table created successfully!")

# ==========================================
# GOLD TABLE 2 - PRODUCT PERFORMANCE
# ==========================================

products = pd.read_csv(silver / "products.csv")
sales = pd.read_csv(silver / "sales.csv")

# Join Sales with Products
product_data = sales.merge(
    products,
    on="product_id",
    how="inner"
)

# Aggregate product-level performance
product_performance = (
    product_data.groupby(
        ["product_id", "product_name", "category"]
    )
    .agg(
        total_quantity=("quantity", "sum"),
        total_sales=("sale_id", "count"),
        total_revenue=("amount", "sum")
    )
    .reset_index()
)

# Sort by revenue (highest first)
product_performance = product_performance.sort_values(
    by="total_revenue",
    ascending=False
)

# Save Gold table
product_performance.to_csv(
    gold / "product_performance.csv",
    index=False
)

print("\n" + "=" * 50)
print("GOLD LAYER - PRODUCT PERFORMANCE")
print("=" * 50)

print("\nTop 10 Products by Revenue:")
print(product_performance.head(10))

print("\nProduct performance table created successfully!")

# ==========================================
# GOLD TABLE 3 - CUSTOMER ANALYTICS
# ==========================================

customers = pd.read_csv(silver / "customers.csv")
orders = pd.read_csv(silver / "orders.csv")
sales = pd.read_csv(silver / "sales.csv")

# Join Customers with Orders
customer_orders = orders.merge(
    customers,
    on="customer_id",
    how="inner"
)

# Join with Sales
customer_data = customer_orders.merge(
    sales,
    on="order_id",
    how="inner"
)

# Aggregate customer-level metrics
customer_analytics = (
    customer_data.groupby(
        ["customer_id", "name", "city"]
    )
    .agg(
        total_orders=("order_id", "nunique"),
        total_items=("quantity", "sum"),
        total_spending=("amount", "sum")
    )
    .reset_index()
)

# Sort by spending
customer_analytics = customer_analytics.sort_values(
    by="total_spending",
    ascending=False
)

# Save Gold table
customer_analytics.to_csv(
    gold / "customer_analytics.csv",
    index=False
)

print("\n" + "=" * 50)
print("GOLD LAYER - CUSTOMER ANALYTICS")
print("=" * 50)

print("\nTop 10 Customers by Spending:")
print(customer_analytics.head(10))

print("\nTotal customers:", len(customer_analytics))

print("\nCustomer analytics table created successfully!")


