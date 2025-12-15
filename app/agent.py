# app/agent.py

from typing import List, Optional

from app.llm_client import ask_llm, DEFAULT_SYSTEM_PROMPT
from app.memory.repository import (
    get_or_create_user,
    get_last_messages,
    add_message,
)
from app.rag.retriever import retrieve_documents


async def run_ainova_agent(
    user_external_id: int,
    username: Optional[str],
    user_text: str,
) -> str:
    """
    Единый вход в "мозг" ассистента AINOVA.

    На вход:
      - user_external_id: любой внешний ID пользователя (телега, сайт, ватсап и т.д.)
      - username: имя/логин, если есть
      - user_text: текст сообщения

    На выход:
      - текст ответа от LLM с учётом памяти и RAG.
    """

    # 1. Находим или создаём пользователя в нашей БД
    # (поле telegram_id по сути выполняет роль external_id — потом переименуем, если захочешь)
    user = get_or_create_user(
        telegram_id=user_external_id,
        username=username,
    )

    # 2. Загружаем историю диалога
    history_messages = get_last_messages(user_id=user.id, limit=12)

    # 3. Собираем базовый список messages
    messages: List[dict] = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
    for msg in history_messages:
        messages.append({"role": msg.role, "content": msg.content})

    # 4. RAG — ищем документы по запросу пользователя
    rag_docs = retrieve_documents(user_text, top_k=2)

    if rag_docs:
        context_parts = []
        for doc in rag_docs:
            context_parts.append(f"{doc.title}:\n{doc.content}")

        rag_context = "\n\n---\n\n".join(context_parts)

        messages.append({
            "role": "system",
            "content": (
                "Вот релевантная информация из базы знаний AINOVA. "
                "Используй её при ответе, опирайся на факты, "
                "но не говори, что ты читаешь документы:\n\n"
                f"{rag_context}"
            ),
        })

    # 5. Добавляем текущее сообщение пользователя
    messages.append({"role": "user", "content": user_text})

    # 6. Запрос к LLM
    answer = await ask_llm(messages)

    # 7. Сохраняем новые сообщения в БД
    add_message(user_id=user.id, role="user", content=user_text)
    add_message(user_id=user.id, role="assistant", content=answer)

    return answer
