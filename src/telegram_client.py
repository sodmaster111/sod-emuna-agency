import requests


API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_message(token: str, chat_id: str, title: str, text: str):
    url = API_URL.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": f"📿 *{title}*\n\n{text}",
        "parse_mode": "Markdown",
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()
