import os
import base64
import streamlit as st
from dotenv import load_dotenv
import config
import file_handler
from vector_store import VectorStoreManager
import llm_services
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
config.ensure_directories_exist()


def display_pdf(file_path):
    if not os.path.exists(file_path):
        st.error(f"Erro: Arquivo PDF não encontrado em: {file_path}")
        return

    try:
        
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        
        st.success(f"**Arquivo encontrado:** {file_name}")
        st.info(f"**Tamanho:** {file_size / (1024 * 1024):.1f} MB")

        
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        
        st.markdown(
            """
        <div style="text-align: center; margin: 30px 0;">
            <h3 style="color: #4CAF50;">Visualizar PDF</h3>
            <p style="color: #666;">Use o botão abaixo para baixar e abrir o PDF</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label=" BAIXAR E ABRIR PDF",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )

        
        st.markdown("""
        ### Como visualizar o PDF:
        
        **Método Recomendado (mais confiável):**
        1. **Clique em "BAIXAR E ABRIR PDF"** acima
        2. O arquivo será baixado automaticamente 
        3. Abra o arquivo baixado com seu visualizador de PDF preferido
        """)

    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")
        st.info(" Tente usar a opção 'Ler PDF (Texto Formatado)' como alternativa.")


def main():
    st.set_page_config(page_title="Agente de Análise Financeira", layout="wide")
    
    st.markdown(
        """
    <style>
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #357ABD 0%, #2E6DA4 100%) !important;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 2px solid #4A90E2 !important;
        color: #4A90E2 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #4A90E2 !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #357ABD 0%, #2E6DA4 100%) !important;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4) !important;
    }
    </style>
    
    <h1 style="font-size: 2.2rem; font-weight: 600; margin-bottom: 2rem; text-align: center; line-height: 1.2;">
        Agente de Análise de Investimentos PRO
    </h1>
    """,
        unsafe_allow_html=True,
    )

    
    vector_manager = VectorStoreManager()

    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    
    with st.sidebar:
        st.markdown("# Menu Principal")

        
        if "selected_menu" not in st.session_state:
            st.session_state.selected_menu = "Dashboard"

        
        st.markdown(
            """
        <style>
        .menu-item {
            padding: 12px 16px;
            margin: 4px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            background-color: transparent;
            border: none;
            width: 100%;
            text-align: left;
            font-size: 16px;
            color: #ffffff;
        }
        .menu-item:hover {
            background-color: rgba(255, 255, 255, 0.1);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            transform: translateY(-1px);
        }
        .menu-item.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            font-weight: 600;
        }
        .menu-item.active:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        
        menu_options = ["Dashboard", "Documentos", "Configurações", "Sistema"]

        for option in menu_options:
            active_class = "active" if st.session_state.selected_menu == option else ""

            if st.button(
                option,
                key=f"menu_{option}",
                use_container_width=True,
                type="primary"
                if st.session_state.selected_menu == option
                else "secondary",
            ):
                st.session_state.selected_menu = option
                st.rerun()

        menu_option = st.session_state.selected_menu

        st.divider()

        
        if menu_option == "Dashboard":
            st.markdown("### Ações Rápidas")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Chat", use_container_width=True):
                    st.session_state.active_tab = "chat"
                if st.button("Insights", use_container_width=True):
                    st.session_state.active_tab = "insights"

            with col2:
                if st.button("Visualizar", use_container_width=True):
                    st.session_state.active_tab = "viewer"
                if st.button("Áudios", use_container_width=True):
                    st.session_state.active_tab = "audio"

        
        elif menu_option == "Documentos":
            st.markdown("### Upload de Documentos")
            st.write("**Tipos aceitos:** PDF de FIIs, Ações, DREs, Balanços")

            uploaded_files = st.file_uploader(
                "Arrastar arquivos ou clicar para selecionar:",
                accept_multiple_files=True,
                type="pdf",
                key="doc_uploader",
            )

            if uploaded_files:
                count = file_handler.save_uploaded_files(uploaded_files)
                st.success(f"{count} arquivo(s) carregado(s)")

            st.markdown("### Processamento")
            new_reports = file_handler.get_new_reports_to_process()

            if new_reports:
                st.info(f"{len(new_reports)} arquivo(s) aguardando processamento")

                if st.button(
                    "Processar Todos", use_container_width=True, type="primary"
                ):
                    st.session_state.process_documents = True
            else:
                st.success("Todos os documentos estão processados")

        
        elif menu_option == "Configurações":
            st.markdown("### Modelo de IA")

            selected_model = st.selectbox(
                "Escolha o modelo LLM:",
                options=list(config.AVAILABLE_LLM_MODELS.keys()),
                format_func=lambda x: config.AVAILABLE_LLM_MODELS[x],
                index=0,
                help="Modelos mais avançados são mais inteligentes, mas custam mais.",
            )

            
            model_info = {
                "gpt-5": ("Máxima Qualidade", "blue"),
                "gpt-4o": ("Premium", "blue"),
                "gpt-4-turbo": ("Avançado", "blue"),
                "gpt-4": ("Clássico", "blue"),
                "gpt-3.5-turbo": ("Econômico", "green"),
                "gpt-4o-mini": ("Balanceado", "blue"),
            }

            if selected_model in model_info:
                desc, color = model_info[selected_model]
                if color == "blue":
                    st.info(f"**{desc}**")
                elif color == "green":
                    st.success(f"**{desc}**")

            st.session_state.selected_model = selected_model

        
        elif menu_option == "Sistema":
            st.markdown("### Status do Sistema")

            try:
                doc_count = vector_manager.count_documents()
                processed_docs_info = vector_manager.get_processed_documents_info()

                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Chunks Totais", doc_count)
                with col2:
                    st.metric("Documentos", len(processed_docs_info))

                if doc_count > 0:
                    st.success("Sistema RAG Ativo")

                    
                    with st.expander("Ver documentos processados"):
                        for doc_name, info in processed_docs_info.items():
                            chunk_count = info["chunk_count"]
                            st.write(f"• **{doc_name}**: {chunk_count} chunks")

                    
                    if st.button("Testar RAG", use_container_width=True):
                        test_results = vector_manager.search_similarity(
                            "investimento", k=2
                        )
                        if test_results:
                            st.success("RAG funcionando!")
                            with st.expander("Ver resultados do teste"):
                                for i, (doc, score) in enumerate(test_results):
                                    st.write(
                                        f"**Resultado {i + 1}** (Score: {score:.3f})"
                                    )
                                    st.write(
                                        f"Fonte: {doc.metadata.get('source_file', 'N/A')}"
                                    )
                                    st.write(doc.page_content[:150] + "...")
                        else:
                            st.error("RAG não respondeu")
                else:
                    st.warning("Nenhum documento processado")

            except Exception as e:
                st.error(f"Erro no sistema: {e}")

    
    if st.session_state.get("process_documents", False):
        st.session_state.process_documents = False
        new_reports = file_handler.get_new_reports_to_process()

        if new_reports:
            with st.spinner(f"Processando {len(new_reports)} documento(s)..."):
                processed_count = 0
                skipped_count = 0

                progress_bar = st.progress(0)
                for i, report_path in enumerate(new_reports):
                    progress_bar.progress((i + 1) / len(new_reports))

                    chunks_added = vector_manager.add_documents_from_file(report_path)
                    if chunks_added > 0:
                        processed_count += 1
                        file_handler.move_processed_file(report_path)
                        st.success(
                            f"{os.path.basename(report_path)} - {chunks_added} chunks processados"
                        )
                    else:
                        skipped_count += 1
                        file_handler.move_processed_file(report_path)
                        st.info(
                            f"{os.path.basename(report_path)} - Duplicado, ignorado"
                        )

                progress_bar.empty()

                if processed_count > 0:
                    st.success(
                        f"{processed_count} documento(s) processado(s) com sucesso!"
                    )
                if skipped_count > 0:
                    st.info(f"{skipped_count} documento(s) já existiam no sistema")

    
    
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "chat"

    
    active_tab = st.session_state.get("active_tab", "chat")

    
    main_container = st.container()

    
    with main_container:
        tab_col1, tab_col2, tab_col3, tab_col4 = st.columns(4)

        with tab_col1:
            if st.button(
                "Chat com IA",
                use_container_width=True,
                type="primary" if active_tab == "chat" else "secondary",
            ):
                st.session_state.active_tab = "chat"
                st.rerun()

        with tab_col2:
            if st.button(
                "Visualizar Docs",
                use_container_width=True,
                type="primary" if active_tab == "viewer" else "secondary",
            ):
                st.session_state.active_tab = "viewer"
                st.rerun()

        with tab_col3:
            if st.button(
                "Insights",
                use_container_width=True,
                type="primary" if active_tab == "insights" else "secondary",
            ):
                st.session_state.active_tab = "insights"
                st.rerun()

        with tab_col4:
            if st.button(
                "Centro de Áudio",
                use_container_width=True,
                type="primary" if active_tab == "audio" else "secondary",
            ):
                st.session_state.active_tab = "audio"
                st.rerun()

        st.divider()

    
    if active_tab == "chat":
        
        selected_model = st.session_state.get("selected_model", config.LLM_MODEL_NAME)
        st.subheader("Conversar com o Agente")
        st.info(
            f"**Modelo ativo:** {config.AVAILABLE_LLM_MODELS.get(selected_model, selected_model)}"
        )

        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_question = st.chat_input("Faça sua pergunta...")
        if user_question:
            st.session_state.messages.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.spinner("O Agente está pensando..."):
                
                selected_model = st.session_state.get(
                    "selected_model", config.LLM_MODEL_NAME
                )
                agent_executor = llm_services.setup_agent(
                    vector_manager.get_retriever(), model_name=selected_model
                )
                try:
                    
                    response = agent_executor.invoke({"input": user_question})["output"]
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                    with st.chat_message("assistant"):
                        st.markdown(response)
                except Exception as e:
                    error_message = f"Erro: {e}"
                    st.error(error_message)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_message}
                    )

    
    elif active_tab == "viewer":
        st.subheader("Visualizador de Documentos Financeiros")
        st.info(
            "**Dica**: Agora as ações não se interrompem! Use outras tabs enquanto processa."
        )

        
        processed_reports = file_handler.get_all_processed_reports()

        if not processed_reports:
            st.warning("Nenhum documento processado encontrado.")
            st.info(
                "Vá para o menu **Documentos** para carregar e processar arquivos primeiro."
            )
        else:
            col1, col2 = st.columns([3, 1])

            with col1:
                selected_report = st.selectbox(
                    "Escolha um documento para visualizar:",
                    options=processed_reports,
                    index=None,
                    placeholder="Selecione um arquivo...",
                )

            with col2:
                st.metric("Total", len(processed_reports))

            if selected_report:
                st.success(f"**Selecionado:** {selected_report}")
                report_path = os.path.join(
                    config.REPORTS_PROCESSED_DIR, selected_report
                )

                
                st.markdown("### Ações Disponíveis")

                action_col1, action_col2 = st.columns(2)

                with action_col1:
                    st.markdown("**Leitura e Visualização**")
                    
                    current_action = st.session_state.get('action', None)
                    current_action_type = current_action[0] if current_action else None
                    
                    if st.button(
                        "Ver PDF Original", 
                        use_container_width=True, 
                        key="view_pdf",
                        type="primary" if current_action_type == "read_pdf_viewer" else "secondary"
                    ):
                        st.session_state.action = ("read_pdf_viewer", report_path)
                        st.rerun()

                    if st.button(
                        "Extrair Texto Completo",
                        use_container_width=True,
                        key="extract_text",
                        type="primary" if current_action_type == "read_pdf_text" else "secondary"
                    ):
                        st.session_state.action = ("read_pdf_text", report_path)
                        st.rerun()

                    if st.button(
                        "Gerar Resumo com IA",
                        use_container_width=True,
                        key="generate_summary",
                        type="primary" if current_action_type == "summarize" else "secondary"
                    ):
                        st.session_state.action = ("summarize", report_path)
                        st.rerun()

                with action_col2:
                    st.markdown("**Áudio com IA**")
                    
                    if st.button(
                        "Ouvir Resumo (IA)",
                        use_container_width=True,
                        key="listen_summary",
                        type="primary" if current_action_type == "listen_summary" else "secondary"
                    ):
                        st.session_state.action = ("listen_summary", report_path)
                        st.rerun()

                    if st.button(
                        "Ouvir Relatório Completo (IA)",
                        use_container_width=True,
                        key="listen_full",
                        type="primary" if current_action_type == "listen_full" else "secondary"
                    ):
                        st.session_state.action = ("listen_full", report_path)
                        st.rerun()

                    st.caption(
                        "Nota: Áudio completo pode levar vários minutos para textos longos"
                    )

        if "action" in st.session_state and st.session_state.action:
            action_type, file_path = st.session_state.action

            if action_type == "read_pdf_viewer":
                st.write("Exibindo PDF:")
                display_pdf(file_path)

            elif action_type == "read_pdf_text":
                
                file_name = os.path.basename(file_path)

                st.subheader(f" Texto Extraído: {file_name}")

                with st.spinner("Extraindo texto do PDF..."):
                    try:
                        full_text = file_handler.get_full_pdf_text(file_path)

                        
                        word_count = len(full_text.split())
                        char_count = len(full_text)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(" Palavras", f"{word_count:,}")
                        with col2:
                            st.metric(" Caracteres", f"{char_count:,}")
                        with col3:
                            st.metric(" Páginas (aprox.)", max(1, word_count // 250))

                        
                        st.download_button(
                            label=" Baixar Texto (.txt)",
                            data=full_text,
                            file_name=f"texto_{file_name.replace('.pdf', '')}.txt",
                            mime="text/plain",
                        )

                        
                        view_option = st.radio(
                            "Opções de visualização:",
                            [
                                " Texto Completo",
                                " Primeiras 500 palavras",
                                " Buscar no texto",
                            ],
                        )

                        if view_option == " Texto Completo":
                            st.text_area("Conteúdo do PDF", full_text, height=700)

                        elif view_option == " Primeiras 500 palavras":
                            words = full_text.split()
                            preview_text = " ".join(words[:500])
                            if len(words) > 500:
                                preview_text += (
                                    "\n\n[... restante do texto omitido ...]"
                                )
                            st.text_area(
                                "Prévia do PDF (500 palavras)", preview_text, height=400
                            )

                        elif view_option == " Buscar no texto":
                            search_term = st.text_input("Digite o termo para buscar:")
                            if search_term:
                                
                                import re

                                matches = re.finditer(
                                    re.escape(search_term), full_text, re.IGNORECASE
                                )
                                match_positions = [
                                    (m.start(), m.end()) for m in matches
                                ]

                                if match_positions:
                                    st.success(
                                        f"Encontradas {len(match_positions)} ocorrências de '{search_term}'"
                                    )

                                    
                                    for i, (start, end) in enumerate(
                                        match_positions[:5]
                                    ):
                                        context_start = max(0, start - 100)
                                        context_end = min(len(full_text), end + 100)
                                        context = full_text[context_start:context_end]

                                        
                                        highlighted = context.replace(
                                            search_term, f"**{search_term}**"
                                        )

                                        st.write(f"**Ocorrência {i + 1}:**")
                                        st.write(f"...{highlighted}...")
                                        st.write("---")
                                else:
                                    st.warning(
                                        f"Termo '{search_term}' não encontrado no texto."
                                    )

                    except Exception as e:
                        st.error(f"Erro ao extrair texto do PDF: {e}")
                        st.info(
                            " Tente a opção 'Ler PDF (Visualizador)' como alternativa."
                        )

            elif action_type == "summarize":
                with st.spinner("Gerando resumo..."):
                    full_text = file_handler.get_full_pdf_text(file_path)
                    summarizer = llm_services.get_summarizer_chain()
                    summary = summarizer.invoke(
                        {"text_to_summarize": full_text}
                    ).content
                    st.text_area("Resumo", summary, height=600)

            elif action_type in ["listen_summary", "listen_full"]:
                
                file_name = os.path.basename(file_path)

                if action_type == "listen_summary":
                    with st.spinner("Gerando resumo e áudio..."):
                        
                        full_text = file_handler.get_full_pdf_text(file_path)
                        summarizer = llm_services.get_summarizer_chain()
                        summary_text = summarizer.invoke(
                            {"text_to_summarize": full_text}
                        ).content

                        
                        st.subheader(" Resumo do Relatório")
                        st.text_area("Resumo", summary_text, height=300)

                        
                        with st.spinner("Convertendo resumo para áudio..."):
                            audio_content = llm_services.text_to_speech(summary_text)

                            if audio_content:
                                st.subheader(" Áudio do Resumo")
                                st.audio(audio_content, format="audio/mp3")

                                
                                st.download_button(
                                    label=" Baixar Áudio do Resumo",
                                    data=audio_content,
                                    file_name=f"resumo_{file_name.replace('.pdf', '')}.mp3",
                                    mime="audio/mp3",
                                )
                            else:
                                st.error("Falha ao gerar áudio do resumo.")

                else:  
                    with st.spinner(
                        "Gerando áudio do relatório completo... Isso pode demorar!"
                    ):
                        full_text = file_handler.get_full_pdf_text(file_path)

                        
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=4000,  
                            chunk_overlap=200,
                        )
                        text_chunks = text_splitter.split_text(full_text)

                        st.info(
                            f"Processando {len(text_chunks)} partes do relatório..."
                        )

                        
                        progress_bar = st.progress(0)
                        progress_text = st.empty()

                        audio_contents = []
                        for i, chunk in enumerate(text_chunks):
                            progress_text.text(
                                f"Convertendo parte {i + 1}/{len(text_chunks)} para áudio..."
                            )
                            progress_bar.progress((i + 1) / len(text_chunks))

                            audio_content = llm_services.text_to_speech(chunk)
                            if audio_content:
                                audio_contents.append(audio_content)
                            else:
                                st.error(f"Falha ao gerar áudio para a parte {i + 1}.")
                                break

                        
                        progress_bar.empty()
                        progress_text.empty()

                        if audio_contents:
                            st.subheader(" Áudio do Relatório Completo")

                            
                            with st.spinner("Concatenando arquivos de áudio..."):
                                final_audio = llm_services.concatenate_audio_files(
                                    audio_contents
                                )

                            if final_audio:
                                st.success(
                                    f"Áudio completo gerado com {len(audio_contents)} partes!"
                                )
                                st.audio(final_audio, format="audio/mp3")

                                
                                st.download_button(
                                    label=" Baixar Áudio Completo",
                                    data=final_audio,
                                    file_name=f"audio_completo_{file_name.replace('.pdf', '')}.mp3",
                                    mime="audio/mp3",
                                )
                            else:
                                st.warning(
                                    "Concatenação não disponível. Reproduzindo primeira parte:"
                                )
                                st.audio(audio_contents[0], format="audio/mp3")

                                
                                st.subheader(" Download das Partes Individuais")
                                for i, audio_content in enumerate(audio_contents):
                                    st.download_button(
                                        label=f"Parte {i + 1}/{len(audio_contents)}",
                                        data=audio_content,
                                        file_name=f"parte_{i + 1}_{file_name.replace('.pdf', '')}.mp3",
                                        mime="audio/mp3",
                                        key=f"download_part_{i}",
                                    )
                        else:
                            st.error("Nenhum áudio foi gerado.")


    
    elif active_tab == "insights":
        
        selected_model = st.session_state.get("selected_model", config.LLM_MODEL_NAME)
        st.subheader("Insights Automáticos dos Investimentos")
        st.info(
            f"**Modelo ativo:** {config.AVAILABLE_LLM_MODELS.get(selected_model, selected_model)}"
        )

        
        doc_count = vector_manager.count_documents()
        if doc_count == 0:
            st.warning(
                "Nenhum documento financeiro foi processado ainda. Faça upload e processe documentos primeiro."
            )
            st.info("Vá para a barra lateral e:")
            st.write("1. Carregar novos documentos (FIIs, Ações, etc.)")
            st.write("2. Processar documentos")
            st.write("3. Volte aqui para ver os insights!")
            return

        
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Resumo Executivo", use_container_width=True):
                st.session_state.insight_action = "market_summary"

        with col2:
            if st.button("Métricas Chave", use_container_width=True):
                st.session_state.insight_action = "key_metrics"

        with col3:
            if st.button("Análise Detalhada", use_container_width=True):
                st.session_state.insight_action = "detailed_insights"

        
        if "insight_action" in st.session_state and st.session_state.insight_action:
            action = st.session_state.insight_action
            retriever = vector_manager.get_retriever(k=6)  

            if action == "market_summary":
                st.subheader(" Resumo Executivo do Mercado")
                with st.spinner("Gerando resumo executivo..."):
                    selected_model = st.session_state.get(
                        "selected_model", config.LLM_MODEL_NAME
                    )
                    summary = llm_services.generate_market_summary(
                        retriever, model_name=selected_model
                    )
                    st.markdown(summary)

                    
                    st.download_button(
                        label=" Baixar Resumo Executivo",
                        data=summary,
                        file_name="resumo_executivo_fii.txt",
                        mime="text/plain",
                    )

            elif action == "key_metrics":
                st.subheader(" Métricas Chave Extraídas")
                with st.spinner("Extraindo métricas dos relatórios..."):
                    selected_model = st.session_state.get(
                        "selected_model", config.LLM_MODEL_NAME
                    )
                    metrics = llm_services.extract_key_metrics(
                        retriever, model_name=selected_model
                    )

                    if "error" in metrics:
                        st.error(metrics["error"])
                    else:
                        st.markdown(
                            metrics.get("metrics", "Nenhuma métrica encontrada")
                        )

                        
                        if metrics.get("metrics"):
                            st.download_button(
                                label=" Baixar Métricas",
                                data=metrics["metrics"],
                                file_name="metricas_chave_fii.txt",
                                mime="text/plain",
                            )

            elif action == "detailed_insights":
                st.subheader(" Análise Detalhada dos Relatórios")
                with st.spinner(
                    "Gerando insights detalhados... Isso pode levar alguns minutos."
                ):
                    selected_model = st.session_state.get(
                        "selected_model", config.LLM_MODEL_NAME
                    )
                    insights = llm_services.generate_insights_from_documents(
                        retriever, model_name=selected_model
                    )

                    
                    insight_tabs = st.tabs(
                        [
                            " Ativos Principais",
                            " Performance",
                            " Setores & Segmentos",
                            " Recomendações",
                            " Riscos & Oportunidades",
                            " Indicadores",
                        ]
                    )

                    queries = list(insights.keys())

                    for i, tab in enumerate(insight_tabs):
                        with tab:
                            if i < len(queries):
                                query = queries[i]
                                insight = insights[query]
                                st.markdown(f"**Pergunta:** {query}")
                                st.markdown("---")
                                st.markdown(insight)

                    
                    all_insights_text = "\n\n".join(
                        [
                            f"PERGUNTA: {q}\n\nRESPOSTA: {a}\n{'=' * 50}"
                            for q, a in insights.items()
                        ]
                    )
                    st.download_button(
                        label=" Baixar Todos os Insights",
                        data=all_insights_text,
                        file_name="insights_completos_fii.txt",
                        mime="text/plain",
                    )

            
            st.session_state.insight_action = None

        
        with st.expander(" Como funcionam os Insights"):
            st.write("""
            **Os insights são gerados automaticamente usando:**
            
            1. **RAG (Retrieval-Augmented Generation)**: Busca informações relevantes nos documentos
            2. **IA Generativa**: Analisa e sintetiza as informações encontradas  
            3. **Prompts Especializados**: Perguntas específicas para extrair insights valiosos
            
            **Tipos de Insights Disponíveis:**
            -  **Resumo Executivo**: Visão geral do mercado e recomendações
            -  **Métricas Chave**: Valores, rendimentos e dados numéricos
            -  **Análise Detalhada**: Insights segmentados por categoria
            
            **Dica**: Quanto mais documentos processados, mais ricos serão os insights!
            """)

    
    elif active_tab == "audio":
        st.subheader("Centro de Áudio com IA")

        
        processed_reports = file_handler.get_all_processed_reports()

        if not processed_reports:
            st.warning("Nenhum documento processado encontrado.")
            st.info(
                "Vá para **Documentos** no menu para carregar e processar arquivos primeiro."
            )
        else:
            
            col1, col2 = st.columns([2, 1])

            with col1:
                selected_report = st.selectbox(
                    "Selecionar documento:",
                    options=processed_reports,
                    index=None,
                    placeholder="Selecione um arquivo para gerar áudio...",
                    label_visibility="collapsed"
                )

            with col2:
                st.metric("Docs Disponíveis", len(processed_reports))

            if selected_report:
                st.success(f"**Documento selecionado:** {selected_report}")
                report_path = os.path.join(
                    config.REPORTS_PROCESSED_DIR, selected_report
                )

                
                st.markdown("### Opções de Áudio")

                audio_col1, audio_col2 = st.columns(2)

                with audio_col1:
                    if st.button(
                        " Gerar Áudio do Resumo",
                        use_container_width=True,
                        type="primary",
                        key="audio_summary",
                    ):
                        if f"audio_summary_{selected_report}" not in st.session_state:
                            st.session_state[f"audio_summary_{selected_report}"] = (
                                "processing"
                            )
                            st.rerun()

                    
                    if f"audio_summary_{selected_report}" in st.session_state:
                        status = st.session_state[f"audio_summary_{selected_report}"]
                        if status == "processing":
                            with st.spinner(" Gerando áudio do resumo..."):
                                try:
                                    selected_model = st.session_state.get(
                                        "selected_model", config.LLM_MODEL_NAME
                                    )
                                    full_text = file_handler.get_full_pdf_text(report_path)
                                    summarizer = llm_services.get_summarizer_chain(model_name=selected_model)
                                    summary = summarizer.invoke({"text_to_summarize": full_text}).content
                                    audio_content = llm_services.text_to_speech(summary)

                                    if audio_content:
                                        st.session_state[
                                            f"audio_summary_{selected_report}"
                                        ] = audio_content
                                        st.success(" Áudio do resumo gerado!")
                                        st.rerun()
                                    else:
                                        st.error(" Erro ao gerar áudio")
                                        del st.session_state[
                                            f"audio_summary_{selected_report}"
                                        ]
                                except Exception as e:
                                    st.error(f" Erro: {e}")
                                    del st.session_state[
                                        f"audio_summary_{selected_report}"
                                    ]

                        elif isinstance(status, bytes):
                            st.audio(status, format="audio/mp3")
                            if st.button(" Limpar", key="clear_summary"):
                                del st.session_state[f"audio_summary_{selected_report}"]
                                st.rerun()

                with audio_col2:
                    if st.button(
                        " Gerar Áudio Completo",
                        use_container_width=True,
                        type="secondary",
                        key="audio_full",
                    ):
                        if f"audio_full_{selected_report}" not in st.session_state:
                            st.session_state[f"audio_full_{selected_report}"] = (
                                "processing"
                            )
                            st.rerun()

                    
                    if f"audio_full_{selected_report}" in st.session_state:
                        status = st.session_state[f"audio_full_{selected_report}"]
                        if status == "processing":
                            with st.spinner(
                                " Gerando áudio completo... (pode demorar)"
                            ):
                                try:
                                    full_text = file_handler.get_full_pdf_text(
                                        report_path
                                    )

                                    
                                    text_splitter = RecursiveCharacterTextSplitter(
                                        chunk_size=3000,
                                        chunk_overlap=200,
                                        separators=["\n\n", "\n", ". ", " "],
                                    )
                                    text_chunks = text_splitter.split_text(full_text)

                                    st.info(
                                        f" Processando {len(text_chunks)} partes..."
                                    )

                                    audio_contents = []
                                    progress_bar = st.progress(0)

                                    for i, chunk in enumerate(
                                        text_chunks[:10]
                                    ):  
                                        chunk_audio = llm_services.text_to_speech(chunk)
                                        if chunk_audio:
                                            audio_contents.append(chunk_audio)
                                        progress_bar.progress(
                                            (i + 1) / min(len(text_chunks), 10)
                                        )

                                    if audio_contents:
                                        
                                        combined_audio = audio_contents[0]
                                        st.session_state[
                                            f"audio_full_{selected_report}"
                                        ] = combined_audio
                                        st.success(
                                            f" Áudio gerado! ({len(audio_contents)} partes)"
                                        )
                                        st.rerun()
                                    else:
                                        st.error(" Erro ao gerar áudio")
                                        del st.session_state[
                                            f"audio_full_{selected_report}"
                                        ]
                                except Exception as e:
                                    st.error(f" Erro: {e}")
                                    del st.session_state[
                                        f"audio_full_{selected_report}"
                                    ]

                        elif isinstance(status, bytes):
                            st.audio(status, format="audio/mp3")
                            if st.button(" Limpar", key="clear_full"):
                                del st.session_state[f"audio_full_{selected_report}"]
                                st.rerun()


if __name__ == "__main__":
    main()
