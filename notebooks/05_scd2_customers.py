# Databricks notebook source
# MAGIC %md
# MAGIC # 05 - SCD Type 2 on customers (track history of city changes)
# MAGIC Columns added: `effective_from`, `effective_to`, `is_current`.
# MAGIC When a customer's city/email changes -> close the old row, insert a new row.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

from delta.tables import DeltaTable
from pyspark.sql import functions as F

DIM = f"{GOLD}/dim_customer_scd2"
src = spark.read.format("delta").load(f"{SILVER}/customers")

# COMMAND ----------
# MAGIC %md ## First run: create the dimension

# COMMAND ----------

if not DeltaTable.isDeltaTable(spark, DIM):
    (src.withColumn("effective_from", F.current_timestamp())
        .withColumn("effective_to", F.lit(None).cast("timestamp"))
        .withColumn("is_current", F.lit(True))
        .write.format("delta").save(DIM))
    print("dim_customer_scd2 created")

# COMMAND ----------
# MAGIC %md ## Every later run: 2-step SCD2 merge

# COMMAND ----------

dim = DeltaTable.forPath(spark, DIM)
current = dim.toDF().filter("is_current = true")

# rows whose tracked attributes changed
changed = (src.alias("s").join(current.alias("d"), "customer_id")
           .filter("s.city <> d.city OR s.email <> d.email")
           .select("s.*"))
new_cust = src.alias("s").join(current.alias("d"), "customer_id", "left_anti")

# IMPORTANT: Spark is lazy. After step 1 the "current" rows change, so `changed`
# would be re-evaluated to empty. Materialize it in a staging Delta table first.
STAGE = f"{GOLD}/_staging/customer_changes"
changed.unionByName(new_cust).write.format("delta").mode("overwrite").save(STAGE)
changed_ids = spark.read.format("delta").load(STAGE)

# Step 1: close old versions (only customers that already exist & changed)
(dim.alias("d")
    .merge(changed_ids.alias("s"), "d.customer_id = s.customer_id AND d.is_current = true")
    .whenMatchedUpdate(set={"is_current": F.lit(False), "effective_to": F.current_timestamp()})
    .execute())

# Step 2: insert new versions (changed + brand-new customers)
(changed_ids.withColumn("effective_from", F.current_timestamp())
            .withColumn("effective_to", F.lit(None).cast("timestamp"))
            .withColumn("is_current", F.lit(True))
            .write.format("delta").mode("append").save(DIM))

print("versions inserted:", changed_ids.count())

# COMMAND ----------

display(spark.read.format("delta").load(DIM)
        .orderBy("customer_id", "effective_from"))
