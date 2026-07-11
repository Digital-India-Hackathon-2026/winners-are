from fastapi import APIRouter, Depends
from backend.modules.chatbot.schemas import ChatRequest, ChatResponse
from backend.modules.chatbot.service import ChatbotService, get_chatbot_service

router = APIRouter(prefix="/api/v1/chat", tags=["Chatbot"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    body: ChatRequest,
    service: ChatbotService = Depends(get_chatbot_service),
) -> ChatResponse:
    """
    Site-wide UPI / TrustLayer AI assistant.
    Accepts a user message + conversation history, returns a scoped AI reply.
    """
    reply = await service.chat(body.message, body.history)
    return ChatResponse(reply=reply)
