# Step-by-Step Guide (terminal se poora project)

Har step ke baad **khud check karo** ki output sahi aaya. Atko toh error copy karke poochho.

---
## Step 0: Setup (Day 0)
```bash
python --version                    # 3.10+
pip install -r requirements.txt
# Azure CLI install: https://learn.microsoft.com/cli/azure/install-azure-cli
az --version
az login                            # browser khulega, free account se login
az account show                     # subscription check
```

## Step 1: Data generate karo (Day 1-2)
```bash
python extraction/generate_data.py
python extraction/generate_data.py --incremental
```
Check karo: `data/` mein 5 CSV, `data/incremental/` mein 4 CSV.
Khud dekho gandagi: `head data/customers.csv`, NULL emails, negative prices.

## Step 2: Azure resources banao (Day 3)
```bash
bash azure/01_setup_azure.sh
```
Ye banata hai: Resource Group, ADLS Gen2 (landing/bronze/silver/gold), ADF, Databricks.
Portal par jaake verify karo (portal.azure.com -> Resource groups -> rg-ecommerce-de).

## Step 3: Data landing mein upload karo
```bash
bash azure/02_upload_to_landing.sh full
```

## Step 4: ADF pipeline deploy aur run karo (Day 4)
```bash
bash azure/03_deploy_adf.sh
source azure/.env
az datafactory pipeline create-run -g $RG --factory-name $ADF_NAME \
   --name pl_ingest_landing_to_bronze
```
Status dekho: ADF Studio -> Monitor. Bronze container mein `<table>/load_date=.../` folders aane chahiye.

## Step 5: Databricks setup (Day 5)
1. Portal -> Databricks workspace -> **Launch Workspace**
2. Compute -> Create cluster (single node, smallest size, auto-terminate 20 min) **cost bachane ke liye**
3. Workspace -> Import -> `notebooks/*.py` sab import karo (Databricks .py notebook format support karta hai)
4. `00_config` mein `STORAGE_ACCOUNT` aur `ACCOUNT_KEY` bharo
   (key: `az storage account keys list -g $RG -n $STORAGE --query "[0].value" -o tsv`)

## Step 6: Medallion run karo (Day 5-9)
Order mein run karo:
1. `01_bronze_ingest`
2. `02_silver_clean`
3. `03_gold_aggregates`

Check karo: Silver mein customers ~1000 (1040 nahi), products 192 (8 negative price quarantine), orders mein bad dates/orphans quarantine.

## Step 7: SQL (Day 10-11)
`sql/analytics.sql` ki queries Databricks SQL / notebook mein run karo.
Pehle Gold tables register karo (file ke top par comment mein command hai).

## Step 8: Incremental + SCD2 (Day 12-13)
```bash
bash azure/02_upload_to_landing.sh incremental     # naye orders + changed customers
```
ADF pipeline dobara run karo (parameters: `load_type=incremental`, `run_date=<aaj ki date>`):
```bash
source azure/.env
az datafactory pipeline create-run -g $RG --factory-name $ADF_NAME \
  --name pl_ingest_landing_to_bronze \
  --parameters '{"load_type":"incremental","run_date":"'$(date +%F)'"}'
```
Phir notebooks: `01_bronze_ingest` -> `04_incremental_load` -> `05_scd2_customers` -> `03_gold_aggregates`.

## Step 9: Power BI (Day 14)
1. Power BI Desktop (Windows) install karo
2. Get Data -> **Azure Data Lake Storage Gen2** -> `https://<storage>.dfs.core.windows.net/gold`
   (ya Databricks connector use karo)
3. Tables: `monthly_revenue`, `category_revenue`, `top_products`, `city_revenue`, `payment_methods`
4. Visuals: KPI cards (revenue, orders, AOV), line chart (monthly), bar (category), map (city), donut (payments)
5. Screenshot `docs/` mein save karo

## Step 10: GitHub (Day 15)
```bash
git init && git add . && git commit -m "E-commerce DE pipeline"
git remote add origin https://github.com/<username>/ecommerce-data-engineering-pipeline.git
git push -u origin main
```
`.gitignore` already `azure/.env` aur `data/` ko exclude karta hai.

## COST WARNING
- Kaam khatam hone par: `az group delete -n rg-ecommerce-de --yes` (sab delete, billing band)
- Databricks cluster auto-terminate zaroor rakho
