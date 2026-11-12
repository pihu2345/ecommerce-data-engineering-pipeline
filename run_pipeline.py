
import subprocess
import sys
import time
from pathlib import Path

from extraction.logger import logger

BASE_DIR = Path(__file__).resolve().parent
scripts = [
    "extraction/generate_data.py",
    "extraction/clean_customers.py",
    "extraction/clean_products.py",
    "extraction/clean_orders.py",
    "extraction/clean_sales.py",
    "extraction/clean_payments.py",
    "extraction/clean_references.py",
    "extraction/validate_silver.py",
    "extraction/build_gold.py",
    "extraction/validate_gold.py",
    "extraction/data_quality_tests.py",
    "sql/load_warehouse.py"
]
pipeline_start = time.time()

print("=" * 60)
print("       E-COMMERCE DATA ENGINEERING PIPELINE")
print("=" * 60)

logger.info("E-commerce pipeline started")

try:
    for script in scripts:
        print(f"\nRunning: {script}")

        logger.info(f"Started: {script}")
        step_start = time.time()

        try:
            subprocess.run(
                [sys.executable, str(BASE_DIR / script)],
                cwd=BASE_DIR,
                check=True
            )

            step_time = time.time() - step_start

            print(f"SUCCESS: {script}")
            logger.info(
                f"SUCCESS: {script} | Time: {step_time:.2f} seconds"
            )

        except subprocess.CalledProcessError:
            logger.exception(f"FAILED: {script}")
            print(f"FAILED: {script}")
            raise

    total_time = time.time() - pipeline_start

    print("\n" + "=" * 60)
    print("       COMPLETE PIPELINE EXECUTED SUCCESSFULLY!")
    print(f"       Total Time: {total_time:.2f} seconds")
    print("=" * 60)

    logger.info(
        f"Pipeline completed successfully | Total time: {total_time:.2f} seconds"
    )

except Exception:
    logger.exception("PIPELINE FAILED")
    print("\nPIPELINE FAILED! Check logs/pipeline.log")
    sys.exit(1)
