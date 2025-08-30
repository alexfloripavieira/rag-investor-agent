from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
import os

from config import VECTOR_STORE_DIR, CHROMA_COLLECTION_NAME, EMBEDDING_MODEL_NAME

class VectorStoreManager:
    def __init__(self):
        """Inicializa o gerenciador do vector store."""
        self.embedding_function = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
        self.vector_store = None
        self._ensure_vector_store_exists()
    
    def _ensure_vector_store_exists(self):
        """Garante que o vector store existe e está inicializado."""
        try:
            # Usar sempre o diretório configurado
            actual_dir = VECTOR_STORE_DIR
            
            # Criar diretório se não existir
            if not os.path.exists(actual_dir):
                os.makedirs(actual_dir)
                print(f"📁 Criado diretório: {actual_dir}")
            
            self.vector_store = Chroma(
                collection_name=CHROMA_COLLECTION_NAME,
                embedding_function=self.embedding_function,
                persist_directory=actual_dir
            )
            print(f"✅ ChromaDB inicializado em: {actual_dir}")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar ChromaDB: {e}")
            self.vector_store = None

    def add_documents_from_file(self, file_path):
        """Carrega, divide e adiciona documentos de um arquivo ao ChromaDB."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
        print(f"📄 Processando arquivo: {os.path.basename(file_path)}")
        
        try:
            # Carregar o PDF
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            print(f"📚 Carregadas {len(documents)} páginas")
            
            # Dividir em chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=200,
                separators=["\n\n", "\n", " ", ""]
            )
            docs_split = text_splitter.split_documents(documents)
            print(f"✂️ Criados {len(docs_split)} chunks")
            
            # Adicionar metadados
            for i, doc in enumerate(docs_split):
                doc.metadata.update({
                    'source_file': os.path.basename(file_path),
                    'chunk_id': i,
                    'total_chunks': len(docs_split)
                })
            
            # Adicionar ao ChromaDB
            if self.vector_store is None:
                # Re-inicializar se necessário
                self._ensure_vector_store_exists()
                if self.vector_store is None:
                    raise Exception("Não foi possível inicializar o vector store")
            
            # Adicionar documentos ao vector store existente
            self.vector_store.add_documents(docs_split)
            print("➕ Documentos adicionados ao vector store")
            
            print(f"✅ Vector store atualizado com sucesso!")
            return len(docs_split)
            
        except Exception as e:
            print(f"❌ Erro ao processar arquivo: {e}")
            raise

    def count_documents(self):
        """Retorna o número de documentos na coleção ChromaDB."""
        if self.vector_store is None:
            return 0
        try:
            collection = self.vector_store._collection
            count = collection.count()
            print(f"📊 Total de chunks no vector store: {count}")
            return count
        except Exception as e:
            print(f"⚠️ Erro ao contar documentos: {e}")
            return 0

    def get_retriever(self, k=4):
        """Retorna um retriever para busca por similaridade."""
        if self.vector_store is None:
            self._ensure_vector_store_exists()
            
        if self.vector_store is None:
            raise ValueError("Vector store não foi inicializado corretamente")
            
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
    
    def search_similarity(self, query, k=4):
        """Busca documentos similares e retorna com scores."""
        if self.vector_store is None:
            return []
            
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            print(f"🔍 Encontrados {len(results)} documentos para: '{query[:50]}...'")
            return results
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []
    
    def get_collection_info(self):
        """Retorna informações sobre a coleção."""
        if self.vector_store is None:
            return {}
            
        try:
            collection = self.vector_store._collection
            return {
                'name': collection.name,
                'count': collection.count(),
                'metadata': collection.metadata
            }
        except Exception as e:
            print(f"⚠️ Erro ao obter informações da coleção: {e}")
            return {}