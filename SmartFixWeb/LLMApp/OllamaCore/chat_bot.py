import json
import requests
from .llama_strings import LLamaStrings as llst

class SfChatBot():
    def __init__(self) :
        # L'URL de l'API d'Ollama pour la fonctionnalité de chat.
        # Notez que nous utilisons "/api/chat" au lieu de "/api/generate".
        self.url = "http://localhost:11434/api/chat"
        self.memory_enabled=True
        self.history= []
           
    def set_history(self, message_list:list):
        # L'historique de la conversation.
        # C'est une liste de dictionnaires. Chaque dictionnaire représente un message.
        # Le "role" peut être "system", "user", ou "assistant".
        # - system: Donne des instructions générales au modèle.
        # - user: Le message de l'utilisateur.
        # - assistant: La réponse du modèle.
        self.history = message_list

    def _invoke(self, messages):
        """
        Fonction pour envoyer une liste de messages au LLM et obtenir une réponse.
        """
        data = {
            "model": "llama3.2:3b",
            "messages": messages,
            "stream": False,  # On reçoit la réponse en une seule fois.
        }

        # Envoi de la requête POST avec l'historique des messages.
        response = requests.post(self.url, json=data)

        # Vérification de la réponse.
        if response.status_code == 200:
            response_data = json.loads(response.text)
            # La réponse de l'API de chat est un objet JSON contenant un champ "message".
            # Ce champ "message" est un dictionnaire avec "role" et "content".
            return response_data.get("message")
        else:
            exception = Exception(f"Erreur SfChatBot {response.status_code} => {response.text}")
            raise exception

    def execute(self, user_message:str) :    
        self.history.append({
            llst.KEY.ROLE: llst.ROLEVALUE.USER, 
            llst.KEY.CONTENT: user_message})
        
        messages_to_send = self.history
    
        assistant_response = self._invoke(messages_to_send)
        return assistant_response