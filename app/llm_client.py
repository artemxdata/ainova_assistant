# app/llm_client.py

from typing import Dict, List, Optional

from openai import AsyncOpenAI

from app.config import (
    PROXYAPI_API_KEY,
    PROXYAPI_BASE_URL,
    LLM_MODEL,
    LLM_TEMPERATURE,
)

_client: Optional[AsyncOpenAI] = None


def get_client() -> AsyncOpenAI:
    """
    Лениво создаём клиента (не падаем при импорте).
    """
    global _client
    if _client is not None:
        return _client

    if not PROXYAPI_API_KEY:
        raise RuntimeError("PROXYAPI_API_KEY не найден. Заполни его в .env")

    _client = AsyncOpenAI(
        api_key=PROXYAPI_API_KEY,
        base_url=PROXYAPI_BASE_URL,
    )
    return _client


async def ask_llm(messages: List[Dict[str, str]]) -> str:
    """
    Запрос к LLM через ProxyAPI (OpenAI-compatible).
    Настройки модели/температуры берём из config.
    """
    try:
        client = get_client()
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=LLM_TEMPERATURE,
            stream=False,
        )
        content = response.choices[0].message.content
        return content or ""
    except Exception as e:
        print("Ошибка при запросе к LLM через ProxyAPI:", repr(e))
        return "Что-то пошло не так при запросе к AI. Попробуй ещё раз позже 🙏"
