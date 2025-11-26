import logging
from .config import (ARTIFACT_PATH,LOGGING_FILE)
import os

logging_path = os.path.join(ARTIFACT_PATH,LOGGING_FILE)
os.makedirs(os.path.dirname(logging_path),exist_ok=True)
logging.basicConfig(
    filename=logging_path,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
    )





