# app/llm_client.py

from typing import Dict, List, Optional

from openai import AsyncOpenAI

from app.config import PROXYAPI_API_KEY

DEFAULT_MODEL_NAME = "gpt-4o-mini"

DEFAULT_SYSTEM_PROMPT = (
    "Ты умный, доброжелательный AI-ассистент студии AINOVA. "
    "Отвечаешь по-делу, простым языком, иногда даёшь короткие советы бизнесу. "
    "Если вопрос не по теме, отвечай кратко и дружелюбно."
)

_client: Optional[AsyncOpenAI] = None


def get_client() -> AsyncOpenAI:
    """
    Лениво создаём клиента. Это важно, чтобы приложение не падало при импорте модулей,
    если ключ не задан (например, в среде без .env).
    """
    global _client

    if _client is not None:
        return _client

    if not PROXYAPI_API_KEY:
        # Не валим импорт всего приложения — валим только конкретный запрос.
        raise RuntimeError("PROXYAPI_API_KEY не найден. Заполни его в .env")

    _client = AsyncOpenAI(
        api_key=PROXYAPI_API_KEY,
        base_url="https://openai.api.proxyapi.ru/v1",
    )
    return _client


async def ask_llm(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL_NAME,
    temperature: float = 0.7,
) -> str:
    """
    Универсальная функция для запроса к LLM через ProxyAPI.
    messages — список:
    [{"role": "system" | "user" | "assistant", "content": "..."}, ...]
    """
    try:
        client = get_client()
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=False,
        )

        content = response.choices[0].message.content
        return content or ""
    except Exception as e:
        # Временно логируем ошибку в консоль
        print("Ошибка при запросе к LLM через ProxyAPI:", repr(e))
        return "Что-то пошло не так при запросе к AI. Попробуй ещё раз позже 🙏"
