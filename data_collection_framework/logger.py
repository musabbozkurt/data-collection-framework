"""Central logging setup: console + rotating file. Replaces the former per-call MongoDB logger."""
import logging
from logging.handlers import RotatingFileHandler

_ROOT = "data_collection_framework"
_configured = False


def get_logger(name: str = _ROOT) -> logging.Logger:
    global _configured
    if not _configured:
        root = logging.getLogger(_ROOT)
        root.setLevel(logging.DEBUG)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
        file_handler = RotatingFileHandler("pypro.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
        root.addHandler(console)
        root.addHandler(file_handler)
        _configured = True
    return logging.getLogger(name if name.startswith(_ROOT) else f"{_ROOT}.{name}")
