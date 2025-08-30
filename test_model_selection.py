#!/usr/bin/env python3
"""
Script para testar a seleção de modelos LLM
"""
import config

def test_model_configuration():
    """Testa a configuração dos modelos disponíveis."""
    print("🤖 TESTE DE CONFIGURAÇÃO DE MODELOS LLM")
    print("=" * 60)
    
    print(f"✅ Modelo padrão: {config.LLM_MODEL_NAME}")
    print(f"✅ Modelo de embedding: {config.EMBEDDING_MODEL_NAME}")
    
    print(f"\n📋 Modelos disponíveis ({len(config.AVAILABLE_LLM_MODELS)}):")
    for model_key, model_description in config.AVAILABLE_LLM_MODELS.items():
        default_marker = " ⭐ (PADRÃO)" if model_key == config.LLM_MODEL_NAME else ""
        print(f"   • {model_key}: {model_description}{default_marker}")
    
    print("\n🧪 Testando importação de llm_services...")
    try:
        import llm_services
        print("✅ llm_services importado com sucesso")
        
        # Testar se as funções aceitam o parâmetro model_name
        import inspect
        
        functions_to_test = [
            'generate_insights_from_documents',
            'generate_market_summary', 
            'extract_key_metrics',
            'setup_agent'
        ]
        
        for func_name in functions_to_test:
            if hasattr(llm_services, func_name):
                func = getattr(llm_services, func_name)
                sig = inspect.signature(func)
                if 'model_name' in sig.parameters:
                    print(f"✅ {func_name} - aceita parâmetro model_name")
                else:
                    print(f"❌ {func_name} - NÃO aceita parâmetro model_name")
            else:
                print(f"❌ {func_name} - função não encontrada")
                
    except ImportError as e:
        print(f"❌ Erro ao importar llm_services: {e}")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE DE MODELOS CONCLUÍDO")
    
    print("\n💡 Como usar:")
    print("   • Na barra lateral, selecione o modelo desejado no dropdown")
    print("   • O modelo será aplicado a todas as operações (chat, insights, resumos)")
    print("   • Modelos premium (GPT-4o, GPT-4) têm maior qualidade mas custam mais")

if __name__ == "__main__":
    test_model_configuration()