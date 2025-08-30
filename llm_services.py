
"""Módulo de Serviços de LLM

Encapsula interações com a API da OpenAI: Agente, Resumo e TTS.
"""
from io import BytesIO
from openai import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationBufferMemory

from config import LLM_MODEL_NAME, TTS_VOICE

# Cliente OpenAI para TTS será inicializado quando necessário
client = None

def get_openai_client():
    """Retorna cliente OpenAI inicializado."""
    global client
    if client is None:
        client = OpenAI()
    return client

def get_summarizer_chain(model_name=None):
    """Cria e retorna uma cadeia para resumir textos."""
    if model_name is None:
        model_name = LLM_MODEL_NAME
    llm = ChatOpenAI(model_name=model_name, temperature=0)
    prompt = PromptTemplate.from_template(
        "Faça um resumo conciso e bem estruturado em português do seguinte texto:\n\n{text_to_summarize}\n\nRESUMO:"
    )
    return prompt | llm

def generate_insights_from_documents(retriever, model_name=None):
    """Gera insights automáticos dos documentos usando RAG."""
    if model_name is None:
        model_name = LLM_MODEL_NAME
    llm = ChatOpenAI(model_name=model_name, temperature=0.3)
    
    # Queries para extrair insights específicos
    insight_queries = [
        "Quais são os principais FIIs mencionados e suas características?",
        "Quais são os rendimentos e dividendos mais destacados?",
        "Quais setores de investimento imobiliário são mais mencionados?",
        "Quais são as principais recomendações de investimento?",
        "Quais são os riscos e oportunidades identificados?",
        "Quais são as tendências do mercado imobiliário mencionadas?"
    ]
    
    insights = {}
    
    for query in insight_queries:
        try:
            # Buscar documentos relevantes
            docs = retriever.invoke(query)
            if docs:
                # Combinar contexto dos documentos
                context = "\n\n".join([doc.page_content for doc in docs[:3]])
                
                # Prompt para gerar insight
                prompt = f"""
                Com base no seguinte contexto dos relatórios financeiros, responda de forma clara e estruturada:

                PERGUNTA: {query}

                CONTEXTO:
                {context}

                RESPOSTA (seja específico e cite dados quando possível):
                """
                
                response = llm.invoke(prompt)
                insights[query] = response.content
                
        except Exception as e:
            insights[query] = f"Erro ao gerar insight: {e}"
    
    return insights

def generate_market_summary(retriever, model_name=None):
    """Gera um resumo executivo do mercado baseado nos documentos."""
    if model_name is None:
        model_name = LLM_MODEL_NAME
    llm = ChatOpenAI(model_name=model_name, temperature=0.2)
    
    try:
        # Buscar documentos para análise geral
        docs = retriever.invoke("resumo investimentos FII mercado tendências")
        
        if not docs:
            return "Não há documentos suficientes para gerar resumo do mercado."
        
        # Combinar contexto
        context = "\n\n".join([doc.page_content for doc in docs[:4]])
        
        prompt = f"""
        Você é um analista financeiro especializado em FIIs. Baseado nos relatórios fornecidos, 
        crie um RESUMO EXECUTIVO do mercado de Fundos Imobiliários.

        CONTEXTO DOS RELATÓRIOS:
        {context}

        Crie um resumo executivo com:
        1. **Situação Atual do Mercado**
        2. **Principais Oportunidades**  
        3. **Principais Riscos**
        4. **Recomendações Gerais**

        Seja objetivo, use dados específicos quando disponíveis, e mantenha linguagem profissional:
        """
        
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        return f"Erro ao gerar resumo do mercado: {e}"

def extract_key_metrics(retriever, model_name=None):
    """Extrai métricas chave dos relatórios."""
    try:
        # Buscar documentos com dados numéricos
        docs = retriever.invoke("valor preço rentabilidade dividend yield cotação R$")
        
        if not docs:
            return {}
        
        if model_name is None:
            model_name = LLM_MODEL_NAME
        llm = ChatOpenAI(model_name=model_name, temperature=0)
        context = "\n\n".join([doc.page_content for doc in docs[:3]])
        
        prompt = f"""
        Extraia APENAS os dados numéricos e métricas específicas do seguinte contexto.
        Retorne em formato estruturado:

        CONTEXTO:
        {context}

        Extraia e organize:
        - Valores de FIIs (formato: CÓDIGO: R$ X,XX)
        - Rentabilidades/Yields (formato: X,XX% ou X.XX%)
        - Dividendos (formato: R$ X,XX por cota)
        
        Seja preciso e cite apenas valores que estão explícitos no texto:
        """
        
        response = llm.invoke(prompt)
        return {"metrics": response.content}
        
    except Exception as e:
        return {"error": f"Erro ao extrair métricas: {e}"}

def text_to_speech(text):
    """Converte texto para áudio usando a API da OpenAI."""
    try:
        client = get_openai_client()
        response = client.audio.speech.create(
            model="tts-1",
            voice=TTS_VOICE,
            input=text
        )
        # Retorna os bytes diretamente para compatibilidade com st.audio
        return response.content
    except Exception as e:
        print(f"Erro na API de TTS: {e}")
        return None

def concatenate_audio_files(audio_contents_list):
    """Concatena múltiplos arquivos de áudio usando pydub."""
    try:
        from pydub import AudioSegment
        from io import BytesIO
        
        if not audio_contents_list:
            return None
            
        # Carregar o primeiro áudio
        combined = AudioSegment.from_file(BytesIO(audio_contents_list[0]), format="mp3")
        
        # Concatenar os demais
        for audio_content in audio_contents_list[1:]:
            audio_segment = AudioSegment.from_file(BytesIO(audio_content), format="mp3")
            combined += audio_segment
        
        # Exportar para bytes
        output_buffer = BytesIO()
        combined.export(output_buffer, format="mp3")
        return output_buffer.getvalue()
        
    except ImportError:
        print("pydub não está disponível para concatenação de áudio")
        return audio_contents_list[0] if audio_contents_list else None
    except Exception as e:
        print(f"Erro ao concatenar áudios: {e}")
        return audio_contents_list[0] if audio_contents_list else None

def setup_agent(retriever, model_name=None):
    """Inicializa e retorna o agente com suas ferramentas e memória."""
    if model_name is None:
        model_name = LLM_MODEL_NAME
    llm = ChatOpenAI(model_name=model_name, temperature=0)
    
    # Ferramenta RAG que usa o retriever do ChromaDB
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=retriever
    )
    # Usar invoke para a cadeia RAG
    def run_qa_chain_with_invoke(question):
        return qa_chain.invoke({"query": question})["result"]

    report_analyzer_tool = Tool(
        name="Analisador de Relatórios Financeiros",
        func=run_qa_chain_with_invoke,
        description="Você é um assistente virtual que irá responder dúvidas dos clientes. Use os seguintes trechos de contexto recuperado para responder à pergunta. Se você não souber a resposta, diga que não sabe. Use no máximo três frases e mantenha a resposta concisa"
    )
    
    # Ferramenta de busca na web
    web_search_tool = DuckDuckGoSearchRun()
    
    tools = [report_analyzer_tool, web_search_tool]
    
    # Configura a memória para o agente
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    return initialize_agent(
        tools,
        llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, # Agente que suporta memória
        verbose=True,
        memory=memory,
        handle_parsing_errors=True # Adicionado para tratamento de erros
    )
