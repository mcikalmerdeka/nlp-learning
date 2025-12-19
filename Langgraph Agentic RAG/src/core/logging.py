"""Logging configuration for the RAG application."""

import logging
import sys

# Create logger
logger = logging.getLogger("rag")


def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logger.setLevel(getattr(logging, level.upper()))
    
    # Only add handler if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%H:%M:%S"
            )
        )
        logger.addHandler(handler)


# Auto-setup with INFO level (can be overridden)
setup_logging()

