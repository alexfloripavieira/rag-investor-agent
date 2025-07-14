import os

from langchain_community.document_loaders import PyPDFLoader

from config import RAG_FILES_DIR, REPORTS_PROCESSED_DIR


def save_uploaded_files(uploaded_files):
    """Salva os arquivos enviados na pasta de novos relatórios."""
    for uploaded_file in uploaded_files:
        with open(os.path.join(RAG_FILES_DIR, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
    return len(uploaded_files)


def get_new_reports_to_process():
    """Retorna uma lista de caminhos de arquivos na pasta de novos relatórios."""
    return [
        os.path.join(RAG_FILES_DIR, f)
        for f in os.listdir(RAG_FILES_DIR)
        if f.endswith(".pdf")
    ]


def get_all_processed_reports():
    """Lista todos os relatórios na pasta de processados."""
    if not os.path.exists(REPORTS_PROCESSED_DIR):
        return []
    return sorted([f for f in os.listdir(REPORTS_PROCESSED_DIR) if f.endswith(".pdf")])


def get_full_pdf_text(file_path):
    """Extrai e retorna todo o texto de um único arquivo PDF."""
    loader = PyPDFLoader(file_path)
    return "\n".join([doc.page_content for doc in loader.load()])
