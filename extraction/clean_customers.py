
import pandas as pd
from pathlib import Path

# Read raw customer data
df = pd.read_csv("data/customers.csv")

print("Before cleaning:", len(df))

# Remove exact duplicate records
df_clean = df.drop_duplicates()

print("After removing exact duplicates:", len(df_clean))

# Check primary key uniqueness
print(
    "Duplicate customer IDs remaining:",
    df_clean["customer_id"].duplicated().sum()
)

# Keep missing email and city values unchanged

# Create Silver folder
Path("data/silver").mkdir(parents=True, exist_ok=True)

# Save cleaned data
df_clean.to_csv(
    "data/silver/customers.csv",
    index=False
)

print("Silver customers file created successfully!")
