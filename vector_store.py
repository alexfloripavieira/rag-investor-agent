import os
import shutil

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings

from config import (
    RAG_FILES_DIR,
    REPORTS_PROCESSED_DIR,
    VECTOR_STORE_PATH,
)


class VectorStoreManager:
    def __init__(self):
        self

    def load_documents(self):
        docs = []
        processed_dir = REPORTS_PROCESSED_DIR
        os.makedirs(processed_dir, exist_ok=True)

        files = [
            os.path.join(RAG_FILES_DIR, f)
            for f in os.listdir(RAG_FILES_DIR)
        ]

        for file in files:
            loader = PyPDFLoader(file)
            file_docs = loader.load()
            if file_docs:
                docs.extend(file_docs)

                dest_path = os.path.join(processed_dir, os.path.basename(file))
                shutil.move(file, dest_path)

        if docs:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )
            splits = text_splitter.split_documents(docs)
            return Chroma.from_documents(
                documents=splits,
                embedding=OpenAIEmbeddings(),
                persist_directory=VECTOR_STORE_PATH,
            )

    def add_documents_from_file():
        return Chroma(
            embedding_function=OpenAIEmbeddings(),
            persist_directory=VECTOR_STORE_PATH,
        )
