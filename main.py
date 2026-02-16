"""
Entry point for the FastAPI application.

This script initializes the logging system, loads environment variables,
and starts the uvicorn server for the backend application.
"""
import logging
import os
import warnings

import uvicorn
from dotenv import load_dotenv

warnings.filterwarnings("ignore")

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s — %(name)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Initializing data, this may take a few seconds...")
    logger.info("Initialization complete, starting server...")

    logger.info("Running in production mode")
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        root_path=os.environ.get("BASE_PATH", "/"),
        reload=False,
        workers=1,
        log_level="debug",
    )
