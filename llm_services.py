
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
    
    # Queries para extrair insights específicos de FIIs e Ações
    insight_queries = [
        "Quais são os principais ativos (FIIs e ações) mencionados e suas características principais?",
        "Quais são os rendimentos, dividendos e performance financeira mais destacados?", 
        "Quais setores e segmentos (imobiliário, tecnologia, bancos, etc.) são mais mencionados?",
        "Quais são as principais recomendações de investimento baseadas nos dados financeiros?",
        "Quais são os riscos e oportunidades identificados nos investimentos analisados?",
        "Quais indicadores financeiros (P/L, ROE, dividend yield, etc.) se destacam nos relatórios?"
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
        # Buscar documentos para análise geral de investimentos
        docs = retriever.invoke("resumo investimentos FII ações mercado tendências performance")
        
        if not docs:
            return "Não há documentos suficientes para gerar resumo do mercado."
        
        # Combinar contexto
        context = "\n\n".join([doc.page_content for doc in docs[:4]])
        
        prompt = f"""
        Você é um analista financeiro especializado em investimentos. Baseado nos relatórios fornecidos, 
        crie um RESUMO EXECUTIVO do mercado de investimentos (FIIs, Ações e outros ativos).

        CONTEXTO DOS RELATÓRIOS:
        {context}

        Crie um resumo executivo com:
        1. **Situação Atual do Mercado** (FIIs, Ações, Setores)
        2. **Performance dos Ativos** (rendimentos, valorização, indicadores)
        3. **Principais Oportunidades** (setores em alta, ativos promissores)  
        4. **Principais Riscos** (setores em baixa, riscos sistêmicos)
        5. **Recomendações Gerais** (estratégias de investimento)

        Seja objetivo, cite tickers/códigos quando disponíveis, use dados específicos e mantenha linguagem profissional:
        """
        
        response = llm.invoke(prompt)
        return response.content
        
    except Exception as e:
        return f"Erro ao gerar resumo do mercado: {e}"

def extract_key_metrics(retriever, model_name=None):
    """Extrai métricas chave dos relatórios."""
    try:
        # Buscar documentos com dados numéricos de FIIs e Ações
        docs = retriever.invoke("valor preço cotação P/L ROE EBITDA receita lucro dividend yield rentabilidade R$")
        
        if not docs:
            return {}
        
        if model_name is None:
            model_name = LLM_MODEL_NAME
        llm = ChatOpenAI(model_name=model_name, temperature=0)
        context = "\n\n".join([doc.page_content for doc in docs[:3]])
        
        prompt = f"""
        Extraia APENAS os dados numéricos e métricas específicas do seguinte contexto financeiro.
        Retorne em formato estruturado:

        CONTEXTO:
        {context}

        Extraia e organize por categoria:

        **FIIs:**
        - Códigos de FIIs e valores (formato: CÓDIGO: R$ X,XX)
        - Dividend yield (formato: X,XX%)
        - Valor patrimonial por cota

        **Ações:**
        - Tickers e cotações (formato: TICKER4: R$ X,XX)
        - Indicadores (P/L: X,X | ROE: X,X% | P/VP: X,X)
        - Receita/Lucro líquido (em milhões)

        **Métricas Gerais:**
        - Rentabilidades e retornos
        - Dividendos pagos
        
        Seja preciso e cite apenas valores explícitos no texto:
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
    llm = ChatOpenAI(model_name=model_name, temperature=0.1)
    
    # Template específico para análise de investimentos (FIIs e Ações)
    template = """Use o contexto dos documentos financeiros para responder à pergunta do usuário de forma precisa e útil.

Contexto dos relatórios financeiros (FIIs, Ações e outros investimentos):
{context}

Pergunta do usuário: {question}

Instruções para sua resposta:
1. **Identifique o tipo de investimento**: FII, ação, fundo, etc.
2. **Analise o contexto**: Use todas as informações relevantes dos documentos
3. **Seja específico**: Inclua valores exatos, percentuais, datas, períodos
4. **Use terminologia adequada**:
   - FIIs: Valor patrimonial, dividend yield, vacância, NOI
   - Ações: P/L, P/VP, ROE, EBITDA, receita líquida, margem
5. **Cite códigos/tickers** quando disponíveis (ex: KNRI11, PETR4)
6. **Se não encontrar**: Informe claramente que a informação não está nos documentos processados

Resposta detalhada e técnica:"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt}
    )
    
    # Wrapper function para a ferramenta RAG
    def analyze_investment_reports(question):
        """Analisa relatórios de investimento para responder perguntas específicas."""
        try:
            print(f"🔍 Analisando pergunta: {question}")
            result = qa_chain.invoke({"query": question})
            print(f"📄 Resultado da busca: {result['result'][:200]}...")
            return result["result"]
        except Exception as e:
            print(f"❌ Erro ao acessar documentos: {str(e)}")
            return f"Erro ao acessar os documentos: {str(e)}"

    report_analyzer_tool = Tool(
        name="Consultar_Relatórios_Financeiros",
        func=analyze_investment_reports,
        description="""SEMPRE use esta ferramenta para perguntas sobre investimentos: FIIs (códigos, valores patrimoniais, rendimentos, dividend yield), Ações (tickers, balanço, DRE, indicadores como P/L, ROE, EBITDA), ou qualquer dado financeiro específico. Busca em todos os relatórios financeiros processados. Input: pergunta sobre investimentos."""
    )
    
    # Ferramenta de busca na web para informações gerais
    web_search_tool = DuckDuckGoSearchRun()
    
    tools = [report_analyzer_tool, web_search_tool]
    
    # Configurar a memória para o agente
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Inicializar agente com configuração padrão mas instruções específicas
    agent_executor = initialize_agent(
        tools,
        llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
        max_iterations=4,
        early_stopping_method="generate"
    )
    
    return agent_executor
