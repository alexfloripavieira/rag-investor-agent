#!/usr/bin/env python3
"""
Script para testar integração completa do agente com RAG
"""
import os
from dotenv import load_dotenv
from vector_store import VectorStoreManager
import llm_services

# Carregar variáveis de ambiente
load_dotenv()

def test_agent_integration():
    """Testa a integração completa do agente com RAG."""
    print("🤖 TESTE DE INTEGRAÇÃO DO AGENTE COM RAG")
    print("=" * 60)
    
    # Verificar se OpenAI API key está configurada
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY não configurada!")
        return
    print("✅ OpenAI API Key configurada")
    
    # Inicializar vector store
    print("\n🔧 Inicializando Vector Store...")
    vector_manager = VectorStoreManager()
    doc_count = vector_manager.count_documents()
    
    if doc_count == 0:
        print("⚠️ Nenhum documento no vector store. Execute test_add_document.py primeiro.")
        return
    
    print(f"📊 Vector Store com {doc_count} chunks prontos")
    
    # Inicializar agente
    print("\n🤖 Inicializando Agente...")
    try:
        retriever = vector_manager.get_retriever(k=4)
        agent = llm_services.setup_agent(retriever)
        print("✅ Agente inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar agente: {e}")
        return
    
    # Testar perguntas
    print("\n🔍 Testando perguntas ao agente...")
    
    test_questions = [
        "Quais são os melhores FIIs para investir?",
        "Qual a rentabilidade média dos FIIs?",
        "Como funcionam os Fundos de Investimento Imobiliário?",
        "Quais os riscos dos FIIs?",
        "Qual o valor de alguns FIIs mencionados no relatório?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Pergunta {i}: {question}")
        print("-" * 50)
        
        try:
            response = agent.invoke({"input": question})
            answer = response.get("output", "Sem resposta")
            print(f"🤖 Resposta: {answer}")
            
            # Verificar se o agente usou o retriever
            if "relatório" in answer.lower() or "documento" in answer.lower() or "fii" in answer.lower():
                print("✅ Agente parece ter usado informações do RAG")
            else:
                print("⚠️ Resposta genérica - pode não ter usado RAG")
                
        except Exception as e:
            print(f"❌ Erro na pergunta: {e}")
    
    # Testar retriever diretamente
    print(f"\n🔍 Teste direto do Retriever...")
    try:
        docs = retriever.invoke("FII rentabilidade")
        print(f"✅ Retriever retornou {len(docs)} documentos")
        for i, doc in enumerate(docs[:2]):
            print(f"   Doc {i+1}: {doc.metadata.get('source_file', 'N/A')} - {doc.page_content[:100]}...")
    except Exception as e:
        print(f"❌ Erro no retriever: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE DE INTEGRAÇÃO CONCLUÍDO")

if __name__ == "__main__":
    test_agent_integration()