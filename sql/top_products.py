import sqlite3
import pandas as pd

connection = sqlite3.connect("data/warehouse/ecommerce.db")

query = """
SELECT
    product_id,
    product_name,
    category,
    total_quantity,
    total_revenue
FROM product_performance
ORDER BY total_revenue DESC
LIMIT 10;
"""

result = pd.read_sql_query(query, connection)

print("\nTOP 10 PRODUCTS BY REVENUE")
print("=" * 60)
print(result.to_string(index=False))

connection.close()
