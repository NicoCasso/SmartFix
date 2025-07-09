from fastapi import APIRouter
from schemas.chat_bot_data import ChatBotRequestData, ChatBotResponseData
from OllamaCore.sf_chat_bot import SfChatBot

router = APIRouter()
sf_chat_bot = SfChatBot()

@router.post("/ask", response_model = ChatBotResponseData) 
def ask_chatbot(request: ChatBotRequestData) -> ChatBotResponseData:
    sf_chat_bot.set_history(request.history)
    answer_text = sf_chat_bot.execute(request.question)

    response = ChatBotResponseData(answer=answer_text)

    return response