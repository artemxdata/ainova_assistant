# app/memory/debug_db.py

from textwrap import shorten

from app.memory.db import SessionLocal
from app.memory.models import User, Message, Document


def print_users(session):
    print("\n=== USERS ===")
    users = session.query(User).all()
    if not users:
        print("Нет пользователей")
        return
    for u in users:
        print(f"[id={u.id}] tg_id={u.telegram_id}, username={u.username}, created_at={u.created_at}")


def print_messages(session, limit_per_user: int = 5):
    print("\n=== MESSAGES (по пользователям, последние) ===")
    users = session.query(User).all()
    if not users:
        print("Нет пользователей -> нет сообщений")
        return

    for u in users:
        print(f"\n--- Диалог с пользователем id={u.id} (tg_id={u.telegram_id}) ---")
        msgs = (
            session.query(Message)
            .filter(Message.user_id == u.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        if not msgs:
            print("  Сообщений нет")
            continue

        # Покажем не больше limit_per_user
        for msg in msgs[-limit_per_user:]:
            snippet = shorten(msg.content.replace("\n", " "), width=80, placeholder="...")
            print(f"  [{msg.created_at}] {msg.role:9} | {snippet}")


def print_documents(session, limit: int = 5):
    print("\n=== DOCUMENTS (RAG) ===")
    docs = session.query(Document).all()
    if not docs:
        print("Нет документов в базе")
        return

    for doc in docs[:limit]:
        snippet = shorten(doc.content.replace("\n", " "), width=100, placeholder="...")
        print(f"[id={doc.id}] title={doc.title}, created_at={doc.created_at}")
        print(f"  content: {snippet}")
        print(f"  embedding length: приблизительно {len(doc.embedding)} символов (JSON-строка)")
        print()


def main():
    with SessionLocal() as session:
        print_users(session)
        print_messages(session, limit_per_user=10)
        print_documents(session, limit=10)


if __name__ == "__main__":
    main()
