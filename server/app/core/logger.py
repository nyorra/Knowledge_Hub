"""
Centralized logging configuration for the entire application.
All modules import logger from here.
"""

import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        # Console handler
        logging.StreamHandler(sys.stdout),
        # File handler
        logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
    ],
)

# Create application logger
logger = logging.getLogger("knowledge_hub")
logger.setLevel(logging.INFO)

# Suppress noisy third-party loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
