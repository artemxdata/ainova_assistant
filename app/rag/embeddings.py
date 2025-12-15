# app/rag/embeddings.py

from openai import OpenAI
from app.config import PROXYAPI_API_KEY

if not PROXYAPI_API_KEY:
    raise RuntimeError("PROXYAPI_API_KEY не найден в .env")

# Клиент для ProxyAPI (OpenAI-совместимый)
client = OpenAI(
    api_key=PROXYAPI_API_KEY,
    base_url="https://openai.api.proxyapi.ru/v1",
)

def get_embedding(text: str) -> list:
    """
    Получаем эмбеддинг текста через ProxyAPI / OpenAI.
    Используем современный метод embeddings.create().
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",  # современная быстрая модель
        input=text
    )
    return response.data[0].embedding
