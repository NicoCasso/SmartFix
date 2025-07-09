from fastapi import FastAPI
from endpoints import chat_bot_service

app = FastAPI(
    title = "SmartFix Service") 

app.include_router(chat_bot_service.router, prefix="/chatbot")


