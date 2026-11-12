
import pandas as pd

df = pd.read_csv("data/customers.csv")

# 1. Check duplicate customer IDs
duplicate_ids = df[df.duplicated(
    subset=["customer_id"], keep=False
)]

print("Total customer records:", len(df))
print("Unique customer IDs:", df["customer_id"].nunique())
print("Duplicate customer ID rows:", len(duplicate_ids))

# 2. Display duplicate records
print("\nDuplicate Customer Records:")
print(duplicate_ids.sort_values("customer_id").to_string(index=False))

# 3. Check missing email and city
print("\nMissing Email Records:")
print(df[df["email"].isnull()][["customer_id", "email"]].head())

print("\nMissing City Records:")
print(df[df["city"].isnull()][["customer_id", "city"]].head())
