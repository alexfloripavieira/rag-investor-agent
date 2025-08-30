
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

def get_summarizer_chain():
    """Cria e retorna uma cadeia para resumir textos."""
    llm = ChatOpenAI(model_name=LLM_MODEL_NAME, temperature=0)
    prompt = PromptTemplate.from_template(
        "Faça um resumo conciso e bem estruturado em português do seguinte texto:\n\n{text_to_summarize}\n\nRESUMO:"
    )
    return prompt | llm

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
