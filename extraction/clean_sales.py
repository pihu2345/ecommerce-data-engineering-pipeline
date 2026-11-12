
import pandas as pd
from pathlib import Path

# Read Bronze data
df = pd.read_csv("data/sales.csv")

print("Total sales before cleaning:", len(df))

# Remove exact duplicate rows
df_clean = df.drop_duplicates()

# Apply business validation rules
valid_sales = df_clean[
    (df_clean["quantity"] > 0) &
    (df_clean["amount"] > 0)
].copy()

invalid_sales = df_clean[
    (df_clean["quantity"] <= 0) |
    (df_clean["amount"] <= 0)
].copy()

# Create folders
Path("data/silver").mkdir(parents=True, exist_ok=True)
Path("data/quarantine").mkdir(parents=True, exist_ok=True)

# Save Silver data
valid_sales.to_csv(
    "data/silver/sales.csv",
    index=False
)

# Save invalid data
invalid_sales.to_csv(
    "data/quarantine/invalid_sales.csv",
    index=False
)

print("Valid sales:", len(valid_sales))
print("Invalid sales:", len(invalid_sales))
print("Silver sales file created!")

