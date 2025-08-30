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

def clean_redundant_directories():
    """Remove duplicatas e organiza arquivos corretamente."""
    print("🧹 Limpando redundâncias nos diretórios...")
    
    # Se arquivo já foi processado (está no ChromaDB), remover de reports_new
    # Isto será usado quando rebuild do Docker resolver as permissões
    processed_files = get_all_processed_reports()
    
    if os.path.exists(REPORTS_NEW_DIR):
        new_files = [f for f in os.listdir(REPORTS_NEW_DIR) if f.endswith('.pdf')]
        for file_name in new_files:
            if file_name in processed_files:
                try:
                    old_path = os.path.join(REPORTS_NEW_DIR, file_name)
                    os.remove(old_path)
                    print(f"🗑️ Removido duplicata: {file_name} (já processado)")
                except Exception as e:
                    print(f"⚠️ Não foi possível remover {file_name}: {e}")
    
    # Remover rag_files se existir
    rag_files_dir = "rag_files"
    if os.path.exists(rag_files_dir):
        try:
            import shutil
            shutil.rmtree(rag_files_dir)
            print("🗑️ Diretório rag_files removido (obsoleto)")
        except Exception as e:
            print(f"⚠️ Não foi possível remover rag_files: {e}")
    
    print("✅ Limpeza concluída")
