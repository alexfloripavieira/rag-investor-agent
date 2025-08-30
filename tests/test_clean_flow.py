#!/usr/bin/env python3
"""
Script para testar fluxo limpo de diretórios
"""
import os
from dotenv import load_dotenv
import file_handler
import config

# Carregar variáveis de ambiente
load_dotenv()

def test_clean_directory_flow():
    """Testa o fluxo limpo de diretórios."""
    print("🧪 TESTE DO FLUXO LIMPO DE DIRETÓRIOS")
    print("=" * 60)
    
    # Garantir diretórios existem
    config.ensure_directories_exist()
    
    print("\n1. Estado atual dos diretórios:")
    
    # Verificar reports_new
    reports_new_dir = config.REPORTS_NEW_DIR
    if os.path.exists(reports_new_dir):
        new_files = [f for f in os.listdir(reports_new_dir) if f.endswith('.pdf')]
        print(f"📁 {reports_new_dir}: {len(new_files)} arquivos")
        for f in new_files:
            print(f"   • {f}")
    else:
        print(f"📁 {reports_new_dir}: Não existe")
    
    # Verificar reports_processed
    processed_files = file_handler.get_all_processed_reports()
    print(f"📁 {config.REPORTS_PROCESSED_DIR}: {len(processed_files)} arquivos")
    for f in processed_files:
        print(f"   • {f}")
    
    # Verificar rag_files
    rag_files_dir = "rag_files"
    if os.path.exists(rag_files_dir):
        try:
            rag_files = [f for f in os.listdir(rag_files_dir) if f.endswith('.pdf')]
            print(f"📁 {rag_files_dir}: {len(rag_files)} arquivos (OBSOLETO)")
            for f in rag_files:
                print(f"   • {f}")
        except PermissionError:
            print(f"📁 {rag_files_dir}: Sem permissão (criado pelo Docker)")
    else:
        print(f"📁 {rag_files_dir}: Não existe ✅")
    
    print("\n2. Testando função de limpeza:")
    try:
        file_handler.clean_redundant_directories()
    except Exception as e:
        print(f"⚠️ Erro na limpeza: {e}")
    
    print("\n3. Fluxo recomendado:")
    print("   1. Upload → reports_new/")
    print("   2. Processamento RAG → move para reports_processed/")
    print("   3. reports_new/ fica vazio para próximos uploads")
    
    print("\n4. Verificações finais:")
    
    # Verificar se há duplicatas
    new_reports = file_handler.get_new_reports_to_process()
    processed_reports = file_handler.get_all_processed_reports()
    
    duplicates = []
    for new_path in new_reports:
        new_name = os.path.basename(new_path)
        if new_name in processed_reports:
            duplicates.append(new_name)
    
    if duplicates:
        print("⚠️ DUPLICATAS ENCONTRADAS:")
        for dup in duplicates:
            print(f"   • {dup} (em reports_new E reports_processed)")
        print("💡 Execute docker-compose down && docker-compose up --build para limpar")
    else:
        print("✅ Nenhuma duplicata encontrada")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_clean_directory_flow()