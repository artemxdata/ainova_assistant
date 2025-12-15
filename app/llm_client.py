# app/llm_client.py

from typing import List, Dict
from openai import AsyncOpenAI

from app.config import PROXYAPI_API_KEY

if not PROXYAPI_API_KEY:
    raise RuntimeError("PROXYAPI_API_KEY не найден. Заполни его в .env")

# Клиент ProxyAPI (OpenAI-совместимый эндпоинт)
# Документацию по моделям и ценам смотри у ProxyAPI.
client = AsyncOpenAI(
    api_key=PROXYAPI_API_KEY,
    base_url="https://openai.api.proxyapi.ru/v1",
)

# По умолчанию можно использовать gpt-4o-mini, потом поменяем при желании
DEFAULT_MODEL_NAME = "gpt-4o-mini"

DEFAULT_SYSTEM_PROMPT = (
    "Ты умный, доброжелательный AI-ассистент студии AINOVA. "
    "Отвечаешь по-делу, простым языком, иногда даёшь короткие советы бизнесу. "
    "Если вопрос не по теме, отвечай кратко и дружелюбно."
)


async def ask_llm(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL_NAME,
    temperature: float = 0.7,
) -> str:
    """
    Универсальная функция для запроса к LLM через ProxyAPI.
    messages — список словарей формата:
    [{"role": "system" | "user" | "assistant", "content": "..."}, ...]
    """
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        # Временно логируем ошибку в консоль
        print("Ошибка при запросе к LLM через ProxyAPI:", repr(e))
        return "Что-то пошло не так при запросе к AI. Попробуй ещё раз позже 🙏"
