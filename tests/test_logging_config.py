import pytest
import logging
from pathlib import Path
from csv_refine.logging_config import configure_logging


def test_configure_logging(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    configure_logging()

    logger = logging.getLogger("test_config")
    logger.info("include")
    logger.debug("exclude")

    for handler in logging.getLogger().handlers:
        handler.flush()

    log_file = tmp_path / "logs" / "app.log"
    result = log_file.read_text(encoding="utf-8")

    assert "include" in result
    assert "exclude" not in result
