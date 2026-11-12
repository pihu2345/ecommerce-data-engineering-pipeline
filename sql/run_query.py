import sqlite3
import pandas as pd

connection = sqlite3.connect("data/warehouse/ecommerce.db")

query = """
SELECT
    customer_id,
    name,
    city,
    total_orders,
    total_spending
FROM customer_analytics
ORDER BY total_spending DESC
LIMIT 10;
"""

result = pd.read_sql_query(query, connection)

print("\nTOP 10 CUSTOMERS BY REVENUE")
print("=" * 60)
print(result.to_string(index=False))

connection.close()