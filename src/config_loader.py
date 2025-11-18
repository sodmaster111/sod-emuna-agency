import json
from pathlib import Path


CONFIG_FILENAMES = ["config.json", "config/config.json"]


def load_config():
    for name in CONFIG_FILENAMES:
        path = Path(name)
        if path.exists():
            with path.open(encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(
        "config.json missing. Create it from config/config.example.json in the project root or config/."
    )
