import logging
import logging.config
import yaml
from pathlib import Path


def init_logger(logging_yaml_path: str = "config/config.yaml"):
    path = Path(logging_yaml_path)
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        logging.config.dictConfig(cfg)
    else:
        logging.basicConfig(level=logging.INFO)


def get_logger(name: str):
    return logging.getLogger(name)
