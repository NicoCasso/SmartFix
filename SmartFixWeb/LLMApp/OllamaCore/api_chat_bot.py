import json
import requests

FAST_API_URL = "http://127.0.0.1:8080/"

class SfApiChatBot():
    def __init__(self):
        self.api_url = f"{FAST_API_URL}/chatbot/ask"

    def call(self, message_list:list, user_message: str) -> str:
        request_data = {}
        history = []
        for message in message_list :
            history.append( { "role" : message["role"], "content": message["content"] } )

        request_data["history"] = history
        request_data["question"] = user_message

        response_data = requests.post(self.api_url, json= request_data)

        answer_text = response_data["answer"]
        return answer_text
