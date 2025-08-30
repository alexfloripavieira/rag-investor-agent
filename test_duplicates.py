#!/usr/bin/env python3
"""
Script para testar o sistema anti-duplicação de documentos
"""
import os
import shutil
from dotenv import load_dotenv
from vector_store import VectorStoreManager
import config

# Carregar variáveis de ambiente
load_dotenv()

def test_duplicate_prevention():
    """Testa o sistema de prevenção de duplicatas."""
    print("🔒 TESTE DO SISTEMA ANTI-DUPLICAÇÃO")
    print("=" * 60)
    
    # Inicializar vector store
    print("\n1. Inicializando Vector Store Manager...")
    vector_manager = VectorStoreManager()
    
    # Verificar estado atual
    print("\n2. Estado atual do banco:")
    doc_count = vector_manager.count_documents()
    processed_docs = vector_manager.get_processed_documents_info()
    
    print(f"📊 Total de chunks: {doc_count}")
    print(f"📁 Documentos únicos: {len(processed_docs)}")
    
    if processed_docs:
        print("📋 Documentos já processados:")
        for doc_name, info in processed_docs.items():
            print(f"   • {doc_name}: {info['chunk_count']} chunks")
    
    # Testar com arquivo existente
    test_file = "/home/alexvieira/rag-investor-agent/reports_processed/desmistificandofii.com.br_relatorios_relatorio-FIIS-30-12-07-2025.pdf"
    
    if os.path.exists(test_file):
        print(f"\n3. Testando duplicata com arquivo existente...")
        print(f"📄 Arquivo de teste: {os.path.basename(test_file)}")
        
        # Verificar se já está processado
        is_duplicate = vector_manager.is_document_already_processed(test_file)
        print(f"🔍 Já processado: {'Sim' if is_duplicate else 'Não'}")
        
        # Tentar processar novamente
        print("\n4. Tentativa de reprocessamento...")
        chunks_added = vector_manager.add_documents_from_file(test_file)
        
        if chunks_added == 0:
            print("✅ SUCESSO: Duplicata detectada e bloqueada!")
        else:
            print(f"❌ FALHA: {chunks_added} chunks adicionados (deveria ser 0)")
        
        # Verificar estado final
        print("\n5. Estado final:")
        final_count = vector_manager.count_documents()
        print(f"📊 Chunks antes: {doc_count}")
        print(f"📊 Chunks depois: {final_count}")
        print(f"📈 Diferença: {final_count - doc_count} (deveria ser 0)")
        
        if final_count == doc_count:
            print("✅ TESTE PASSOU: Nenhum chunk duplicado foi adicionado!")
        else:
            print("❌ TESTE FALHOU: Chunks duplicados foram adicionados!")
    
    else:
        print(f"\n❌ Arquivo de teste não encontrado: {test_file}")
        print("💡 Execute test_add_document.py primeiro para ter dados de teste")
    
    # Teste de simulação de novo documento
    print(f"\n6. Simulando documento novo (inexistente)...")
    fake_file = "/fake/path/documento_novo.pdf"
    is_new = not vector_manager.is_document_already_processed(fake_file)
    print(f"🆕 Documento seria processado: {'Sim' if is_new else 'Não'}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE ANTI-DUPLICAÇÃO CONCLUÍDO")

if __name__ == "__main__":
    test_duplicate_prevention()