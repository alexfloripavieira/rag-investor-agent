
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

# Cliente OpenAI para TTS
client = OpenAI()

def get_summarizer_chain():
    """Cria e retorna uma cadeia para resumir textos."""
    llm = ChatOpenAI(model_name=LLM_MODEL_NAME, temperature=0.2)
    prompt = PromptTemplate.from_template(
        "Faça um resumo conciso e bem estruturado em português do seguinte texto:\n\n{text_to_summarize}\n\nRESUMO:"
    )
    return prompt | llm

def text_to_speech(text):
    """Converte texto para áudio usando a API da OpenAI."""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=TTS_VOICE,
            input=text
        )
        audio_fp = BytesIO(response.content)
        return audio_fp
    except Exception as e:
        print(f"Erro na API de TTS: {e}")
        return None

def setup_agent(retriever):
    """Inicializa e retorna o agente com suas ferramentas e memória."""
    llm = ChatOpenAI(model_name=LLM_MODEL_NAME, temperature=0)
    
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
        description="Use esta ferramenta para responder perguntas sobre o conteúdo de relatórios financeiros, fundos de investimento e análises de ações que foram carregados na aplicação. Sempre use esta ferramenta para perguntas sobre os relatórios. Forneça a pergunta completa como entrada."
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
