"""Chat router — WhatsApp NLP simulation endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services import chat_service

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    store_id: Optional[str] = "S001"


@router.post("")
async def chat(request: ChatRequest):
    """Process a chat message and return AI response."""
    result = chat_service.generate_response(request.message, request.store_id)
    return result


@router.post("/classify")
async def classify_intent(request: ChatRequest):
    """Classify the intent of a message (debug endpoint)."""
    result = chat_service.classify_intent(request.message)
    return result
