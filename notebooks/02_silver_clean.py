# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Silver layer (cleaning)
# MAGIC - Fix data types
# MAGIC - Remove duplicates
# MAGIC - Handle NULLs
# MAGIC - Remove invalid values (negative price, bad dates)
# MAGIC - Referential integrity (orphan orders -> quarantine)

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window

def bronze(t):
    return spark.read.format("delta").load(f"{BRONZE}/delta/{t}")

def write_silver(df, t):
    (df.write.format("delta").mode("overwrite")
       .option("overwriteSchema", "true").save(f"{SILVER}/{t}"))
    print(f"silver.{t}: {df.count()} rows")

# COMMAND ----------
# MAGIC %md ## Customers: dedupe (keep latest), NULL handling

# COMMAND ----------

w = Window.partitionBy("customer_id").orderBy(F.col("updated_at").desc(), F.col("_ingest_ts").desc())

customers = (bronze("customers")
    .withColumn("customer_id", F.col("customer_id").cast("int"))
    .withColumn("signup_date", F.to_date("signup_date"))
    .withColumn("updated_at", F.to_timestamp("updated_at"))
    .withColumn("rn", F.row_number().over(w))
    .filter("rn = 1").drop("rn")                                   # duplicates removed
    .withColumn("email", F.lower(F.trim("email")))
    .withColumn("email", F.when(F.col("email").isNull(), F.lit("unknown@na.com")).otherwise(F.col("email")))
    .withColumn("city", F.coalesce(F.initcap(F.trim("city")), F.lit("Unknown")))
    .withColumn("name", F.initcap(F.trim("name")))
    .select("customer_id", "name", "email", "city", "signup_date", "updated_at"))
write_silver(customers, "customers")

# COMMAND ----------
# MAGIC %md ## Products: negative price -> absolute value is wrong, so we quarantine

# COMMAND ----------

p = (bronze("products")
     .withColumn("product_id", F.col("product_id").cast("int"))
     .withColumn("price", F.col("price").cast("double"))
     .dropDuplicates(["product_id"]))

bad_p = p.filter("price <= 0 OR price IS NULL")
good_p = p.filter("price > 0")
bad_p.write.format("delta").mode("overwrite").save(f"{SILVER}/_quarantine/products")
write_silver(good_p, "products")

# COMMAND ----------
# MAGIC %md ## Orders: valid dates + valid customers

# COMMAND ----------

o = (bronze("orders")
     .withColumn("order_id", F.col("order_id").cast("int"))
     .withColumn("customer_id", F.col("customer_id").cast("int"))
     .withColumn("order_date", F.to_date("order_date", "yyyy-MM-dd"))   # invalid -> NULL
     .dropDuplicates(["order_id"]))

valid_cust = customers.select("customer_id")
bad_o = (o.filter("order_date IS NULL")
         .unionByName(o.join(valid_cust, "customer_id", "left_anti")))
good_o = (o.filter("order_date IS NOT NULL")
           .join(valid_cust, "customer_id", "left_semi"))

bad_o.write.format("delta").mode("overwrite").save(f"{SILVER}/_quarantine/orders")
write_silver(good_o, "orders")

# COMMAND ----------
# MAGIC %md ## Sales & Payments: only for valid orders / products

# COMMAND ----------

valid_orders = good_o.select("order_id")
valid_products = good_p.select("product_id")

s = (bronze("sales")
     .select(F.col("sale_id").cast("int"), F.col("order_id").cast("int"),
             F.col("product_id").cast("int"), F.col("quantity").cast("int"),
             F.col("amount").cast("double"))
     .dropDuplicates(["sale_id"])
     .join(valid_orders, "order_id", "left_semi")
     .join(valid_products, "product_id", "left_semi")
     .filter("quantity > 0 AND amount > 0"))
write_silver(s, "sales")

pay = (bronze("payments")
       .select(F.col("payment_id").cast("int"), F.col("order_id").cast("int"),
               "method", F.col("amount").cast("double"))
       .dropDuplicates(["payment_id"])
       .join(valid_orders, "order_id", "left_semi")
       .filter("amount > 0"))
write_silver(pay, "payments")
