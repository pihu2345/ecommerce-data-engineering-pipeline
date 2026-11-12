
import sqlite3
import pandas as pd

connection = sqlite3.connect("data/warehouse/ecommerce.db")

queries = {
    "CATEGORY-WISE REVENUE": """
        SELECT
            category,
            SUM(total_quantity) AS total_quantity,
            ROUND(SUM(total_revenue), 2) AS revenue
        FROM product_performance
        GROUP BY category
        ORDER BY revenue DESC;
    """,

    "MONTHLY REVENUE": """
        SELECT
            strftime('%Y-%m', order_day) AS month,
            SUM(total_orders) AS total_orders,
            ROUND(SUM(total_revenue), 2) AS revenue
        FROM daily_sales_summary
        GROUP BY month
        ORDER BY month;
    """,

    "AVERAGE ORDER VALUE": """
        SELECT
            ROUND(
                SUM(total_revenue) * 1.0 /
                NULLIF(SUM(total_orders), 0),
                2
            ) AS average_order_value
        FROM daily_sales_summary;
    """,

    "MONTH-ON-MONTH REVENUE GROWTH": """
        WITH monthly AS (
            SELECT
                strftime('%Y-%m', order_day) AS month,
                SUM(total_revenue) AS revenue
            FROM daily_sales_summary
            GROUP BY month
        ),
        comparison AS (
            SELECT
                month,
                revenue,
                LAG(revenue) OVER (ORDER BY month) AS previous_revenue
            FROM monthly
        )
        SELECT
            month,
            ROUND(revenue, 2) AS revenue,
            ROUND(previous_revenue, 2) AS previous_revenue,
            ROUND(
                (revenue - previous_revenue) * 100.0 /
                NULLIF(previous_revenue, 0),
                2
            ) AS growth_percentage
        FROM comparison
        ORDER BY month;
    """
}

for title, query in queries.items():
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)

    result = pd.read_sql_query(query, connection)
    print(result.to_string(index=False))

connection.close()
