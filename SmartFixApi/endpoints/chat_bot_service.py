from fastapi import APIRouter
from schemas.chat_bot_data import ChatBotRequest, ChatBotResponse

router = APIRouter()

@router.post("/ask", response_model = ChatBotResponse) 
def ask_chatbot(data: dict) -> ChatBotResponse:
    return {"message": "Données reçues", "data": data}