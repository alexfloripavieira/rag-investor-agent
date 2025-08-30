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
    """Exibe informações do PDF e oferece opções de visualização."""
    if not os.path.exists(file_path):
        st.error(f"Erro: Arquivo PDF não encontrado em: {file_path}")
        return

    try:
        # Obter informações do arquivo
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        # Mostrar informações do arquivo
        st.success(f"📄 **Arquivo encontrado:** {file_name}")
        st.info(f"📊 **Tamanho:** {file_size / (1024*1024):.1f} MB")
        
        # Ler o arquivo
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Botão de download principal (mais confiável)
        st.markdown("""
        <div style="text-align: center; margin: 30px 0;">
            <h3 style="color: #4CAF50;">📖 Visualizar PDF</h3>
            <p style="color: #666;">Use o botão abaixo para baixar e abrir o PDF</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão principal de download estilizado
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 BAIXAR E ABRIR PDF",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        
        # Instruções melhoradas
        st.markdown("""
        ### 📋 Como visualizar o PDF:
        
        **Método Recomendado (mais confiável):**
        1. **Clique em "BAIXAR E ABRIR PDF"** acima
        2. O arquivo será baixado automaticamente 
        3. Abra o arquivo baixado com seu visualizador de PDF preferido
        
        **Métodos Alternativos:**
        """)
        
        # Métodos alternativos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🌐 Tentar abrir no navegador:**")
            # Criar data URL para teste
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            data_url = f"data:application/pdf;base64,{base64_pdf}"
            
            if st.button("🔗 Tentar abrir no navegador", use_container_width=True):
                st.markdown(f"""
                <script>
                    window.open('{data_url}', '_blank');
                </script>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <a href="{data_url}" target="_blank" 
                   style="display: block; 
                          text-align: center; 
                          background-color: #0066cc; 
                          color: white;
                          padding: 8px;
                          text-decoration: none;
                          border-radius: 4px;
                          margin-top: 8px;">
                    Se não abriu, clique aqui
                </a>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**📄 Ver como texto:**")
            if st.button("📖 Ler como texto formatado", use_container_width=True):
                st.session_state.action = ('read_pdf_text', file_path)
                st.rerun()
        
        # Informações adicionais
        st.markdown("""
        ---
        ### ℹ️ Informações importantes:
        
        - **Navegadores modernos** podem bloquear PDFs incorporados por segurança
        - **Baixar o arquivo** é sempre a opção mais confiável
        - **Visualizadores recomendados:** Adobe Reader, navegador padrão, visualizador do sistema
        """)
        
        # Mostrar prévia do iframe como última opção
        with st.expander("🔧 Opções Avançadas - Tentar visualização incorporada"):
            st.warning("⚠️ Esta opção pode não funcionar em todos os navegadores")
            
            if st.button("Tentar visualização incorporada"):
                try:
                    # Tentar iframe simples
                    st.components.v1.html(f"""
                    <iframe src="{data_url}" 
                            width="100%" 
                            height="600px"
                            style="border: 1px solid #ddd;">
                        <p>Seu navegador não suporta visualização de PDF incorporado.</p>
                    </iframe>
                    """, height=620)
                except Exception as e:
                    st.error(f"Visualização incorporada falhou: {e}")
                    
    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")
        st.info("💡 Tente usar a opção 'Ler PDF (Texto Formatado)' como alternativa.")

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
        
        # Seletor de Modelo LLM
        st.subheader("🤖 Configuração do Modelo")
        selected_model = st.selectbox(
            "Escolha o modelo LLM:",
            options=list(config.AVAILABLE_LLM_MODELS.keys()),
            format_func=lambda x: config.AVAILABLE_LLM_MODELS[x],
            index=0,  # GPT-4o-mini como padrão
            help="Modelos mais avançados são mais inteligentes, mas consomem mais tokens."
        )
        
        # Mostrar informações sobre o modelo selecionado
        if selected_model == "gpt-5":
            st.info("🎯 **Modelo Mais Avançado** - Máxima qualidade, maior custo")
        elif selected_model in ["gpt-4o", "gpt-4-turbo", "gpt-4"]:
            st.info("💰 **Modelo Premium** - Maior qualidade, maior custo")
        elif selected_model == "gpt-3.5-turbo":
            st.info("🚀 **Modelo Econômico** - Rápido e barato")
        else:
            st.info("⚡ **Modelo Balanceado** - Ótima relação qualidade/custo")
        
        # Armazenar o modelo selecionado no session state
        st.session_state.selected_model = selected_model
        
        st.subheader("1. Carregar Novos Relatórios")
        uploaded_files = st.file_uploader("Selecione arquivos PDF", accept_multiple_files=True, type="pdf")
        if uploaded_files:
            count = file_handler.save_uploaded_files(uploaded_files)
            st.success(f"{count} arquivo(s) pronto(s) para processamento.")

        st.subheader("2. Processar Relatórios")
        
        # Mostrar arquivos pendentes com status
        new_reports = file_handler.get_new_reports_to_process()
        if new_reports:
            st.write("**Arquivos pendentes:**")
            for report_path in new_reports:
                file_name = os.path.basename(report_path)
                is_duplicate = vector_manager.is_document_already_processed(report_path)
                if is_duplicate:
                    st.warning(f"🚫 {file_name} - JÁ PROCESSADO")
                else:
                    st.info(f"📄 {file_name} - Novo")
        
        if st.button("Integrar Novos Relatórios ao Agente"):
            if not new_reports:
                st.info("Nenhum novo relatório para processar.")
            else:
                with st.spinner(f"Processando {len(new_reports)} relatório(s)..."):
                    processed_count = 0
                    skipped_count = 0
                    
                    for report_path in new_reports:
                        chunks_added = vector_manager.add_documents_from_file(report_path)
                        if chunks_added > 0:
                            processed_count += 1
                            file_handler.move_processed_file(report_path)
                            st.success(f"✅ {os.path.basename(report_path)} - {chunks_added} chunks adicionados")
                        else:
                            skipped_count += 1
                            # Ainda mover arquivo mesmo se foi pulado (já processado)
                            file_handler.move_processed_file(report_path)
                            st.info(f"⏭️ {os.path.basename(report_path)} - Pulado (duplicata)")
                    
                    if processed_count > 0:
                        st.success(f"🎉 {processed_count} arquivo(s) processado(s) com sucesso!")
                    if skipped_count > 0:
                        st.info(f"⏭️ {skipped_count} arquivo(s) pulado(s) (já processados)")
        
        # Mostrar informações do Vector Store
        with st.expander("📊 Informações do Banco de Dados Vetorial (RAG)"):
            try:
                doc_count = vector_manager.count_documents()
                collection_info = vector_manager.get_collection_info()
                processed_docs_info = vector_manager.get_processed_documents_info()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📄 Chunks totais", doc_count)
                with col2:
                    st.metric("📁 Documentos únicos", len(processed_docs_info))
                with col3:
                    st.metric("🧠 Modelo Embeddings", config.EMBEDDING_MODEL_NAME)
                
                if doc_count > 0:
                    st.success("✅ Vector Store funcionando corretamente!")
                    
                    # Mostrar documentos processados
                    if processed_docs_info:
                        st.write("**📋 Documentos processados:**")
                        for doc_name, info in processed_docs_info.items():
                            chunk_count = info['chunk_count']
                            total_chunks = info['total_chunks']
                            st.write(f"• **{doc_name}**: {chunk_count} chunks")
                    
                    # Teste de busca simples
                    if st.button("🔍 Testar busca no RAG"):
                        test_query = "investimento"
                        results = vector_manager.search_similarity(test_query, k=2)
                        if results:
                            st.write(f"**Teste de busca por '{test_query}':**")
                            for i, (doc, score) in enumerate(results):
                                st.write(f"**Resultado {i+1}** (Score: {score:.3f})")
                                st.write(f"Fonte: {doc.metadata.get('source_file', 'N/A')}")
                                st.write(f"Conteúdo: {doc.page_content[:200]}...")
                                st.write("---")
                else:
                    st.warning("⚠️ Nenhum documento foi processado ainda.")
                    
            except Exception as e:
                st.error(f"❌ Erro ao acessar vector store: {e}")
        
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

    # --- Abas Principais ---
    tab_agent, tab_explorer, tab_insights = st.tabs([
        "🗣️ Conversar com Agente", 
        "📄 Visualizador de Relatório", 
        "💡 Insights dos Relatórios"
    ])

    with tab_agent:
        # Mostrar modelo ativo
        selected_model = st.session_state.get('selected_model', config.LLM_MODEL_NAME)
        st.subheader("🗣️ Conversar com o Agente")
        st.info(f"🤖 **Modelo ativo:** {config.AVAILABLE_LLM_MODELS.get(selected_model, selected_model)}")
        
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
                # Usar o modelo selecionado pelo usuário
                selected_model = st.session_state.get('selected_model', config.LLM_MODEL_NAME)
                agent_executor = llm_services.setup_agent(vector_manager.get_retriever(), model_name=selected_model)
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
                # Extrair nome do arquivo
                file_name = os.path.basename(file_path)
                
                st.subheader(f"📄 Texto Extraído: {file_name}")
                
                with st.spinner("Extraindo texto do PDF..."):
                    try:
                        full_text = file_handler.get_full_pdf_text(file_path)
                        
                        # Mostrar estatísticas do texto
                        word_count = len(full_text.split())
                        char_count = len(full_text)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📊 Palavras", f"{word_count:,}")
                        with col2:
                            st.metric("🔤 Caracteres", f"{char_count:,}")
                        with col3:
                            st.metric("📑 Páginas (aprox.)", max(1, word_count // 250))
                        
                        # Botão de download do texto
                        st.download_button(
                            label="📥 Baixar Texto (.txt)",
                            data=full_text,
                            file_name=f"texto_{file_name.replace('.pdf', '')}.txt",
                            mime="text/plain"
                        )
                        
                        # Opções de visualização
                        view_option = st.radio(
                            "Opções de visualização:",
                            ["📖 Texto Completo", "🔍 Primeiras 500 palavras", "🎯 Buscar no texto"]
                        )
                        
                        if view_option == "📖 Texto Completo":
                            st.text_area("Conteúdo do PDF", full_text, height=700)
                            
                        elif view_option == "🔍 Primeiras 500 palavras":
                            words = full_text.split()
                            preview_text = " ".join(words[:500])
                            if len(words) > 500:
                                preview_text += "\n\n[... restante do texto omitido ...]"
                            st.text_area("Prévia do PDF (500 palavras)", preview_text, height=400)
                            
                        elif view_option == "🎯 Buscar no texto":
                            search_term = st.text_input("Digite o termo para buscar:")
                            if search_term:
                                # Buscar termo no texto (case insensitive)
                                import re
                                matches = re.finditer(re.escape(search_term), full_text, re.IGNORECASE)
                                match_positions = [(m.start(), m.end()) for m in matches]
                                
                                if match_positions:
                                    st.success(f"Encontradas {len(match_positions)} ocorrências de '{search_term}'")
                                    
                                    # Mostrar contexto das primeiras 5 ocorrências
                                    for i, (start, end) in enumerate(match_positions[:5]):
                                        context_start = max(0, start - 100)
                                        context_end = min(len(full_text), end + 100)
                                        context = full_text[context_start:context_end]
                                        
                                        # Destacar o termo encontrado
                                        highlighted = context.replace(
                                            search_term, f"**{search_term}**"
                                        )
                                        
                                        st.write(f"**Ocorrência {i+1}:**")
                                        st.write(f"...{highlighted}...")
                                        st.write("---")
                                else:
                                    st.warning(f"Termo '{search_term}' não encontrado no texto.")
                                    
                    except Exception as e:
                        st.error(f"Erro ao extrair texto do PDF: {e}")
                        st.info("💡 Tente a opção 'Ler PDF (Visualizador)' como alternativa.")
            
            elif action_type == 'summarize':
                with st.spinner("Gerando resumo..."):
                    full_text = file_handler.get_full_pdf_text(file_path)
                    summarizer = llm_services.get_summarizer_chain()
                    summary = summarizer.invoke({"text_to_summarize": full_text}).content
                    st.text_area("Resumo", summary, height=600)

            elif action_type in ['listen_summary', 'listen_full']:
                # Extrair nome do arquivo a partir do caminho
                file_name = os.path.basename(file_path)
                
                if action_type == 'listen_summary':
                    with st.spinner("Gerando resumo e áudio..."):
                        # Gerar resumo
                        full_text = file_handler.get_full_pdf_text(file_path)
                        summarizer = llm_services.get_summarizer_chain()
                        summary_text = summarizer.invoke({"text_to_summarize": full_text}).content
                        
                        # Mostrar resumo
                        st.subheader("📝 Resumo do Relatório")
                        st.text_area("Resumo", summary_text, height=300)
                        
                        # Converter resumo para áudio
                        with st.spinner("Convertendo resumo para áudio..."):
                            audio_content = llm_services.text_to_speech(summary_text)
                            
                            if audio_content:
                                st.subheader("🎧 Áudio do Resumo")
                                st.audio(audio_content, format='audio/mp3')
                                
                                # Botão de download do áudio
                                st.download_button(
                                    label="📥 Baixar Áudio do Resumo",
                                    data=audio_content,
                                    file_name=f"resumo_{file_name.replace('.pdf', '')}.mp3",
                                    mime="audio/mp3"
                                )
                            else:
                                st.error("Falha ao gerar áudio do resumo.")
                
                else: # listen_full
                    with st.spinner("Gerando áudio do relatório completo... Isso pode demorar!"):
                        full_text = file_handler.get_full_pdf_text(file_path)
                        
                        # Dividir o texto em chunks menores para a API de TTS
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=4000,  # Tamanho máximo de chunk para a API de TTS
                            chunk_overlap=200
                        )
                        text_chunks = text_splitter.split_text(full_text)
                        
                        st.info(f"Processando {len(text_chunks)} partes do relatório...")
                        
                        # Criar progress bar
                        progress_bar = st.progress(0)
                        progress_text = st.empty()
                        
                        audio_contents = []
                        for i, chunk in enumerate(text_chunks):
                            progress_text.text(f"Convertendo parte {i+1}/{len(text_chunks)} para áudio...")
                            progress_bar.progress((i + 1) / len(text_chunks))
                            
                            audio_content = llm_services.text_to_speech(chunk)
                            if audio_content:
                                audio_contents.append(audio_content)
                            else:
                                st.error(f"Falha ao gerar áudio para a parte {i+1}.")
                                break
                        
                        # Limpar progress indicators
                        progress_bar.empty()
                        progress_text.empty()
                        
                        if audio_contents:
                            st.subheader("🎧 Áudio do Relatório Completo")
                            
                            # Tentar concatenar áudios
                            with st.spinner("Concatenando arquivos de áudio..."):
                                final_audio = llm_services.concatenate_audio_files(audio_contents)
                            
                            if final_audio:
                                st.success(f"Áudio completo gerado com {len(audio_contents)} partes!")
                                st.audio(final_audio, format='audio/mp3')
                                
                                # Botão de download
                                st.download_button(
                                    label="📥 Baixar Áudio Completo",
                                    data=final_audio,
                                    file_name=f"audio_completo_{file_name.replace('.pdf', '')}.mp3",
                                    mime="audio/mp3"
                                )
                            else:
                                st.warning("Concatenação não disponível. Reproduzindo primeira parte:")
                                st.audio(audio_contents[0], format='audio/mp3')
                                
                                # Opção para baixar partes individuais
                                st.subheader("📥 Download das Partes Individuais")
                                for i, audio_content in enumerate(audio_contents):
                                    st.download_button(
                                        label=f"Parte {i+1}/{len(audio_contents)}",
                                        data=audio_content,
                                        file_name=f"parte_{i+1}_{file_name.replace('.pdf', '')}.mp3",
                                        mime="audio/mp3",
                                        key=f"download_part_{i}"
                                    )
                        else:
                            st.error("Nenhum áudio foi gerado.")
            
            # Limpa a ação para evitar reexecução
            st.session_state.action = None

    with tab_insights:
        # Mostrar modelo ativo
        selected_model = st.session_state.get('selected_model', config.LLM_MODEL_NAME)
        st.subheader("💡 Insights Automáticos dos Relatórios")
        st.info(f"🤖 **Modelo ativo:** {config.AVAILABLE_LLM_MODELS.get(selected_model, selected_model)}")
        
        # Verificar se há documentos processados
        doc_count = vector_manager.count_documents()
        if doc_count == 0:
            st.warning("⚠️ Nenhum relatório foi processado ainda. Faça upload e processe documentos primeiro.")
            st.info("📝 Vá para a barra lateral e:")
            st.write("1. Carregar novos relatórios")
            st.write("2. Processar relatórios")
            st.write("3. Volte aqui para ver os insights!")
            return
        
        st.info(f"📊 Analisando {doc_count} chunks de dados dos relatórios processados...")
        
        # Botões para diferentes tipos de insights
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Resumo Executivo", use_container_width=True):
                st.session_state.insight_action = "market_summary"
        
        with col2:
            if st.button("📊 Métricas Chave", use_container_width=True):
                st.session_state.insight_action = "key_metrics"
        
        with col3:
            if st.button("🔍 Análise Detalhada", use_container_width=True):
                st.session_state.insight_action = "detailed_insights"
        
        # Processar ações de insights
        if 'insight_action' in st.session_state and st.session_state.insight_action:
            action = st.session_state.insight_action
            retriever = vector_manager.get_retriever(k=6)  # Mais contexto para insights
            
            if action == "market_summary":
                st.subheader("📋 Resumo Executivo do Mercado")
                with st.spinner("Gerando resumo executivo..."):
                    selected_model = st.session_state.get('selected_model', config.LLM_MODEL_NAME)
                    summary = llm_services.generate_market_summary(retriever, model_name=selected_model)
                    st.markdown(summary)
                    
                    # Botão para download
                    st.download_button(
                        label="📥 Baixar Resumo Executivo",
                        data=summary,
                        file_name="resumo_executivo_fii.txt",
                        mime="text/plain"
                    )
            
            elif action == "key_metrics":
                st.subheader("📊 Métricas Chave Extraídas")
                with st.spinner("Extraindo métricas dos relatórios..."):
                    selected_model = st.session_state.get('selected_model', config.LLM_MODEL_NAME)
                    metrics = llm_services.extract_key_metrics(retriever, model_name=selected_model)
                    
                    if "error" in metrics:
                        st.error(metrics["error"])
                    else:
                        st.markdown(metrics.get("metrics", "Nenhuma métrica encontrada"))
                        
                        # Botão para download
                        if metrics.get("metrics"):
                            st.download_button(
                                label="📥 Baixar Métricas",
                                data=metrics["metrics"],
                                file_name="metricas_chave_fii.txt",
                                mime="text/plain"
                            )
            
            elif action == "detailed_insights":
                st.subheader("🔍 Análise Detalhada dos Relatórios")
                with st.spinner("Gerando insights detalhados... Isso pode levar alguns minutos."):
                    selected_model = st.session_state.get('selected_model', config.LLM_MODEL_NAME)
                    insights = llm_services.generate_insights_from_documents(retriever, model_name=selected_model)
                    
                    # Criar abas para diferentes insights
                    insight_tabs = st.tabs([
                        "🏢 FIIs Principais", 
                        "💰 Rendimentos", 
                        "🏗️ Setores", 
                        "📈 Recomendações",
                        "⚠️ Riscos & Oportunidades",
                        "📊 Tendências"
                    ])
                    
                    queries = list(insights.keys())
                    
                    for i, tab in enumerate(insight_tabs):
                        with tab:
                            if i < len(queries):
                                query = queries[i]
                                insight = insights[query]
                                st.markdown(f"**Pergunta:** {query}")
                                st.markdown("---")
                                st.markdown(insight)
                    
                    # Botão para download de todos os insights
                    all_insights_text = "\n\n".join([f"PERGUNTA: {q}\n\nRESPOSTA: {a}\n{'='*50}" for q, a in insights.items()])
                    st.download_button(
                        label="📥 Baixar Todos os Insights",
                        data=all_insights_text,
                        file_name="insights_completos_fii.txt",
                        mime="text/plain"
                    )
            
            # Limpar ação após processamento
            st.session_state.insight_action = None
        
        # Seção de informações adicionais
        with st.expander("ℹ️ Como funcionam os Insights"):
            st.write("""
            **Os insights são gerados automaticamente usando:**
            
            1. **RAG (Retrieval-Augmented Generation)**: Busca informações relevantes nos documentos
            2. **IA Generativa**: Analisa e sintetiza as informações encontradas  
            3. **Prompts Especializados**: Perguntas específicas para extrair insights valiosos
            
            **Tipos de Insights Disponíveis:**
            - 📋 **Resumo Executivo**: Visão geral do mercado e recomendações
            - 📊 **Métricas Chave**: Valores, rendimentos e dados numéricos
            - 🔍 **Análise Detalhada**: Insights segmentados por categoria
            
            **Dica**: Quanto mais documentos processados, mais ricos serão os insights!
            """)

if __name__ == '__main__':
    main()