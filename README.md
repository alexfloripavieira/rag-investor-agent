# 📊 Agente de Análise de Investimentos PRO

Bem-vindo ao **Agente de Análise de Investimentos PRO**! Esta aplicação Streamlit permite que você interaja com seus relatórios financeiros em PDF, extraia informações, resuma conteúdos e até mesmo ouça o texto dos relatórios. Utilizando Retrieval-Augmented Generation (RAG) com ChromaDB e modelos de linguagem avançados da OpenAI, o agente oferece uma experiência interativa para análise de investimentos.

## ✨ Funcionalidades

*   **Upload de Relatórios PDF:** Carregue facilmente múltiplos arquivos PDF de relatórios financeiros.
*   **Processamento e Indexação:** Os relatórios são processados, divididos em chunks e indexados em um banco de dados vetorial (ChromaDB) para busca eficiente.
*   **Agente Conversacional:** Faça perguntas em linguagem natural sobre o conteúdo dos relatórios carregados e receba respostas precisas.
*   **Visualizador de PDF:** Visualize os relatórios PDF diretamente na interface da aplicação.
*   **Extração de Texto Formatado:** Opção para exibir o texto completo extraído de um PDF, formatado para leitura.
*   **Resumo de Relatórios:** Gere resumos concisos de relatórios financeiros com o auxílio de LLMs.
*   **Text-to-Speech (TTS):** Converta o texto de resumos ou relatórios completos em áudio para uma experiência auditiva.
*   **Persistência de Dados:** Os relatórios processados e o banco de dados vetorial são persistidos, permitindo que você retome suas análises.

## 🚀 Tecnologias Utilizadas

*   **Frontend:** Streamlit
*   **Backend/Lógica:** Python
*   **LLM Framework:** LangChain
*   **Modelos de Linguagem:** OpenAI (GPT-4o para LLM, `text-embedding-3-small` para Embeddings, `tts-1` para TTS)
*   **Banco de Dados Vetorial:** ChromaDB
*   **Processamento de PDF:** PyPDFLoader
*   **Manipulação de Áudio:** pydub (requer FFmpeg)
*   **Busca na Web (Agente):** DuckDuckGo Search
*   **Orquestração:** Docker e Docker Compose

## ⚙️ Configuração e Instalação

Siga os passos abaixo para configurar e executar a aplicação em seu ambiente local.

### Pré-requisitos

*   **Python 3.9+**
*   **Docker** e **Docker Compose** (recomendado para ambiente de produção/desenvolvimento consistente)
*   **FFmpeg:** Necessário para a funcionalidade de Text-to-Speech (TTS) e concatenação de áudio.
    *   **Linux (Debian/Ubuntu):** `sudo apt-get update && sudo apt-get install ffmpeg`
    *   **macOS (Homebrew):** `brew install ffmpeg`
    *   **Windows:** Baixe o executável do site oficial do FFmpeg e adicione-o ao seu PATH.

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/rag-investor-agent.git
cd rag-investor-agent
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com suas chaves de API da OpenAI:

```
OPENAI_API_KEY="sua_chave_api_openai_aqui"
```

### 3. Executar com Docker Compose (Recomendado)

A maneira mais fácil de iniciar a aplicação é usando Docker Compose, que gerencia o ambiente Python e as dependências.

```bash
docker-compose up --build
```

A aplicação estará disponível em `http://localhost:8501`.

### 4. Executar Localmente (Alternativo)

Se preferir executar sem Docker:

#### a. Criar e Ativar o Ambiente Virtual

```bash
python -m venv venv
# No Linux/macOS
source venv/bin/activate
# No Windows
venv\Scripts\activate
```

#### b. Instalar Dependências

```bash
pip install -r requirements.txt
```

#### c. Iniciar a Aplicação Streamlit

```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`.

## 📖 Uso

1.  **Carregar Relatórios:** Na barra lateral, use a seção "1. Carregar Novos Relatórios" para fazer upload de arquivos PDF.
2.  **Processar Relatórios:** Clique em "2. Processar Relatórios" para indexar os PDFs carregados no banco de dados vetorial. O número de documentos indexados será exibido.
3.  **Conversar com o Agente:** Na aba "🗣️ Conversar com Agente", digite suas perguntas sobre os relatórios. O agente tentará usar as informações indexadas para responder.
4.  **Explorar Relatórios:** Na aba "📄 Visualizador de Relatório", selecione um relatório processado para:
    *   **Ler PDF (Visualizador):** Tentar exibir o PDF diretamente.
    *   **Ler PDF (Texto Formatado):** Ver o texto extraído do PDF.
    *   **Gerar Resumo:** Obter um resumo do relatório.
    *   **Ouvir Resumo/Relatório Completo:** Converter o texto em áudio.

## 📁 Estrutura do Projeto

*   `app.py`: Ponto de entrada principal da aplicação Streamlit e interface do usuário.
*   `config.py`: Contém configurações globais, como nomes de diretórios e modelos.
*   `file_handler.py`: Funções para salvar, mover e extrair texto de arquivos PDF.
*   `llm_services.py`: Encapsula a lógica de interação com LLMs (agente, resumo, TTS).
*   `vector_store.py`: Gerencia a interação com o ChromaDB (adição de documentos, retriever).
*   `requirements.txt`: Lista de dependências Python do projeto.
*   `Dockerfile`: Define o ambiente Docker para a aplicação.
*   `docker-compose.yml`: Orquestra a construção e execução do contêiner Docker.
*   `.env`: Arquivo para variáveis de ambiente sensíveis (excluído pelo `.gitignore`).
*   `.gitignore`: Define arquivos e diretórios a serem ignorados pelo Git.
*   `reports_new/`: Diretório para PDFs recém-carregados.
*   `reports_processed/`: Diretório para PDFs que já foram processados e indexados.
*   `vector_store/`: Diretório onde o ChromaDB persiste os dados vetoriais.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues para bugs ou sugestões, e enviar pull requests.

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📧 Contato

Para dúvidas ou sugestões, entre em contato com [Seu Nome/Email/GitHub Profile].
