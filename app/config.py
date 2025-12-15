import os
from pathlib import Path
from dotenv import load_dotenv

# Путь к корню проекта (папка, где лежит этот файл -> на уровень выше)
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем .env из корня проекта
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PROXYAPI_API_KEY = os.getenv("PROXYAPI_API_KEY")

# SQLite по умолчанию в файле ainova_assistant.db в корне
DB_URL = os.getenv("DB_URL", f"sqlite:///{BASE_DIR / 'ainova_assistant.db'}")
