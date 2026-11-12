"""
Day 1-2: Generate fake E-Commerce data (5 tables) with INTENTIONAL dirty data.

Usage:
    python extraction/generate_data.py                 # full load  -> data/
    python extraction/generate_data.py --incremental   # new orders -> data/incremental/

Tables: customers, products, orders, payments, sales
Dirty data added on purpose (cleaned later in the Silver layer):
    - duplicate customers
    - NULL emails / cities
    - negative product prices
    - invalid order dates
    - orders pointing to missing customers (orphans)
"""
import argparse
import os
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

SEED = 42
random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

N_CUSTOMERS = 1000
N_PRODUCTS = 200
N_ORDERS = 5000

CATEGORIES = ["Electronics", "Fashion", "Home", "Beauty", "Books", "Sports", "Grocery"]
STATUSES = ["Delivered", "Shipped", "Cancelled", "Returned", "Pending"]
PAY_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking", "COD"]
CITIES = ["Jaipur", "Delhi", "Mumbai", "Bengaluru", "Pune", "Hyderabad", "Chennai", "Kolkata"]

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def make_customers(n):
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "customer_id": i,
            "name": fake.name(),
            "email": fake.email(),
            "city": random.choice(CITIES),
            "signup_date": fake.date_between(start_date="-3y", end_date="today").isoformat(),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        })
    df = pd.DataFrame(rows)
    # dirty: NULL emails + NULL cities
    df.loc[df.sample(frac=0.05, random_state=1).index, "email"] = None
    df.loc[df.sample(frac=0.03, random_state=2).index, "city"] = None
    # dirty: duplicates
    df = pd.concat([df, df.sample(40, random_state=3)], ignore_index=True)
    return df


def make_products(n):
    rows = []
    for i in range(1, n + 1):
        cat = random.choice(CATEGORIES)
        rows.append({
            "product_id": i,
            "product_name": f"{cat} Item {i}",
            "category": cat,
            "price": round(random.uniform(99, 49999), 2),
        })
    df = pd.DataFrame(rows)
    # dirty: negative prices
    df.loc[df.sample(8, random_state=4).index, "price"] *= -1
    return df


def make_orders(n, start_id=1, order_date_from="-1y"):
    rows = []
    for i in range(start_id, start_id + n):
        rows.append({
            "order_id": i,
            "customer_id": random.randint(1, N_CUSTOMERS),
            "order_date": fake.date_between(start_date=order_date_from, end_date="today").isoformat(),
            "status": random.choice(STATUSES),
        })
    df = pd.DataFrame(rows)
    # dirty: invalid dates
    bad = df.sample(frac=0.01, random_state=5).index
    df.loc[bad, "order_date"] = random.choice(["2099-99-99", "not_a_date", "31-31-2025"])
    # dirty: orphan customers
    orphan = df.sample(frac=0.01, random_state=6).index
    df.loc[orphan, "customer_id"] = 99999
    return df


def make_sales_and_payments(orders, products):
    sales, payments = [], []
    sale_id, pay_id = 1, 1
    prod_ids = products["product_id"].tolist()
    price_map = products.set_index("product_id")["price"].abs().to_dict()
    for _, o in orders.iterrows():
        total = 0.0
        for _ in range(random.randint(1, 3)):
            pid = random.choice(prod_ids)
            qty = random.randint(1, 4)
            amount = round(price_map[pid] * qty, 2)
            total += amount
            sales.append({
                "sale_id": sale_id, "order_id": o["order_id"],
                "product_id": pid, "quantity": qty, "amount": amount,
            })
            sale_id += 1
        payments.append({
            "payment_id": pay_id, "order_id": o["order_id"],
            "method": random.choice(PAY_METHODS), "amount": round(total, 2),
        })
        pay_id += 1
    return pd.DataFrame(sales), pd.DataFrame(payments)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--incremental", action="store_true",
                        help="Generate only NEW orders (for incremental load demo)")
    args = parser.parse_args()

    products = make_products(N_PRODUCTS)

    if args.incremental:
        out = os.path.join(OUT_DIR, "incremental")
        os.makedirs(out, exist_ok=True)
        orders = make_orders(500, start_id=N_ORDERS + 1, order_date_from="-7d")
        sales, payments = make_sales_and_payments(orders, products)
        # changed customers (for SCD Type 2 demo)
        customers = make_customers(50)
        customers["city"] = random.choice(CITIES)
        customers = customers.drop_duplicates("customer_id")
        customers["updated_at"] = datetime.now().isoformat(timespec="seconds")
        tables = {"customers": customers, "orders": orders, "sales": sales, "payments": payments}
    else:
        out = OUT_DIR
        os.makedirs(out, exist_ok=True)
        customers = make_customers(N_CUSTOMERS)
        orders = make_orders(N_ORDERS)
        sales, payments = make_sales_and_payments(orders, products)
        tables = {"customers": customers, "products": products,
                  "orders": orders, "sales": sales, "payments": payments}

    for name, df in tables.items():
        path = os.path.join(out, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"{name:10s} -> {len(df):6d} rows -> {os.path.normpath(path)}")


if __name__ == "__main__":
    main()
