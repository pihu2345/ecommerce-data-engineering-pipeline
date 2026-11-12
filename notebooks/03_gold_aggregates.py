# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Gold layer (business aggregations for Power BI)

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

from pyspark.sql import functions as F

def silver(t):
    return spark.read.format("delta").load(f"{SILVER}/{t}")

def write_gold(df, name):
    (df.write.format("delta").mode("overwrite")
       .option("overwriteSchema", "true").save(f"{GOLD}/{name}"))
    print(f"gold.{name}: {df.count()} rows")

customers, products = silver("customers"), silver("products")
orders, sales, payments = silver("orders"), silver("sales"), silver("payments")

# COMMAND ----------
# MAGIC %md ## Fact table: one row per sale line

# COMMAND ----------

fact_sales = (sales
    .join(orders, "order_id")
    .join(products.select("product_id", "product_name", "category"), "product_id")
    .join(customers.select("customer_id", "name", "city"), "customer_id")
    .select("sale_id", "order_id", "order_date", "status", "customer_id", "name", "city",
            "product_id", "product_name", "category", "quantity", "amount")
    .withColumn("year", F.year("order_date"))
    .withColumn("month", F.month("order_date")))
write_gold(fact_sales, "fact_sales")

# COMMAND ----------
# MAGIC %md ## Aggregates

# COMMAND ----------

valid = fact_sales.filter(~F.col("status").isin("Cancelled", "Returned"))

# 1. Monthly revenue
write_gold(valid.groupBy("year", "month")
           .agg(F.round(F.sum("amount"), 2).alias("revenue"),
                F.countDistinct("order_id").alias("orders"))
           .orderBy("year", "month"), "monthly_revenue")

# 2. Revenue by category
write_gold(valid.groupBy("category")
           .agg(F.round(F.sum("amount"), 2).alias("revenue"),
                F.sum("quantity").alias("units_sold"))
           .orderBy(F.desc("revenue")), "category_revenue")

# 3. Top 10 products
write_gold(valid.groupBy("product_id", "product_name")
           .agg(F.round(F.sum("amount"), 2).alias("revenue"))
           .orderBy(F.desc("revenue")).limit(10), "top_products")

# 4. Customer lifetime value
write_gold(valid.groupBy("customer_id", "name", "city")
           .agg(F.round(F.sum("amount"), 2).alias("lifetime_value"),
                F.countDistinct("order_id").alias("total_orders"))
           .orderBy(F.desc("lifetime_value")), "customer_ltv")

# 5. Revenue by city
write_gold(valid.groupBy("city")
           .agg(F.round(F.sum("amount"), 2).alias("revenue"))
           .orderBy(F.desc("revenue")), "city_revenue")

# 6. Payment method share
write_gold(payments.groupBy("method")
           .agg(F.count("*").alias("payments"), F.round(F.sum("amount"), 2).alias("amount"))
           .orderBy(F.desc("amount")), "payment_methods")

# 7. Order status funnel
write_gold(orders.groupBy("status").count().orderBy(F.desc("count")), "order_status")

# COMMAND ----------
# MAGIC %md ## Performance tuning (interview topic)
# MAGIC `OPTIMIZE` compacts small files, `ZORDER` co-locates data for faster filters.

# COMMAND ----------

spark.sql(f"OPTIMIZE delta.`{GOLD}/fact_sales` ZORDER BY (order_date, category)")
