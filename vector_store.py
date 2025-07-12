"""Módulo de Banco de Dados Vetorial

Gerencia a criação, atualização e consulta do ChromaDB.
"""
import chromadb
from langchain_chroma import Chroma # Importação atualizada
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader

from config import VECTOR_STORE_DIR, EMBEDDING_MODEL_NAME, CHROMA_COLLECTION_NAME

class VectorStoreManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
        self.client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
        self.vector_store = Chroma(
            client=self.client,
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
        )

    def add_documents_from_file(self, file_path):
        """Carrega, divide e adiciona documentos de um arquivo ao ChromaDB."""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs_split = text_splitter.split_documents(documents)
        
        self.vector_store.add_documents(docs_split)

    def count_documents(self):
        """Retorna o número de documentos na coleção ChromaDB."""
        return self.vector_store._collection.count()

    def get_retriever(self):
        """Retorna um retriever para busca por similaridade."""
        return self.vector_store.as_retriever()