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
LLM_MODEL_NAME = "gpt-4o-mini"  # Modelo padrão
EMBEDDING_MODEL_NAME = "text-embedding-3-small"

# --- Opções de Modelos LLM Disponíveis ---
AVAILABLE_LLM_MODELS = {
    "gpt-4o-mini": "GPT-4o Mini (Rápido e econômico)",
    "gpt-4o": "GPT-4o (Mais inteligente, mais caro)",
    "gpt-4-turbo": "GPT-4 Turbo (Avançado)",
    "gpt-3.5-turbo": "GPT-3.5 Turbo (Econômico)",
    "gpt-4": "GPT-4 (Clássico)",
    "gpt-5": "GPT-5 (Mais avançado e caro)"
}

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