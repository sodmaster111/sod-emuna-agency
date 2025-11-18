import argparse

from . import calendar_guard, config_loader, content_picker, telegram_client


def run(slot: str):
    config = config_loader.load_config()

    if calendar_guard.is_restricted_day(config):
        print("Restricted day (Shabbat/holiday). No message sent.")
        return

    library = content_picker.load_library()
    item = content_picker.pick_content(slot, config, library)

    telegram_client.send_message(
        token=config["telegram_token"],
        chat_id=config["telegram_chat_id"],
        title=item.get("title", ""),
        text=item.get("text", ""),
    )

    print(
        f"Sent: id={item.get('id')} | type={item.get('type')} | title={item.get('title')}"
    )


def main():
    parser = argparse.ArgumentParser(description="Emuna Agency telegram sender")
    parser.add_argument("slot", choices=["morning", "noon", "night"], help="Time slot")
    args = parser.parse_args()
    run(args.slot)


if __name__ == "__main__":
    main()
