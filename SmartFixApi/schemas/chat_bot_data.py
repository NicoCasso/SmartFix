from pydantic import BaseModel, Field

class HistoryItemData(BaseModel):
    role : str
    content: str

class ChatBotRequestData(BaseModel):
    history : list[HistoryItemData]
    question : str

class ChatBotResponseData(BaseModel):
    answer : str

