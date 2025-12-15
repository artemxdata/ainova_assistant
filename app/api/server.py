# app/api/server.py

from typing import Optional, Union

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent import run_ainova_agent

# Если WhatsApp/GreenAPI пока не нужен — импорт можно оставить,
# но эндпоинт ты можешь не использовать.
from app.integrations.greenapi import send_text_message


app = FastAPI(
    title="AINOVA Agent API",
    description="Единый мозг ассистента AINOVA, доступный по HTTP.",
    version="0.2.0",
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

    # Мягкая подготовка к multi-tenant и каналам:
    # старые клиенты это поле не отправляют — им не мешает.
    client_id: Optional[str] = None
    channel: Optional[str] = None  # "web" | "telegram" | "whatsapp" | ...


class AgentResponse(BaseModel):
    answer: str


def normalize_user_id(raw_id: Union[int, str]) -> int:
    """
    Преобразуем любой user_id (строка или число) в стабильное целое число.
    Нужно, чтобы один и тот же пользователь имел свою память независимо от канала.
    """
    if isinstance(raw_id, int):
        return raw_id
    return abs(hash(raw_id)) % (10**9)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/agent", response_model=AgentResponse)
async def agent_endpoint(payload: AgentRequest):
    """
    Единая точка входа в AINOVA Agent для всех каналов.

    На вход: user_id, username, message (+ опционально client_id, channel).
    На выход: answer.
    """
    ext_id = normalize_user_id(payload.user_id)

    answer = await run_ainova_agent(
        user_external_id=ext_id,
        username=payload.username,
        user_text=payload.message,
        client_id=payload.client_id or "default",
        channel=payload.channel or "web",
    )

    return AgentResponse(answer=answer)


@app.post("/webhooks/greenapi")
async def greenapi_webhook(request: Request):
    """
    Вебхук для уведомлений от Green API.
    Сейчас WhatsApp отключён — этот эндпоинт можно не трогать.
    """
    payload = await request.json()

    type_webhook = payload.get("typeWebhook")
    if type_webhook != "incomingMessageReceived":
        return {"status": "ignored", "type": type_webhook}

    sender_data = payload.get("senderData", {}) or {}
    message_data = payload.get("messageData", {}) or {}

    chat_id = sender_data.get("chatId")
    username = sender_data.get("senderName") or sender_data.get("chatName") or "whatsapp_user"

    text_message_data = message_data.get("textMessageData") or {}
    user_text = text_message_data.get("textMessage")

    if not chat_id or not user_text:
        return {"status": "no_text_or_chat", "chat_id": chat_id, "user_text": user_text}

    user_external_id = f"wa:{chat_id}"

    answer = await run_ainova_agent(
        user_external_id=user_external_id,
        username=username,
        user_text=user_text,
        client_id="default",
        channel="whatsapp",
    )

    try:
        send_text_message(chat_id, answer)
    except Exception as e:
        return {"status": "error_send", "detail": str(e)}

    return {"status": "ok", "answer": answer}
