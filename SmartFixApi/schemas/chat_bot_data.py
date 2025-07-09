from pydantic import BaseModel, Field

class ChatBotRequest(BaseModel):
    history : list[dict]
    question : str

class ChatBotResponse(BaseModel):
    answer : str

