import json
import requests

FAST_API_URL = "http://127.0.0.1:8080"

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

        response = requests.post(self.api_url, json= request_data)

        if response.status_code == 200 :
            response_data = response.json()
            answer_text = response_data["answer"]
        else : 
            answer_text = f"HTTP error {response.status_code}"
        
        return answer_text
    
if __name__ == "__main__" :
    api_info_url = f"{FAST_API_URL}/openapi.json"
    response = requests.get(api_info_url)
    schema = response.json()

    searched_path = "/chatbot/ask" 

    if searched_path in schema.get("paths", {}):
        endpoint = schema["paths"][searched_path].get("post", {})
        
        # Extraire les paramètres
        parameters = endpoint.get("parameters", [])
        request_body = endpoint.get("requestBody", {})
        
        print( f"parameters:{parameters}")
        print( f"request_body: {request_body}")
        print( f"responses: {endpoint.get("responses", {})}")
        print( f"summary: {endpoint.get("summary", "")}")
        print( f"description: {endpoint.get("description", "")}")
    

