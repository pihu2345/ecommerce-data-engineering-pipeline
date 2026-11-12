
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SILVER = BASE_DIR / "data" / "silver"

print("=" * 60)
print("       AUTOMATED DATA QUALITY TESTS")
print("=" * 60)

tests_passed = 0
tests_failed = 0


def check_test(test_name, condition):
    global tests_passed, tests_failed

    if condition:
        print(f"PASS: {test_name}")
        tests_passed += 1
    else:
        print(f"FAIL: {test_name}")
        tests_failed += 1


# Load Silver datasets
customers = pd.read_csv(SILVER / "customers.csv")
products = pd.read_csv(SILVER / "products.csv")
orders = pd.read_csv(SILVER / "orders.csv")
sales = pd.read_csv(SILVER / "sales.csv")
payments = pd.read_csv(SILVER / "payments.csv")


# Test 1: Primary key duplicates
check_test(
    "Customers duplicate IDs",
    not customers["customer_id"].duplicated().any()
)

check_test(
    "Products duplicate IDs",
    not products["product_id"].duplicated().any()
)

check_test(
    "Orders duplicate IDs",
    not orders["order_id"].duplicated().any()
)

check_test(
    "Sales duplicate IDs",
    not sales["sale_id"].duplicated().any()
)

check_test(
    "Payments duplicate IDs",
    not payments["payment_id"].duplicated().any()
)


# Test 2: Required columns should not be null
check_test(
    "Customers IDs not null",
    customers["customer_id"].notna().all()
)

check_test(
    "Products IDs not null",
    products["product_id"].notna().all()
)

check_test(
    "Orders IDs not null",
    orders["order_id"].notna().all()
)


# Test 3: Referential integrity
check_test(
    "Sales order references valid",
    sales["order_id"].isin(orders["order_id"]).all()
)

check_test(
    "Sales product references valid",
    sales["product_id"].isin(products["product_id"]).all()
)

check_test(
    "Payments order references valid",
    payments["order_id"].isin(orders["order_id"]).all()
)


# Final report
print("\n" + "=" * 60)
print("DATA QUALITY TEST REPORT")
print("=" * 60)

print("Tests passed:", tests_passed)
print("Tests failed:", tests_failed)

if tests_failed > 0:
    raise SystemExit("DATA QUALITY TESTS FAILED!")

print("\nALL DATA QUALITY TESTS PASSED!")
