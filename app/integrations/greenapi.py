import os
import requests
from dotenv import load_dotenv

# Загружаем .env (на случай, если ещё не подхвачен)
load_dotenv()

GREEN_API_URL = os.getenv("GREEN_API_URL", "https://api.green-api.com")
GREEN_API_INSTANCE_ID = os.getenv("GREEN_API_INSTANCE_ID")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")


if not GREEN_API_INSTANCE_ID or not GREEN_API_TOKEN:
    raise RuntimeError("GREEN_API_INSTANCE_ID или GREEN_API_TOKEN не заданы в .env")


def _build_url(method_path: str) -> str:
    """
    method_path — строка вида '/sendMessage', '/getSettings' и т.д.
    """
    # По докам: POST {{apiUrl}}/waInstance{{idInstance}}/sendMessage/{{apiTokenInstance}}
    return f"{GREEN_API_URL}/waInstance{GREEN_API_INSTANCE_ID}{method_path}/{GREEN_API_TOKEN}"


def send_text_message(chat_id: str, text: str) -> dict:
    """
    Отправить текстовое сообщение в чат WhatsApp.
    chat_id — строка формата '79991234567@c.us'
    """
    url = _build_url("/sendMessage")
    payload = {
        "chatId": chat_id,
        "message": text,
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()
