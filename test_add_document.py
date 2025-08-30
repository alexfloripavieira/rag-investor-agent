#!/usr/bin/env python3
"""
Script para testar adição de documento ao RAG
"""
import os
from dotenv import load_dotenv
from vector_store import VectorStoreManager
import config

# Carregar variáveis de ambiente
load_dotenv()

def test_add_document():
    """Testa a adição de um documento ao RAG."""
    print("📄 TESTE DE ADIÇÃO DE DOCUMENTO")
    print("=" * 50)
    
    # Verificar se há PDFs processados
    pdf_path = "/home/alexvieira/rag-investor-agent/reports_processed/desmistificandofii.com.br_relatorios_relatorio-FIIS-30-12-07-2025.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF não encontrado: {pdf_path}")
        return
    
    print(f"📁 Arquivo encontrado: {os.path.basename(pdf_path)}")
    print(f"📊 Tamanho: {os.path.getsize(pdf_path) / (1024*1024):.1f} MB")
    
    # Inicializar vector store
    print("\n🔧 Inicializando Vector Store...")
    vector_manager = VectorStoreManager()
    
    # Contar documentos antes
    count_before = vector_manager.count_documents()
    print(f"📊 Chunks antes: {count_before}")
    
    # Adicionar documento
    print("\n➕ Adicionando documento ao RAG...")
    try:
        chunks_added = vector_manager.add_documents_from_file(pdf_path)
        print(f"✅ Adicionados {chunks_added} chunks")
        
        # Contar documentos depois
        count_after = vector_manager.count_documents()
        print(f"📊 Chunks depois: {count_after}")
        
        # Testar busca
        print("\n🔍 Testando busca...")
        results = vector_manager.search_similarity("FII", k=3)
        if results:
            print(f"✅ Encontrados {len(results)} resultados para 'FII'")
            for i, (doc, score) in enumerate(results):
                print(f"   {i+1}. Score: {score:.3f} - {doc.page_content[:100]}...")
        else:
            print("❌ Nenhum resultado encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao adicionar documento: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_add_document()