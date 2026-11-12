
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_FOLDER = BASE_DIR / "logs"
LOG_FOLDER.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_FOLDER / "pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ecommerce_pipeline")
