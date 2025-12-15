# app/api/server.py

from fastapi import Request
from app.integrations.greenapi import send_text_message

from typing import Optional, Union
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import run_ainova_agent

app = FastAPI(
    title="AINOVA Agent API",
    description="Единый мозг ассистента AINOVA, доступный по HTTP.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # на учебном этапе можно всем
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    user_id: Union[int, str]
    username: Optional[str] = None
    message: str


class AgentResponse(BaseModel):
    answer: str


def normalize_user_id(raw_id: Union[int, str]) -> int:
    """
    Преобразуем любой user_id (строка или число) в стабильное целое число.
    Это нужно, чтобы один и тот же пользователь (по user_id)
    имел свою память, даже если приходит с разных источников.
    """
    if isinstance(raw_id, int):
        return raw_id
    # если строка — хэшируем и берём по модулю
    return abs(hash(raw_id)) % (10**9)


@app.post("/agent", response_model=AgentResponse)
async def agent_endpoint(payload: AgentRequest):
    """
    Единая точка входа в AINOVA Agent для всех каналов:
    - Telegram
    - WhatsApp
    - Web-чат (сайт)
    - n8n и т.д.

    На вход: user_id, username, message.
    На выход: answer.
    """
    ext_id = normalize_user_id(payload.user_id)

    answer = await run_ainova_agent(
        user_external_id=ext_id,
        username=payload.username,
        user_text=payload.message,
    )

    return AgentResponse(answer=answer)

@app.post("/webhooks/greenapi")
async def greenapi_webhook(request: Request):
    """
    Вебхук для уведомлений от Green API.
    Берём входящее сообщение, прогоняем через AINOVA-агента, отправляем ответ в WhatsApp.
    """
    payload = await request.json()

    # Тип вебхука (нас интересуют входящие сообщения)
    type_webhook = payload.get("typeWebhook")
    if type_webhook != "incomingMessageReceived":
        # Игнорируем всё, что не входящее сообщение
        return {"status": "ignored", "type": type_webhook}

    sender_data = payload.get("senderData", {}) or {}
    message_data = payload.get("messageData", {}) or {}

    chat_id = sender_data.get("chatId")  # вида '79991234567@c.us'
    username = sender_data.get("senderName") or sender_data.get("chatName") or "whatsapp_user"

    # Вытаскиваем текст из текстового сообщения
    text_message_data = message_data.get("textMessageData") or {}
    user_text = text_message_data.get("textMessage")

    if not chat_id or not user_text:
        return {"status": "no_text_or_chat", "chat_id": chat_id, "user_text": user_text}

    # Связываем WhatsApp-пользователя с нашим user_id
    # Можно просто использовать chat_id как внешний ID
    user_external_id = f"wa:{chat_id}"

    # Вызываем наш мозг
    answer = await run_ainova_agent(
        user_external_id=user_external_id,
        username=username,
        user_text=user_text,
    )

    # Отправляем ответ назад в WhatsApp
    try:
        send_text_message(chat_id, answer)
    except Exception as e:
        # Просто логируем в ответ, чтобы видеть в /docs или логах
        return {"status": "error_send", "detail": str(e)}

    return {"status": "ok", "answer": answer}

