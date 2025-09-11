import importlib
import logging
from pathlib import Path

import helpers


def test_logger_delayed_file_creation(tmp_path, monkeypatch):
    logger = logging.getLogger("bilagskontroll")
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    monkeypatch.chdir(tmp_path)
    module = importlib.reload(helpers)

    log_file = Path(tmp_path) / "logs" / "bilagskontroll.log"
    assert not log_file.exists()

    module.logger.info("første melding")
    assert log_file.exists()
    assert "første melding" in log_file.read_text(encoding="utf-8")
