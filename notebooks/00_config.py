# Databricks notebook source
# MAGIC %md
# MAGIC # 00 - Config (run via `%run ./00_config` in other notebooks)

# COMMAND ----------

# ---- CHANGE THESE ----
STORAGE_ACCOUNT = "<your-storage-account-name>"   # from azure/.env
# Recommended: store the key in a Databricks secret scope instead of hard-coding:
#   ACCOUNT_KEY = dbutils.secrets.get(scope="ecom", key="adls-key")
ACCOUNT_KEY = "<your-storage-account-key>"
# ----------------------

spark.conf.set(f"fs.azure.account.key.{STORAGE_ACCOUNT}.dfs.core.windows.net", ACCOUNT_KEY)

def path(container: str, folder: str = "") -> str:
    return f"abfss://{container}@{STORAGE_ACCOUNT}.dfs.core.windows.net/{folder}".rstrip("/")

LANDING = path("landing")
BRONZE = path("bronze")
SILVER = path("silver")
GOLD = path("gold")

TABLES = ["customers", "products", "orders", "sales", "payments"]
