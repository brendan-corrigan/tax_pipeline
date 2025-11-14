import logging.config
from pathlib import Path

import yaml


def init_logging(config_path: str = "configs/logging.yaml"):
    "init logging from YAML config"
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Logging config not found: {config_path}")

    with config_file.open("r") as f:
        config = yaml.safe_load(f)

    for handler in config.get("handlers", {}).values():
        filename = handler.get("filename")
        if filename:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(config)
