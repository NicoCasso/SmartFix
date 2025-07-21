import os
import sys
from typing import TypedDict, List
from pathlib import Path
import httpx

import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader

from langgraph.graph import StateGraph, END
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RAGState(TypedDict):
    question: str
    context: List[str]
    answer: str

os.environ["CHROMA_ENABLE_TELEMETRY"] = "false"

class SfRagEngine :
    def __init__(self, force_initialization=False):
        if force_initialization :
            self.__chroma_initialized = False
        else : 
            self.__chroma_initialized = True

        self.file_pathes = []
        current_path = Path(os.getcwd())
        documents_path = current_path.parent / "DATA" / "Documents"
        print("chargement des documents présents dans {documents_path}")
        for element in documents_path.iterdir():
            if element.is_file():
                self.file_pathes.append(element)

        # for file_path in self.file_pathes :
        #     print(file_path)

        self.collection_name = "smartfix_collection"
        self.embedding_model = "mxbai-embed-large"
        self.llm_model = "llama3.2:3b"

        print("Initialisation de ChromaDB...")
        # Crée un client ChromaDB qui stockera les données sur le disque dans le dossier `chroma_db`
        client = chromadb.PersistentClient(path="./chroma_db")

        print("Initialisation de la fonction d'embedding via Ollama...")
        # Crée une fonction d'embedding qui utilise le modèle spécifié via Ollama.
        # C'est cette fonction qui sera appelée par ChromaDB pour convertir le texte en vecteurs.
        ollama_ef = embedding_functions.OllamaEmbeddingFunction(
            url="http://localhost:11434/api/embeddings",
            model_name=self.embedding_model,
            #timeout=120,
        )

        # --- 4. Création de la collection et stockage des données ---

        print(f"Création ou chargement de la collection : {self.collection_name}")
        # Crée une nouvelle collection (ou la charge si elle existe déjà).
        # La fonction d'embedding est passée à la création pour que la collection sache comment traiter les textes.
        self.collection = client.get_or_create_collection(
            name=self.collection_name, embedding_function=ollama_ef
        )

        if self.__chroma_initialized:
            print(f"Nombre de documents stockés : {self.collection.count()}")
            return 
        
        for index_file, pdf_file in enumerate(self.file_pathes) : 
            
            pdf_file_path = str(pdf_file)

            # Charge et découpe le PDF
            pdf_chunks = self.load_and_chunk_pdf(pdf_file_path)

            print(f"Stockage des chunks du fichier {pdf_file_path} dans ChromaDB...")

            batch_size=10
            
            nb = len(pdf_chunks)

            # Traiter les chunks par lots
            for i in range(0, len(pdf_chunks), batch_size):

                print(f"\r...chunks {(i)} à {(i+batch_size)} sur {nb}...", end="", flush=True)
                sys.stdout.flush()

                batch_chunks = pdf_chunks[i:i + batch_size]
                batch_ids = [f"fi{index_file}_ch{i + j}" for j, _ in enumerate(batch_chunks)]

                # Ajouter le lot actuel à la collection
                self.collection.add(documents=batch_chunks, ids=batch_ids)
            print()

            
        print("\n--- Base de données vectorielle créée avec succès ! ---")

        self.__initialized=True
        print(f"Nombre de documents stockés : {self.collection.count()}")
        


    def load_and_chunk_pdf(self, file_path : str, chunk_size=700, chunk_overlap=100):
    #def load_and_chunk_pdf(self, file_path : str, chunk_size=1000, chunk_overlap=200):
        """
        Charge un fichier PDF, en extrait le texte et le découpe en morceaux (chunks).
        Taille de chunk recommanndée: 500 à 1000 tokens
        Chevauhement recommandé: 50 à 200 tokens
        """
        print(f"Chargement du fichier : {file_path}")
        reader = PdfReader(file_path)
        text = "".join(page.extract_text() for page in reader.pages)
        # print(f"Le document contient {len(text)} caractères.")

        # print("Découpage du texte en chunks...")
        chunks = []
        for i in range(0, len(text), chunk_size - chunk_overlap):
            # print(text[i : i + chunk_size])
            chunks.append(text[i : i + chunk_size])
        # print(f"{len(chunks)} chunks ont été créés.")
        return chunks
    
    def retrieve_documents(self, state: RAGState) -> RAGState:
        """Nœud pour récupérer les documents pertinents"""
        print(f"Recherche de documents pour: {state['question']}")
        docs = self.retriever.get_relevant_documents(state["question"])
        context = [doc.page_content for doc in docs]
        return {
            **state,
            "context": context
        }
    
    def generate_answer(self, state: RAGState) -> RAGState:
        """Nœud pour générer la réponse"""
        print("Génération de la réponse...")
        # Prépare le prompt avec le contexte et la question
        formatted_prompt = self.prompt.format_messages(
            context="\n\n".join(state["context"]),
            question=state["question"]
        )
        
        # Génère la réponse
        response = self.llm.invoke(formatted_prompt)
        answer = self.output_parser.invoke(response)
        
        return {
            **state,
            "answer": answer
        }
    
    def initialize_langgraph(self):
        print("Initialisation des composants LangGraph...")
        
        # Initialise le client Ollama pour les embeddings
        ollama_embeddings = OllamaEmbeddings(model=self.embedding_model)
        
        # Initialise le client ChromaDB pour se connecter à la base de données existante
        vectorstore = Chroma(
            client=chromadb.PersistentClient(path="./chroma_db"),
            collection_name=self.collection_name,
            embedding_function=ollama_embeddings
        )
        
        # Crée un retriever à partir du vectorstore
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Initialise le modèle de chat Ollama
        self.llm = ChatOllama(model=self.llm_model)
        
        # Template du prompt pour le LLM
        template = """Réponds à la question en te basant uniquement sur le contexte suivant:
    {context}

    Question: {question}
    """
        self.prompt = ChatPromptTemplate.from_template(template)
        
        # Parser pour la sortie
        self.output_parser = StrOutputParser()
        
        # --- Définition des nœuds du graphe ---
    
    
    
        # --- Construction du graphe ---
        workflow = StateGraph(RAGState)
        
        # Ajout des nœuds
        workflow.add_node("retrieve", self.retrieve_documents)
        workflow.add_node("generate", self.generate_answer)
        
        # Définition du flux
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        # Compilation du graphe
        rag_graph = workflow.compile()
        
        # Stockage du graphe pour utilisation ultérieure
        self.rag_graph = rag_graph
        
        print("Graphe RAG initialisé avec succès!")
        
        return rag_graph

    def query_rag(self, question: str) -> str:
        """Méthode pour interroger le système RAG avec LangGraph"""
        if not hasattr(self, 'rag_graph'):
            raise ValueError("Le graphe RAG n'est pas initialisé. Appelez initialize_langgraph() d'abord.")
        
        # État initial
        initial_state = {
            "question": question,
            "context": [],
            "answer": ""
        }
        
        # Exécution du graphe
        result = self.rag_graph.invoke(initial_state)
        
        return result["answer"]
    
    #region advanced
    
    def check_context_quality_adv(self, state: RAGState) -> str:
        """Vérifie si le contexte est suffisant"""
        if not state.get("has_context", False):
            return "no_context"
        if len(state["context"]) < 2:
            return "weak_context"
        return "good_context"
    
    def retrieve_documents_adv(self, state: RAGState) -> RAGState:
        """Récupération avec validation"""
        docs = self.retriever.get_relevant_documents(state["question"])
        context = [doc.page_content for doc in docs]
        
        return {
            **state,
            "context": context,
            "has_context": len(context) > 0
        }
    
    def generate_answer_adv(self, state: RAGState) -> RAGState:
        """Génération normale"""
        formatted_prompt = self.prompt.format_messages(
            context="\n\n".join(state["context"]),
            question=state["question"]
        )
        response = self.llm.invoke(formatted_prompt)
        answer = self.output_parser.invoke(response)
        
        return {**state, "answer": answer}
    
    def generate_fallback_answer_adv(self, state: RAGState) -> RAGState:
        """Génération de secours sans contexte suffisant"""
        fallback_prompt = ChatPromptTemplate.from_template(
            "Je n'ai pas trouvé suffisamment d'informations pertinentes pour répondre à cette question: {question}. "
            "Pouvez-vous reformuler votre question ou être plus spécifique?"
        )
        
        formatted_prompt = fallback_prompt.format_messages(question=state["question"])
        response = self.llm.invoke(formatted_prompt)
        answer = self.output_parser.invoke(response)
        
        return {**state, "answer": answer}
        

    # Exemple d'utilisation avancée avec conditions
    def initialize_advanced_langgraph(self):
        """Version avancée avec gestion d'erreurs et conditions"""
        print("Initialisation du graphe RAG avancé...")
        
        # ... (même initialisation que ci-dessus)
        ollama_embeddings = OllamaEmbeddings(model=self.embedding_model)
        vectorstore = Chroma(
            client=chromadb.PersistentClient(path="./chroma_db"),
            collection_name=self.collection_name,
            embedding_function=ollama_embeddings
        )
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        self.llm = ChatOllama(model=self.llm_model)
        self.prompt = ChatPromptTemplate.from_template("""Réponds à la question en te basant uniquement sur le contexte suivant:
    {context}

    Question: {question}
    """)
        self.output_parser = StrOutputParser()
        
        # Construction du graphe avancé
        workflow = StateGraph(RAGState)
        
        workflow.add_node("retrieve", self.retrieve_documents_adv)
        workflow.add_node("generate", self.generate_answer_adv)
        workflow.add_node("fallback", self.generate_fallback_answer_adv)
        
        workflow.set_entry_point("retrieve")
        workflow.add_conditional_edges(
            "retrieve",
            self.check_context_quality_adv,
            {
                "good_context": "generate",
                "weak_context": "generate",
                "no_context": "fallback"
            }
        )
        workflow.add_edge("generate", END)
        workflow.add_edge("fallback", END)
        
        self.rag_graph = workflow.compile()
        
        print("Graphe RAG avancé initialisé!")
        return self.rag_graph
    
    #endregion