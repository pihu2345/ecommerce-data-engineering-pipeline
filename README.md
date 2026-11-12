# End-to-End E-Commerce Data Engineering Pipeline (Azure)

Medallion architecture (Bronze -> Silver -> Gold) on Azure using ADF, ADLS Gen2, Databricks, PySpark, Delta Lake and Power BI.

## Architecture
```
Python (Faker) -> CSV
      |
      v
ADLS Gen2: landing  --(Azure Data Factory: ForEach + Copy, retry)-->  bronze (raw)
                                                                          |
                                         Databricks (PySpark + Delta)     v
                                                              silver (clean, dedupe, validated)
                                                                          |
                                                                          v
                                                              gold (aggregates, SCD2 dim)
                                                                          |
                                                                          v
                                                                     Power BI
```

## Tech stack
Python, SQL, Azure Data Factory, ADLS Gen2, Databricks, PySpark, Delta Lake, Power BI, Azure CLI

## Project structure
```
extraction/generate_data.py   # synthetic data with intentional dirty records
azure/                        # az CLI scripts: provision, upload, deploy ADF
adf/                          # linked service, datasets, pipeline JSON
notebooks/                    # 00_config, 01_bronze, 02_silver, 03_gold, 04_incremental, 05_scd2
sql/analytics.sql             # window functions, MoM growth, segmentation, DQ checks
docs/                         # step-by-step guide, interview Q&A
```

## Key features
- Data quality: dedupe (window `row_number`), NULL handling, invalid dates, negative prices, orphan records -> quarantine
- Incremental load with watermark + Delta `MERGE`
- SCD Type 2 customer dimension
- `OPTIMIZE` + `ZORDER`, ADF retries, idempotent re-runs

## How to run
See [docs/STEP_BY_STEP.md](docs/STEP_BY_STEP.md).

## Dashboard
Add Power BI screenshots in `docs/` (revenue KPI, monthly trend, category, city, payment mix).

## Author
<your name> | <LinkedIn> | <GitHub>
