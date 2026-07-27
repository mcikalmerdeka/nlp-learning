"""Centralized logging configuration for the turboquant-experiment app."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Project root is the directory containing this file.
PROJECT_ROOT = Path(__file__).parent.resolve()

# Default log file location - logs/app.log in project root
DEFAULT_LOG_FILE = PROJECT_ROOT / "logs" / "app.log"


def setup_logger(
    name: str = "turboquant_experiment",
    log_file: str | Path | bool | None = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """Setup centralized logging for the application.

    This configures a named logger that child loggers will inherit from.
    Child loggers like 'turboquant_experiment.app.search' automatically use
    the handlers configured on this logger.

    Args:
        name: Logger name (default: "turboquant_experiment").
        log_file: Optional log file path. If None, uses DEFAULT_LOG_FILE.
            Set to False to disable file logging.
        level: Logging level for the logger and console handler
            (default: logging.INFO).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates when reinitializing.
    logger.handlers.clear()

    # Console handler - output to terminal with simple format.
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler - save to logs/app.log with detailed format.
    if log_file is not False:
        log_path = Path(log_file) if log_file else DEFAULT_LOG_FILE
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Don't propagate to the root logger to avoid duplicate messages.
    logger.propagate = False

    return logger
