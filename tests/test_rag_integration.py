#!/usr/bin/env python3
"""
Script para testar automaticamente a integração RAG
"""
import os
from dotenv import load_dotenv
from vector_store import VectorStoreManager
import llm_services

# Carregar variáveis de ambiente
load_dotenv()

def test_rag_integration():
    """Testa automaticamente a integração RAG."""
    print("🧪 TESTE AUTOMÁTICO DE INTEGRAÇÃO RAG")
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
        print("⚠️ Nenhum documento no vector store.")
        print("💡 Execute primeiro: Processe alguns relatórios via interface web")
        return
    
    print(f"📊 Vector Store com {doc_count} chunks prontos")
    
    # Obter retriever e agente
    retriever = vector_manager.get_retriever(k=3)
    agent = llm_services.setup_agent(retriever)
    
    # Testes automatizados
    test_questions = [
        # Testes de recuperação básica
        {
            "categoria": "RECUPERAÇÃO BÁSICA",
            "pergunta": "Quais são os códigos dos FIIs mencionados nos relatórios?",
            "espera_conteudo": True,
            "palavras_chave": ["FII", "código", "11"]  # Códigos de FII terminam em 11
        },
        {
            "categoria": "RECUPERAÇÃO BÁSICA", 
            "pergunta": "Quais valores de dividend yield são mencionados?",
            "espera_conteudo": True,
            "palavras_chave": ["yield", "%", "dividend"]
        },
        
        # Testes de análise contextual
        {
            "categoria": "ANÁLISE CONTEXTUAL",
            "pergunta": "Quais são as principais recomendações dos relatórios?",
            "espera_conteudo": True,
            "palavras_chave": ["recomend", "invest", "suger"]
        },
        
        # Testes de controle negativo
        {
            "categoria": "CONTROLE NEGATIVO",
            "pergunta": "Qual é o preço atual das ações da Petrobras?",
            "espera_conteudo": False,
            "palavras_chave": ["relatórios", "não", "informação"]
        },
        {
            "categoria": "CONTROLE NEGATIVO",
            "pergunta": "Como está o clima hoje?",
            "espera_conteudo": False,
            "palavras_chave": ["não", "clima", "relatórios"]
        },
        
        # Teste de precisão
        {
            "categoria": "PRECISÃO",
            "pergunta": "Cite uma frase específica sobre riscos mencionada nos relatórios",
            "espera_conteudo": True,
            "palavras_chave": ["risco", "\"", "'"]  # Espera citações
        }
    ]
    
    print("\n2. Executando testes automatizados...")
    results = {"passed": 0, "failed": 0, "total": len(test_questions)}
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n--- TESTE {i}/{len(test_questions)}: {test['categoria']} ---")
        print(f"❓ Pergunta: {test['pergunta']}")
        
        try:
            # Fazer pergunta ao agente
            response = agent.invoke({"input": test['pergunta']})["output"]
            print(f"💬 Resposta: {response[:200]}...")
            
            # Verificar se a resposta é adequada
            response_lower = response.lower()
            
            if test['espera_conteudo']:
                # Deve conter informações dos documentos
                has_keywords = any(keyword.lower() in response_lower for keyword in test['palavras_chave'])
                has_content = len(response) > 50  # Resposta substancial
                
                if has_keywords and has_content:
                    print("✅ PASSOU - Resposta contém informações relevantes")
                    results["passed"] += 1
                else:
                    print("❌ FALHOU - Resposta muito genérica ou sem conteúdo dos documentos")
                    results["failed"] += 1
            else:
                # Não deve inventar informações
                indicates_limitation = any(keyword.lower() in response_lower for keyword in test['palavras_chave'])
                
                if indicates_limitation:
                    print("✅ PASSOU - Reconheceu limitação corretamente")
                    results["passed"] += 1
                else:
                    print("❌ FALHOU - Pode ter inventado informações")
                    results["failed"] += 1
                    
        except Exception as e:
            print(f"❌ ERRO no teste: {e}")
            results["failed"] += 1
    
    # Teste específico de recuperação
    print("\n3. Teste de recuperação direta...")
    try:
        test_docs = retriever.invoke("FII investimento dividend yield")
        print(f"📄 Recuperados: {len(test_docs)} documentos relevantes")
        
        if test_docs:
            print("✅ Retriever funcionando corretamente")
            print(f"📋 Exemplo de conteúdo: {test_docs[0].page_content[:150]}...")
            
            # Verificar metadados
            if 'source_file' in test_docs[0].metadata:
                print(f"📁 Fonte: {test_docs[0].metadata['source_file']}")
                print("✅ Metadados de fonte presentes")
            else:
                print("⚠️ Metadados de fonte ausentes")
        else:
            print("❌ Nenhum documento recuperado")
            
    except Exception as e:
        print(f"❌ Erro na recuperação: {e}")
    
    # Resultados finais
    print("\n" + "=" * 60)
    print("🎯 RESULTADOS DOS TESTES")
    print(f"✅ Passaram: {results['passed']}/{results['total']}")
    print(f"❌ Falharam: {results['failed']}/{results['total']}")
    success_rate = (results['passed'] / results['total']) * 100
    print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 RAG FUNCIONANDO CORRETAMENTE!")
    elif success_rate >= 60:
        print("⚠️ RAG funcionando parcialmente - verificar configurações")
    else:
        print("🚨 RAG COM PROBLEMAS - verificar implementação")
    
    print("\n💡 Recomendações:")
    print("   • Teste manualmente com as perguntas em perguntas_teste_rag.md")
    print("   • Compare diferentes modelos LLM (GPT-4o-mini vs GPT-4o)")
    print("   • Verifique se os documentos foram processados corretamente")
    print("   • Ajuste o parâmetro k do retriever se necessário")

if __name__ == "__main__":
    test_rag_integration()