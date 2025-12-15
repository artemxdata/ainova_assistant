# app/agent.py

from typing import List, Optional, Union

from app.llm_client import ask_llm, DEFAULT_SYSTEM_PROMPT
from app.memory.repository import get_or_create_user, get_last_messages, add_message
from app.rag.retriever import retrieve_documents


def build_rag_block(docs) -> str:
    """
    Формируем аккуратный блок контекста для модели.
    Важно: делаем структуру, чтобы меньше галлюцинаций и проще дебажить.
    """
    if not docs:
        return ""

    parts = []
    for i, doc in enumerate(docs, start=1):
        title = (doc.title or "Документ").strip()
        content = (doc.content or "").strip()
        parts.append(f"[Источник {i}] {title}\n{content}")

    return "\n\n---\n\n".join(parts)


async def run_ainova_agent(
    user_external_id: Union[int, str],
    username: Optional[str],
    user_text: str,
    client_id: str = "default",
    channel: str = "web",
) -> str:
    """
    Единый вход в "мозг" ассистента AINOVA.

    На вход:
      - user_external_id: внешний ID пользователя (web/tg/wa и т.д.)
      - username: имя/логин, если есть
      - user_text: текст сообщения
      - client_id: мягкая заготовка под multi-tenant (пока default)
      - channel: источник (web/telegram/whatsapp)

    На выход:
      - текст ответа LLM с учётом памяти и RAG.
    """

    # 1) Пользователь/память
    # (Да, поле telegram_id пока историческое — позже переименуем в external_id)
    user = get_or_create_user(
        telegram_id=str(user_external_id),
        username=username,
    )

    # 2) История (лимит оставим 12 как у тебя, это ок)
    history_messages = get_last_messages(user_id=user.id, limit=12)

    # 3) Собираем messages для LLM
    messages: List[dict] = [
        {
            "role": "system",
            "content": DEFAULT_SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": (
                f"Технические метаданные (не упоминай пользователю): "
                f"client_id={client_id}, channel={channel}."
            ),
        },
    ]

    for msg in history_messages:
        messages.append({"role": msg.role, "content": msg.content})

    # 4) RAG retrieval (top_k можно потом вынести в config)
    rag_docs = retrieve_documents(user_text, top_k=2)

    rag_block = build_rag_block(rag_docs)
    if rag_block:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Ниже справочная информация из базы знаний. "
                    "Используй её как опору для фактов. "
                    "Если в базе нет ответа — отвечай по общим знаниям или уточняй. "
                    "Не говори, что ты читаешь документы.\n\n"
                    f"{rag_block}"
                ),
            }
        )

    # 5) Сообщение пользователя
    messages.append({"role": "user", "content": user_text})

    # 6) LLM
    answer = await ask_llm(messages)

    # 7) Сохранение в память
    add_message(user_id=user.id, role="user", content=user_text)
    add_message(user_id=user.id, role="assistant", content=answer)

    return answer
