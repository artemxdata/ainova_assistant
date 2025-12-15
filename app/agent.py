# app/agent.py

from typing import List, Optional, Union

from app.config import ENABLE_RAG, HISTORY_LIMIT, RAG_TOP_K, RAG_MAX_CHARS
from app.llm_client import ask_llm
from app.memory.repository import get_or_create_user, get_last_messages, add_message
from app.prompts import load_system_prompt, load_developer_prompt
from app.rag.retriever import retrieve_documents


def build_rag_block(docs) -> str:
    if not docs:
        return ""

    parts = []
    for i, doc in enumerate(docs, start=1):
        title = (doc.title or "Документ").strip()
        content = (doc.content or "").strip()
        parts.append(f"[Источник {i}] {title}\n{content}")

    block = "\n\n---\n\n".join(parts)

    # ограничим размер, чтобы не раздувать контекст
    if len(block) > RAG_MAX_CHARS:
        block = block[:RAG_MAX_CHARS].rstrip() + "\n\n[...контекст обрезан...]"

    return block


async def run_ainova_agent(
    user_external_id: Union[int, str],
    username: Optional[str],
    user_text: str,
    client_id: str = "default",
    channel: str = "web",
) -> str:
    # 1) пользователь/память
    user = get_or_create_user(
        telegram_id=str(user_external_id),
        username=username,
    )

    # 2) история
    history_messages = get_last_messages(user_id=user.id, limit=HISTORY_LIMIT)

    # 3) промпты
    system_prompt = load_system_prompt()
    developer_prompt = load_developer_prompt()

    # 4) messages
    messages: List[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": developer_prompt},
        {
            "role": "system",
            "content": f"Технические метаданные (не упоминай пользователю): client_id={client_id}, channel={channel}.",
        },
    ]

    for msg in history_messages:
        messages.append({"role": msg.role, "content": msg.content})

    # 5) RAG
    if ENABLE_RAG:
        rag_docs = retrieve_documents(user_text, top_k=RAG_TOP_K)
        rag_block = build_rag_block(rag_docs)
        if rag_block:
            messages.append({
                "role": "system",
                "content": (
                    "Ниже справочная информация из базы знаний. Используй её как опору для фактов. "
                    "Если в базе нет ответа — уточни или предложи следующий шаг.\n\n"
                    f"{rag_block}"
                ),
            })

    # 6) user message
    messages.append({"role": "user", "content": user_text})

    # 7) LLM
    answer = await ask_llm(messages)

    # 8) save memory
    add_message(user_id=user.id, role="user", content=user_text)
    add_message(user_id=user.id, role="assistant", content=answer)

    return answer
