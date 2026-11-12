# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Incremental loading (watermark + MERGE)
# MAGIC Only process NEW / CHANGED rows instead of reloading everything.
# MAGIC 1. Read last watermark (max order_id loaded)
# MAGIC 2. Read only newer rows from Bronze
# MAGIC 3. `MERGE` (upsert) into Silver -> idempotent, safe to re-run

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

from delta.tables import DeltaTable
from pyspark.sql import functions as F

WM_PATH = f"{SILVER}/_watermark/orders"

def get_watermark():
    try:
        return spark.read.format("delta").load(WM_PATH).agg(F.max("last_order_id")).first()[0] or 0
    except Exception:
        return 0

def set_watermark(v):
    (spark.createDataFrame([(int(v),)], ["last_order_id"])
          .write.format("delta").mode("overwrite").save(WM_PATH))

# COMMAND ----------

last_id = get_watermark()
print("last watermark:", last_id)

new_orders = (spark.read.format("delta").load(f"{BRONZE}/delta/orders")
    .withColumn("order_id", F.col("order_id").cast("int"))
    .withColumn("customer_id", F.col("customer_id").cast("int"))
    .withColumn("order_date", F.to_date("order_date"))
    .filter(f"order_id > {last_id} AND order_date IS NOT NULL")
    .dropDuplicates(["order_id"])
    .select("order_id", "customer_id", "order_date", "status"))

print("new orders:", new_orders.count())

# COMMAND ----------

if new_orders.count() > 0:
    target = DeltaTable.forPath(spark, f"{SILVER}/orders")
    (target.alias("t")
        .merge(new_orders.alias("s"), "t.order_id = s.order_id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute())
    set_watermark(new_orders.agg(F.max("order_id")).first()[0])
    print("MERGE done, new watermark set")
else:
    print("nothing new")

# COMMAND ----------
# MAGIC %md ### Delta Lake time travel (interview bonus)

# COMMAND ----------

display(spark.sql(f"DESCRIBE HISTORY delta.`{SILVER}/orders`"))
# spark.read.format("delta").option("versionAsOf", 0).load(f"{SILVER}/orders")
