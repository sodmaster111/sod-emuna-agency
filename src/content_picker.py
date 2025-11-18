import json
import random
from pathlib import Path
from typing import Dict, List


LIBRARY_PATH = Path("data/library.json")


def load_library() -> List[Dict]:
    if not LIBRARY_PATH.exists():
        raise FileNotFoundError(
            "library.json missing. Create it from data/library.example.json inside data/."
        )
    with LIBRARY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def pick_content(slot: str, config: Dict, library: List[Dict]) -> Dict:
    allowed_types = config.get("slots", {}).get(slot)
    if not allowed_types:
        raise ValueError(f"Slot '{slot}' is not configured in slots.")

    filtered = [item for item in library if item.get("type") in allowed_types]
    if not filtered:
        raise ValueError(f"No content available for slot '{slot}' with types {allowed_types}.")

    return random.choice(filtered)
