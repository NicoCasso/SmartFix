import os
import sys
from pathlib import Path
import httpx

import chromadb
from chromadb.utils import embedding_functions
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain_community.vectorstores import Chroma
#from OllamaCore.sf_custom_ollama_embedding_function import SfCustomOllamaEmbeddingFunction
from PyPDF2 import PdfReader

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
    
    def initialize_langchain(self):
        pass

        # print("Initialisation des composants LangChain...")

        # # Initialise le client Ollama pour les embeddings
        # ollama_embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

        # # Initialise le client ChromaDB pour se connecter à la base de données existante.
        # # Le chemin doit correspondre à l'endroit où la DB a été créée par module5_creation_db.py
        # # (qui est dans le même dossier 'code')
        # vectorstore = Chroma(
        #     client=chromadb.PersistentClient(path="./chroma_db"),
        #     collection_name=COLLECTION_NAME,
        #     embedding_function=ollama_embeddings
        # )

        # # Crée un retriever à partir du vectorstore.
        # # Le retriever est responsable de la recherche des documents pertinents.
        # retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # Récupère les 3 chunks les plus pertinents

        # # Initialise le modèle de chat Ollama
        # llm = ChatOllama(model=LLM_MODEL)

        # # --- 3. Définition du prompt RAG ---

        # # Le template du prompt pour le LLM.
        # # Il inclut le contexte récupéré et la question de l'utilisateur.
        # template = """Réponds à la question en te basant uniquement sur le contexte suivant:
        # {context}

        # Question: {question}
        # """
        # prompt = ChatPromptTemplate.from_template(template)

        # # --- 4. Construction de la chaîne RAG avec LangChain Expression Language (LCEL) ---

        # # La chaîne RAG est construite en utilisant LCEL pour une meilleure lisibilité et modularité.
        # rag_chain = (
        #     {"context": retriever, "question": RunnablePassthrough()} # Étape de recherche (Retrieval)
        #     | prompt                                                  # Étape d'augmentation (Augmented)
        #     | llm                                                     # Étape de génération (Generation)
        #     | StrOutputParser()                                       # Parse la sortie du LLM en chaîne de caractères
        # )


    
    def get_response(self):
        pass

   

