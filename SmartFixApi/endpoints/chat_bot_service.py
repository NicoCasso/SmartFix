from fastapi import APIRouter
from schemas.chat_bot_data import ChatBotRequestData, ChatBotResponseData
from OllamaCore.sf_chat_bot import SfChatBot

router = APIRouter()
sf_chat_bot = SfChatBot()

@router.post("/ask", response_model = ChatBotResponseData) 
def ask_chatbot(request: ChatBotRequestData) -> ChatBotResponseData:
    history_casted = [{"role" :item.role, "content" : item.content} for item in request.history]
    sf_chat_bot.set_history(history_casted)

    answer_dict = sf_chat_bot.execute(request.question)
    answer_role = answer_dict["role"]
    answer_text = answer_dict["content"]

    response = ChatBotResponseData(answer=answer_text)

    return response