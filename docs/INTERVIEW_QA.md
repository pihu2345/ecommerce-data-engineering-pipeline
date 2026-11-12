# Interview Q&A (is project ke basis par)

**Q1. End-to-end pipeline kaise banayi?**
Python (Faker) se 5 tables generate kiye -> Azure CLI se ADLS Gen2 + ADF + Databricks provision kiye -> ADF `ForEach` + `Copy` se landing se bronze ingestion -> Databricks PySpark se Bronze/Silver/Gold (Delta Lake) -> Gold tables Power BI mein.

**Q2. Duplicate records kaise handle kiye?**
`row_number()` over `partition by customer_id order by updated_at desc` aur `rn = 1` rakha (latest record survive). Simple cases mein `dropDuplicates(["id"])`.

**Q3. NULL values kaise handle kiye?**
Business rule ke hisaab se: email NULL -> `unknown@na.com`, city NULL -> `Unknown` (`coalesce`). Jahan NULL critical tha (order_date), row quarantine table mein gayi.

**Q4. Invalid data (negative price, orphan orders)?**
Delete nahi kiya, `_quarantine` folder mein rakha taaki audit ho sake. Orphan orders `left_anti` join se pakde.

**Q5. Incremental loading kya hai?**
Sirf nayi/badli hui rows process karna. Maine watermark (`last_order_id`) Delta table mein rakha, Bronze se `order_id > watermark` filter kiya, aur Silver mein `MERGE` (upsert) kiya -> idempotent.

**Q6. Bronze vs Silver vs Gold?**
- Bronze: raw data as-is + audit columns (`_ingest_ts`, `_source_file`)
- Silver: cleaned, typed, deduplicated, validated
- Gold: business-level aggregates / star schema, BI-ready

**Q7. SCD Type 2 kya hai?**
History preserve karna. Customer ki city badli toh purani row `is_current=false`, `effective_to` set; nayi row `is_current=true`. Delta `MERGE` + insert se kiya.

**Q8. Spark performance kaise optimize kiya?**
Delta `OPTIMIZE` + `ZORDER`, Bronze mein schema inference band (sab string, tez), sirf zaroori columns `select`, filter pehle join baad mein, chhoti tables par broadcast join, auto-terminate single-node cluster (cost).

**Q9. Pipeline failures kaise handle kiye?**
ADF Copy activity mein `retry: 2` + `retryIntervalInSeconds: 30` + timeout, ADF Monitor alerts, MERGE idempotent hone se re-run safe, bad data quarantine mein jaata hai pipeline fail nahi karta.

**Q10. Secrets kaise manage kiye?**
Databricks secret scope / Azure Key Vault; `.env` aur keys GitHub par commit nahi hote (`.gitignore`).

**Q11. Delta Lake kyun?**
ACID transactions, schema enforcement, time travel (`versionAsOf`), `MERGE`, `OPTIMIZE`.

**Q12. Partition kaise use kiya?**
ADF ne Bronze mein `load_date=YYYY-MM-DD` folders banaye (partition by ingestion date) taaki naya data alag mile.
