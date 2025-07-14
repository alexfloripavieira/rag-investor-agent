"""Ponto de Entrada Principal - Interface do Usuário (Streamlit)

Orquestra as chamadas para os outros módulos e renderiza a UI.
"""
import os
import base64
import streamlit as st
from dotenv import load_dotenv

# Módulos locais
import config
import file_handler
from vector_store import VectorStoreManager
import llm_services
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Carregar variáveis e configurar ambiente
load_dotenv()
config.ensure_directories_exist()

def display_pdf(file_path):
    """Exibe um PDF no Streamlit usando um iframe."""
    if not os.path.exists(file_path):
        st.error(f"Erro: Arquivo PDF não encontrado em: {file_path}")
        return

    try:
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        
        st.write(f"Debug: File path: {file_path}")
        st.write(f"Debug: File size: {len(pdf_bytes)} bytes")
        st.write(f"Debug: Base64 string length: {len(base64_pdf)} characters")

        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao exibir o PDF: {e}. Verifique se o arquivo está acessível e não corrompido. Caminho: {file_path}")

def main():
    st.set_page_config(page_title="Agente de Investimentos", page_icon="📊", layout="wide")
    st.title("📊 Agente de Análise de Investimentos PRO")

    # Inicializar o gerenciador do vector store
    vector_manager = VectorStoreManager()

    # Inicializar histórico de chat no session_state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # --- Barra Lateral (Controles) ---
    with st.sidebar:
        st.header("Controles")
        st.subheader("1. Carregar Novos Relatórios")
        uploaded_files = st.file_uploader("Selecione arquivos PDF", accept_multiple_files=True, type="pdf")
        if uploaded_files:
            count = file_handler.save_uploaded_files(uploaded_files)
            st.success(f"{count} arquivo(s) pronto(s) para processamento.")

        st.subheader("2. Processar Relatórios")
        if st.button("Integrar Novos Relatórios ao Agente"):
            new_reports = file_handler.get_new_reports_to_process()
            if not new_reports:
                st.info("Nenhum novo relatório para processar.")
            else:
                with st.spinner(f"Processando {len(new_reports)} relatório(s)..."):
                    for report_path in new_reports:
                        vector_manager.add_documents_from_file(report_path)
                        file_handler.move_processed_file(report_path)
                    st.success("Banco de dados vetorial atualizado com sucesso!")
        
        # st.info(f"Documentos no Vector Store: {vector_manager.count_documents()}")
        st.divider()

        st.subheader("3. Explorar Relatório Específico")
        processed_reports = file_handler.get_all_processed_reports()
        selected_report = st.selectbox("Selecione um relatório:", options=processed_reports, index=None, placeholder="Escolha um arquivo...")

        if selected_report:
            report_path = os.path.join(config.REPORTS_PROCESSED_DIR, selected_report)
            st.markdown("**Ações:**")
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
            col5, col6 = st.columns(2)

            if col1.button("📖 Ler PDF (Visualizador)", key=f"read_pdf_viewer_{selected_report}"):
                st.session_state.action = ('read_pdf_viewer', report_path)
            if col2.button("📄 Ler PDF (Texto Formatado)", key=f"read_pdf_text_{selected_report}"):
                st.session_state.action = ('read_pdf_text', report_path)
            if col3.button("📝 Gerar Resumo", key=f"summarize_{selected_report}"):
                st.session_state.action = ('summarize', report_path)
            if col4.button("🎧 Ouvir Resumo", key=f"listen_summary_{selected_report}"):
                st.session_state.action = ('listen_summary', report_path)
            if col5.button("🎧 Ouvir Relatório Completo", key=f"listen_full_{selected_report}", help="Pode levar vários minutos para textos longos."):
                st.session_state.action = ('listen_full', report_path)

    # --- Abas Principais (Agente e Visualizador) ---
    tab_agent, tab_explorer = st.tabs(["🗣️ Conversar com Agente", "📄 Visualizador de Relatório"])

    with tab_agent:
        st.subheader("Converse com o Agente")
        
        # Exibir mensagens anteriores do chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_question = st.chat_input("Faça sua pergunta...")
        if user_question:
            st.session_state.messages.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.spinner("O Agente está pensando..."):
                agent_executor = llm_services.setup_agent(vector_manager.get_retriever())
                try:
                    # Usar invoke para compatibilidade com memória
                    response = agent_executor.invoke({"input": user_question})["output"]
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)
                except Exception as e: 
                    error_message = f"Erro: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

    with tab_explorer:
        st.subheader("Leitura, Resumo e Áudio de Relatórios")
        if 'action' in st.session_state and st.session_state.action:
            action_type, file_path = st.session_state.action
            
            if action_type == 'read_pdf_viewer':
                st.write("Exibindo PDF:")
                display_pdf(file_path)
            
            elif action_type == 'read_pdf_text':
                st.write("Exibindo Texto do PDF:")
                with st.spinner("Extraindo texto do PDF..."):
                    full_text = file_handler.get_full_pdf_text(file_path)
                    st.text_area("Conteúdo do PDF", full_text, height=700)
            
            elif action_type == 'summarize':
                with st.spinner("Gerando resumo..."):
                    full_text = file_handler.get_full_pdf_text(file_path)
                    summarizer = llm_services.get_summarizer_chain()
                    summary = summarizer.invoke({"text_to_summarize": full_text}).content
                    st.text_area("Resumo", summary, height=600)

            elif action_type in ['listen_summary', 'listen_full']:
                text_to_convert = ""
                spinner_msg = ""
                if action_type == 'listen_summary':
                    spinner_msg = "Gerando resumo e áudio..."
                    with st.spinner(spinner_msg):
                        full_text = file_handler.get_full_pdf_text(file_path)
                        summarizer = llm_services.get_summarizer_chain()
                        text_to_convert = summarizer.invoke({"text_to_summarize": full_text}).content
                else: # listen_full
                    spinner_msg = "Gerando áudio do relatório completo... Isso pode demorar!"
                    with st.spinner(spinner_msg):
                        full_text = file_handler.get_full_pdf_text(file_path)
                        
                        # Dividir o texto em chunks menores para a API de TTS
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=4000,  # Tamanho máximo de chunk para a API de TTS
                            chunk_overlap=200
                        )
                        text_chunks = text_splitter.split_text(full_text)
                        
                        st.text_area("Texto em Áudio (Primeiro Chunk)", text_chunks[0], height=400)
                        
                        audio_files = []
                        for i, chunk in enumerate(text_chunks):
                            with st.spinner(f"Convertendo chunk {i+1}/{len(text_chunks)} para áudio..."):
                                audio_fp = llm_services.text_to_speech(chunk)
                                if audio_fp:
                                    audio_files.append(audio_fp)
                                else:
                                    st.error(f"Falha ao gerar áudio para o chunk {i+1}. Verifique o log para mais detalhes.")
                                    break # Parar se um chunk falhar
                        
                        if audio_files:
                            # Aqui você precisaria de uma forma de concatenar os áudios, 
                            # ou reproduzi-los sequencialmente. Por simplicidade, 
                            # vamos reproduzir o primeiro chunk por enquanto.
                            # Para concatenar, você precisaria de uma biblioteca como pydub.
                            st.audio(audio_files[0], format='audio/mp3', start_time=0)
                            st.info("Reproduzindo apenas o primeiro chunk. Para áudio completo, seria necessário concatenar.")
                        else:
                            st.error("Nenhum áudio foi gerado.")
            
            # Limpa a ação para evitar reexecução
            st.session_state.action = None

if __name__ == '__main__':
    main()