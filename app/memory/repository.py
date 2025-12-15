# app/memory/repository.py

from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.memory.db import SessionLocal
from app.memory.models import User, Message


def get_session() -> Session:
    """
    Получаем новую сессию к БД.
    Используем через контекстный менеджер: with get_session() as session: ...
    """
    return SessionLocal()


def get_or_create_user(telegram_id: int, username: Optional[str] = None) -> User:
    """
    Находим пользователя по telegram_id.
    Если его нет — создаём.
    """
    with get_session() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        user = session.execute(stmt).scalar_one_or_none()

        if user is None:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            session.commit()
            session.refresh(user)
        else:
            # Обновим username, если он изменился
            if username and user.username != username:
                user.username = username
                session.commit()

        return user


def add_message(user_id: int, role: str, content: str) -> None:
    """
    Сохраняем новое сообщение в БД.
    """
    with get_session() as session:
        msg = Message(user_id=user_id, role=role, content=content)
        session.add(msg)
        session.commit()


def get_last_messages(user_id: int, limit: int = 10) -> List[Message]:
    """
    Получаем последние N сообщений пользователя (user+assistant),
    отсортированные по времени по возрастанию (от старых к новым).
    """
    with get_session() as session:
        stmt = (
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        result = session.execute(stmt).scalars().all()

        # Мы забирали по убыванию, нужно развернуть обратно
        return list(reversed(result))
