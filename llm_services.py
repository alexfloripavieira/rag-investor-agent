"""Módulo de Serviços de LLM

Encapsula interações com a API da OpenAI: Agente, Resumo e TTS.
"""

from io import BytesIO

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from openai import OpenAI

from config import OPENAI_MODEL_NAME, OPENAI_MODEL_TEMPERATURE, TTS_VOICE
from memory import get_session_history
from prompts import contextualize_prompt, qa_prompt
from vector_store import VectorStoreManager

# Cliente OpenAI para TTS
client = OpenAI()


def get_summarizer_chain():
    """Cria e retorna uma cadeia para resumir textos."""
    llm = ChatOpenAI(model_name=OPENAI_MODEL_NAME, temperature=OPENAI_MODEL_TEMPERATURE)
    prompt = PromptTemplate.from_template(
        "Faça um resumo conciso e bem estruturado em português do seguinte texto:\n\n{text_to_summarize}\n\nRESUMO:"
    )
    return prompt | llm


def text_to_speech(text):
    """Converte texto para áudio usando a API da OpenAI."""
    try:
        response = client.audio.speech.create(
            model="tts-1", voice=TTS_VOICE, input=text
        )
        audio_fp = BytesIO(response.content)
        return audio_fp
    except Exception as e:
        print(f"Erro na API de TTS: {e}")
        return None


def get_rag_chain():
    llm = ChatOpenAI(model=OPENAI_MODEL_NAME, temperature=OPENAI_MODEL_TEMPERATURE)
    retriever = VectorStoreManager.add_documents_from_file().as_retriever()
    history_aware_chain = create_history_aware_retriever(
        llm, retriever, contextualize_prompt
    )
    question_answer_chain = create_stuff_documents_chain(llm=llm, prompt=qa_prompt)
    return create_retrieval_chain(history_aware_chain, question_answer_chain)


def get_conversational_rag_chain():
    rag_chain = get_rag_chain()
    return RunnableWithMessageHistory(
        runnable=rag_chain,
        get_session_history=get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
