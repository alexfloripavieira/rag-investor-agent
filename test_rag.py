#!/usr/bin/env python3
"""
Script de teste para verificar o pipeline RAG
"""
import os
from dotenv import load_dotenv
from vector_store import VectorStoreManager
import config

# Carregar variáveis de ambiente
load_dotenv()

def test_rag_pipeline():
    """Testa o pipeline RAG completo."""
    print("🧪 TESTE DO PIPELINE RAG")
    print("=" * 50)
    
    # Garantir que diretórios existem
    config.ensure_directories_exist()
    print("✅ Diretórios verificados")
    
    # Inicializar o vector store manager
    print("\n1. Inicializando Vector Store Manager...")
    try:
        vector_manager = VectorStoreManager()
        print("✅ Vector Store Manager inicializado")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        return
    
    # Verificar se há documentos
    print("\n2. Verificando documentos existentes...")
    doc_count = vector_manager.count_documents()
    collection_info = vector_manager.get_collection_info()
    
    print(f"📊 Chunks no vector store: {doc_count}")
    print(f"🗂️ Nome da coleção: {collection_info.get('name', 'N/A')}")
    print(f"🧠 Modelo de embeddings: {config.EMBEDDING_MODEL_NAME}")
    
    if doc_count == 0:
        print("⚠️ Nenhum documento encontrado. Verifique se há PDFs processados.")
        return
    
    # Testar busca por similaridade
    print("\n3. Testando busca por similaridade...")
    test_queries = [
        "investimento",
        "rentabilidade", 
        "risco",
        "portfolio",
        "FII"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Buscando: '{query}'")
        results = vector_manager.search_similarity(query, k=2)
        
        if results:
            for i, (doc, score) in enumerate(results[:2]):
                print(f"   Resultado {i+1}: Score {score:.3f}")
                print(f"   Fonte: {doc.metadata.get('source_file', 'N/A')}")
                print(f"   Chunk: {doc.metadata.get('chunk_id', 'N/A')}/{doc.metadata.get('total_chunks', 'N/A')}")
                print(f"   Preview: {doc.page_content[:100]}...")
                print()
        else:
            print(f"   ❌ Nenhum resultado encontrado para '{query}'")
    
    # Testar retriever
    print("\n4. Testando Retriever...")
    try:
        retriever = vector_manager.get_retriever(k=3)
        test_docs = retriever.invoke("Como investir em FII?")
        print(f"✅ Retriever retornou {len(test_docs)} documentos")
        
        for i, doc in enumerate(test_docs):
            print(f"   Doc {i+1}: {doc.metadata.get('source_file', 'N/A')} - {doc.page_content[:80]}...")
            
    except Exception as e:
        print(f"❌ Erro no retriever: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_rag_pipeline()