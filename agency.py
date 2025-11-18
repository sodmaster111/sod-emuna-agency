import json
import random
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = BASE_DIR / "config.json"
LIB_PATH = BASE_DIR / "library.json"

def load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_library():
    with LIB_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def is_restricted_day(cfg):
    """לא שולחים בשבת ובחגים המוגדרים."""
    tz = ZoneInfo(cfg.get("timezone", "Asia/Jerusalem"))
    now = datetime.now(tz)
    # שבת (Saturday) – weekday() == 5
    if now.weekday() == 5:
        return True
    today_str = now.date().isoformat()
    holidays = cfg.get("holidays", [])
    if today_str in holidays:
        return True
    return False

def pick_content(slot, cfg, library):
    slot_types = cfg.get("slots", {}).get(slot)
    if not slot_types:
        # ברירת מחדל – כל הספרייה
        items = library
    else:
        items = [item for item in library if item["type"] in slot_types]
    if not items:
        return None
    return random.choice(items)

def send_to_telegram(cfg, title, text):
    token = cfg["telegram_token"]
    chat_id = cfg["telegram_chat_id"]
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    full_text = f"📿 *{title}*\n\n{text}"

    resp = requests.post(api_url, json={
        "chat_id": chat_id,
        "text": full_text,
        "parse_mode": "Markdown"
    })
    if not resp.ok:
        print("שגיאה בשליחה לטלגרם:", resp.status_code, resp.text)
    else:
        print("נשלח בהצלחה לטלגרם.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 agency.py <slot>")
        print("slots: morning | noon | night")
        sys.exit(1)

    slot = sys.argv[1]
    cfg = load_config()

    if is_restricted_day(cfg):
        print("שבת או חג – לא שולחים הודעות היום.")
        return

    library = load_library()
    item = pick_content(slot, cfg, library)

    if not item:
        print("לא נמצא תוכן מתאים לסלוט:", slot)
        return

    print(f"נבחר פריט: {item['id']} ({item['type']})")
    send_to_telegram(cfg, item["title"], item["text"])

if __name__ == "__main__":
    main()
