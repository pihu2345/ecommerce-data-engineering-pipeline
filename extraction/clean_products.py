
import pandas as pd
from pathlib import Path

# Read Bronze data
df = pd.read_csv("data/products.csv")

print("Total products before cleaning:", len(df))

# Separate valid and invalid records
valid_products = df[df["price"] > 0].copy()
invalid_products = df[df["price"] <= 0].copy()

print("Valid products:", len(valid_products))
print("Invalid products:", len(invalid_products))

# Create Silver and quarantine folders
Path("data/silver").mkdir(parents=True, exist_ok=True)
Path("data/quarantine").mkdir(parents=True, exist_ok=True)

# Save valid products to Silver
valid_products.to_csv(
    "data/silver/products.csv",
    index=False
)

# Save invalid products separately
invalid_products.to_csv(
    "data/quarantine/invalid_products.csv",
    index=False
)

print("Silver products file created!")
print("Invalid products moved to quarantine!")
