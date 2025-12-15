# app/memory/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DB_URL

# Создаём движок (подключение к БД)
# Для SQLite это будет файл, путь к которому задан в DB_URL
engine = create_engine(
    DB_URL,
    echo=False,      # можно поставить True, если хочешь видеть SQL в консоли
    future=True,
)

# Фабрика сессий — через неё будем общаться с БД
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

# Базовый класс для моделей (таблиц)
Base = declarative_base()

# app/memory/db.py

def migrate_db():
    """
    Создаём новые таблицы или обновляем существующие.
    """
    Base.metadata.create_all(bind=engine)
