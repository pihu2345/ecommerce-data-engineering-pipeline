
import sqlite3

connection = sqlite3.connect("data/warehouse/ecommerce.db")

query = """
SELECT name
FROM sqlite_master
WHERE type = 'table'
"""

tables = connection.execute(query).fetchall()

print("Tables available in Data Warehouse:")

for table in tables:
    print(table[0])

connection.close()
