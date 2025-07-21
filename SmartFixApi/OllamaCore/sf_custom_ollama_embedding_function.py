import chromadb
from chromadb.utils import embedding_functions
import httpx

# Créez une fonction d'intégration personnalisée qui utilise ce client
class SfCustomOllamaEmbeddingFunction(embedding_functions.OllamaEmbeddingFunction):
    def __init__(self, url:str, model_name:str, client : httpx.Client):
        super().__init__(url, model_name, timeout = client.timeout)
        self.client = client

    def __call__(self, input):
        # Utilisez le client configuré pour effectuer la requête
        response = self.client.post(self.url, json={"input": input})
        response.raise_for_status()
        return response.json()["embeddings"]