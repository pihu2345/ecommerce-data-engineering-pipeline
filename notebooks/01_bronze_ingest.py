# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Bronze layer
# MAGIC Raw CSV (from ADF) -> Delta. **No cleaning here.** Keep data as-is + add audit columns.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

from pyspark.sql import functions as F

dbutils.widgets.text("load_type", "full")          # full | incremental
dbutils.widgets.text("run_date", "")               # yyyy-mm-dd (incremental)
load_type = dbutils.widgets.get("load_type")

# COMMAND ----------

for t in TABLES:
    src = f"{BRONZE}/{t}/"                          # ADF wrote: bronze/<table>/load_date=YYYY-MM-DD/<table>.csv
    try:
        df = (spark.read.option("header", True)
                        .option("inferSchema", False)   # keep everything as string in Bronze
                        .option("recursiveFileLookup", True)
                        .csv(src))
    except Exception as e:
        print(f"skip {t}: {e}")
        continue

    df = (df.withColumn("_ingest_ts", F.current_timestamp())
            .withColumn("_source_file", F.input_file_name())
            .withColumn("_load_type", F.lit(load_type)))

    (df.write.format("delta")
       .mode("append")
       .save(f"{BRONZE}/delta/{t}"))
    print(f"bronze.{t}: {df.count()} rows")
