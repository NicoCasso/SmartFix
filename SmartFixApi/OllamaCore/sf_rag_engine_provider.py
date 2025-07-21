from sf_rag_engine import SfRagEngine

class SfRagEngineProvider:
    _instance = None
    
    def __init__(self):
        if not hasattr(self, 'rag_engine'):  # Évite la réinitialisation
            self.rag_engine = SfRagEngine()
    
    @classmethod
    def get_instance(cls) -> SfRagEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance.rag_engine
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance