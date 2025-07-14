from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader

from config import VECTOR_STORE_DIR

class VectorStoreManager:
    def __init__(self):
        self

    def add_documents_from_file(self, file_path):
        """Carrega, divide e adiciona documentos de um arquivo ao ChromaDB."""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs_split = text_splitter.split_documents(documents)
        
        Chroma.from_documents(
            documents=docs_split,
            embedding=OpenAIEmbeddings(),
            persist_directory=VECTOR_STORE_DIR,
        )

    # def count_documents(self):
    #     """Retorna o número de documentos na coleção ChromaDB."""
    #     return self.vector_store._collection.count()

    def get_retriever(self):
        """Retorna um retriever para busca por similaridade."""
        return Chroma(
        embedding_function=OpenAIEmbeddings(),
        persist_directory=VECTOR_STORE_DIR
    ).as_retriever()