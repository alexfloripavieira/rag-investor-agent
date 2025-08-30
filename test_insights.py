#!/usr/bin/env python3
"""
Script para testar a geração de insights dos relatórios
"""
import os
from dotenv import load_dotenv
from vector_store import VectorStoreManager
import llm_services

# Carregar variáveis de ambiente
load_dotenv()

def test_insights_generation():
    """Testa a geração de insights dos relatórios."""
    print("💡 TESTE DE GERAÇÃO DE INSIGHTS")
    print("=" * 60)
    
    # Verificar se OpenAI API key está configurada
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY não configurada!")
        return
    print("✅ OpenAI API Key configurada")
    
    # Inicializar vector store
    print("\n1. Inicializando Vector Store...")
    vector_manager = VectorStoreManager()
    doc_count = vector_manager.count_documents()
    
    if doc_count == 0:
        print("⚠️ Nenhum documento no vector store. Execute test_add_document.py primeiro.")
        return
    
    print(f"📊 Vector Store com {doc_count} chunks prontos")
    
    # Obter retriever
    retriever = vector_manager.get_retriever(k=4)
    
    print("\n2. Testando Resumo Executivo...")
    try:
        summary = llm_services.generate_market_summary(retriever)
        print("✅ Resumo executivo gerado com sucesso")
        print(f"📄 Tamanho: {len(summary)} caracteres")
        print(f"🔍 Preview: {summary[:200]}...")
        print()
    except Exception as e:
        print(f"❌ Erro no resumo executivo: {e}")
    
    print("\n3. Testando Extração de Métricas...")
    try:
        metrics = llm_services.extract_key_metrics(retriever)
        if "error" in metrics:
            print(f"❌ Erro nas métricas: {metrics['error']}")
        else:
            print("✅ Métricas extraídas com sucesso")
            metrics_text = metrics.get("metrics", "")
            print(f"📊 Tamanho: {len(metrics_text)} caracteres")
            print(f"🔢 Preview: {metrics_text[:200]}...")
        print()
    except Exception as e:
        print(f"❌ Erro na extração de métricas: {e}")
    
    print("\n4. Testando Insights Detalhados...")
    try:
        insights = llm_services.generate_insights_from_documents(retriever)
        print(f"✅ {len(insights)} insights detalhados gerados")
        
        for i, (query, insight) in enumerate(insights.items(), 1):
            print(f"\n📋 Insight {i}: {query}")
            if insight.startswith("Erro"):
                print(f"   ❌ {insight}")
            else:
                print(f"   ✅ Gerado ({len(insight)} caracteres)")
                print(f"   🔍 Preview: {insight[:150]}...")
                
    except Exception as e:
        print(f"❌ Erro nos insights detalhados: {e}")
    
    print("\n5. Teste de Performance...")
    import time
    
    start_time = time.time()
    test_docs = retriever.invoke("FII investimento rentabilidade")
    retrieval_time = time.time() - start_time
    
    print(f"🔍 Recuperação: {len(test_docs)} docs em {retrieval_time:.2f}s")
    
    # Teste simples de geração
    start_time = time.time()
    try:
        quick_summary = llm_services.generate_market_summary(retriever)
        generation_time = time.time() - start_time
        print(f"🤖 Geração: {len(quick_summary)} chars em {generation_time:.2f}s")
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE DE INSIGHTS CONCLUÍDO")
    print("\n💡 Dicas para melhorar insights:")
    print("   • Adicione mais documentos para análises mais ricas")
    print("   • Documentos de diferentes períodos mostram tendências")
    print("   • Dados estruturados geram métricas mais precisas")

if __name__ == "__main__":
    test_insights_generation()