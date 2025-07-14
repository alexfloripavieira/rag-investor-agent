"""Módulo de Manipulação de Arquivos

Responsável por salvar, mover e ler arquivos PDF.
"""
import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from config import REPORTS_NEW_DIR, REPORTS_PROCESSED_DIR

def save_uploaded_files(uploaded_files):
    """Salva os arquivos enviados na pasta de novos relatórios."""
    for uploaded_file in uploaded_files:
        with open(os.path.join(REPORTS_NEW_DIR, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
    return len(uploaded_files)

def get_new_reports_to_process():
    """Retorna uma lista de caminhos de arquivos na pasta de novos relatórios."""
    # CORREÇÃO: Usar os.listdir diretamente
    return [os.path.join(REPORTS_NEW_DIR, f) for f in os.listdir(REPORTS_NEW_DIR) if f.endswith('.pdf')]

def move_processed_file(file_path):
    """Move um arquivo da pasta de novos para a de processados."""
    filename = os.path.basename(file_path)
    shutil.move(file_path, os.path.join(REPORTS_PROCESSED_DIR, filename))

def get_all_processed_reports():
    """Lista todos os relatórios na pasta de processados."""
    if not os.path.exists(REPORTS_PROCESSED_DIR):
        return []
    # CORREÇÃO: Usar os.listdir diretamente
    return sorted([f for f in os.listdir(REPORTS_PROCESSED_DIR) if f.endswith('.pdf')])

def get_full_pdf_text(file_path):
    """Extrai e retorna todo o texto de um único arquivo PDF."""
    loader = PyPDFLoader(file_path)
    return "\n".join([doc.page_content for doc in loader.load()])
