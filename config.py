"""Módulo de Configuração

Centraliza as constantes e configurações do projeto.
"""
import os

# --- Diretórios ---
# Usamos os nomes de diretório diretamente, pois o Docker Compose os monta no mesmo caminho
REPORTS_NEW_DIR = "reports_new"
REPORTS_PROCESSED_DIR = "reports_processed"
VECTOR_STORE_DIR = "vector_store_chroma"

# --- Modelos de IA ---
LLM_MODEL_NAME = "gpt-4o"
EMBEDDING_MODEL_NAME = "text-embedding-3-small"

# --- Configurações de Áudio ---
TTS_VOICE = "onyx"  # Voz masculina aveludada da OpenAI

# --- Nomes de Coleção do ChromaDB ---
CHROMA_COLLECTION_NAME = "investment_reports"

# --- Funções de Inicialização ---
def ensure_directories_exist():
    """Garante que todos os diretórios necessários existam ao iniciar a aplicação."""
    for dir_path in [REPORTS_NEW_DIR, REPORTS_PROCESSED_DIR, VECTOR_STORE_DIR]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)