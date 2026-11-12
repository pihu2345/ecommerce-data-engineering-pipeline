
import pandas as pd
from pathlib import Path

# Read Bronze data
df = pd.read_csv("data/payments.csv")

print("Total payments before cleaning:", len(df))

# Remove exact duplicate rows
df_clean = df.drop_duplicates()

# Validate payment amount
valid_payments = df_clean[
    df_clean["amount"] > 0
].copy()

invalid_payments = df_clean[
    df_clean["amount"] <= 0
].copy()

# Create folders
Path("data/silver").mkdir(parents=True, exist_ok=True)
Path("data/quarantine").mkdir(parents=True, exist_ok=True)

# Save Silver data
valid_payments.to_csv(
    "data/silver/payments.csv",
    index=False
)

# Save invalid records
invalid_payments.to_csv(
    "data/quarantine/invalid_payments.csv",
    index=False
)

print("Valid payments:", len(valid_payments))
print("Invalid payments:", len(invalid_payments))
print("Silver payments file created!")
