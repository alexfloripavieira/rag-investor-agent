# Agente de Análise de Investimentos RAG

## Visão Geral

O Agente de Análise de Investimentos RAG é uma aplicação avançada que utiliza Retrieval-Augmented Generation (RAG) para análise inteligente de documentos financeiros. A aplicação combina processamento de documentos PDF, embeddings vetoriais, e modelos de linguagem para fornecer insights automáticos, conversação inteligente e análises detalhadas de investimentos.

## Arquitetura do Sistema

### Diagrama de Arquitetura

```mermaid
graph TB
    U[Usuario] --> ST[Streamlit Frontend]
    ST --> FM[File Manager]
    ST --> VM[Vector Manager]
    ST --> LLM[LLM Services]
    
    FM --> RN[reports_new/]
    FM --> RP[reports_processed/]
    
    VM --> CB[ChromaDB]
    VM --> OE[OpenAI Embeddings]
    
    LLM --> OA[OpenAI API]
    LLM --> LC[LangChain]
    
    CB --> VS[vector_store_chroma/]
    
    subgraph "RAG Pipeline"
        PDF[PDF Documents] --> TXT[Text Extraction]
        TXT --> CHK[Text Chunking]
        CHK --> EMB[Embeddings Generation]
        EMB --> IDX[Vector Indexing]
        IDX --> CB
    end
    
    subgraph "Query Processing"
        Q[User Query] --> RET[Vector Retrieval]
        RET --> CTX[Context Assembly]
        CTX --> GEN[Response Generation]
        GEN --> R[Response]
    end
```

### Diagrama de Componentes UML

```mermaid
graph LR
    subgraph "Frontend Layer"
        ST[Streamlit App]
        UI[User Interface]
        TABS[Tab Components]
    end
    
    subgraph "Business Logic Layer"
        FM[FileHandler]
        VM[VectorStoreManager]
        LLM[LLMServices]
        CFG[Config]
    end
    
    subgraph "Data Layer"
        FS[File System]
        CB[ChromaDB]
        VS[Vector Store]
    end
    
    subgraph "External Services"
        OAI[OpenAI API]
        DDG[DuckDuckGo Search]
    end
    
    ST --> FM
    ST --> VM
    ST --> LLM
    FM --> FS
    VM --> CB
    VM --> VS
    LLM --> OAI
    LLM --> DDG
    
    CFG --> FM
    CFG --> VM
    CFG --> LLM
```

### Diagrama de Sequência - Processamento de Documento

```mermaid
sequenceDiagram
    participant U as Usuario
    participant ST as Streamlit
    participant FM as FileManager
    participant VM as VectorManager
    participant CB as ChromaDB
    participant OAI as OpenAI
    
    U->>ST: Upload PDF
    ST->>FM: save_uploaded_files()
    FM->>FS: Salvar em reports_new/
    
    U->>ST: Processar Relatórios
    ST->>FM: get_new_reports_to_process()
    FM-->>ST: Lista de arquivos
    
    loop Para cada arquivo
        ST->>VM: is_document_already_processed()
        VM->>CB: Verificar duplicatas
        CB-->>VM: Resultado verificação
        
        alt Não é duplicata
            ST->>VM: add_documents_from_file()
            VM->>VM: Carregar PDF
            VM->>VM: Dividir em chunks
            VM->>OAI: Gerar embeddings
            OAI-->>VM: Embeddings
            VM->>CB: Armazenar no vector store
            CB-->>VM: Confirmação
            ST->>FM: move_processed_file()
            FM->>FS: Mover para reports_processed/
        else É duplicata
            ST->>U: Arquivo já processado
        end
    end
    
    ST-->>U: Processamento concluído
```

### Diagrama de Sequência - Geração de Insights

```mermaid
sequenceDiagram
    participant U as Usuario
    participant ST as Streamlit
    participant LLM as LLMServices
    participant VM as VectorManager
    participant CB as ChromaDB
    participant OAI as OpenAI
    
    U->>ST: Solicitar Insights
    ST->>VM: count_documents()
    VM-->>ST: Número de chunks
    
    alt Documentos disponíveis
        U->>ST: Escolher tipo de insight
        ST->>VM: get_retriever()
        VM-->>ST: Retriever configurado
        
        alt Resumo Executivo
            ST->>LLM: generate_market_summary()
            LLM->>VM: retriever.invoke(query)
            VM->>CB: Busca por similaridade
            CB-->>VM: Documentos relevantes
            VM-->>LLM: Contexto recuperado
            LLM->>OAI: Prompt + Contexto
            OAI-->>LLM: Resposta gerada
            LLM-->>ST: Resumo executivo
        else Métricas Chave
            ST->>LLM: extract_key_metrics()
            LLM->>VM: retriever.invoke(query)
            VM->>CB: Busca dados numéricos
            CB-->>VM: Documentos com métricas
            VM-->>LLM: Contexto com dados
            LLM->>OAI: Prompt de extração
            OAI-->>LLM: Métricas estruturadas
            LLM-->>ST: Dados extraídos
        else Análise Detalhada
            ST->>LLM: generate_insights_from_documents()
            loop Para cada query de insight
                LLM->>VM: retriever.invoke(specific_query)
                VM->>CB: Busca específica
                CB-->>VM: Documentos relacionados
                VM-->>LLM: Contexto específico
                LLM->>OAI: Prompt especializado
                OAI-->>LLM: Insight gerado
            end
            LLM-->>ST: Conjunto de insights
        end
        
        ST-->>U: Insights apresentados
    else Sem documentos
        ST-->>U: Aviso para processar documentos
    end
```

### Diagrama de Fluxo de Dados

```mermaid
flowchart TD
    START([Início]) --> UPLOAD[Upload de PDFs]
    UPLOAD --> CHECK{Arquivo já processado?}
    
    CHECK -->|Não| PROCESS[Processar Documento]
    CHECK -->|Sim| SKIP[Pular Processamento]
    
    PROCESS --> EXTRACT[Extrair Texto]
    EXTRACT --> CHUNK[Dividir em Chunks]
    CHUNK --> EMBED[Gerar Embeddings]
    EMBED --> STORE[Armazenar no ChromaDB]
    STORE --> MOVE[Mover para Processados]
    
    SKIP --> MOVE
    MOVE --> READY[Sistema Pronto]
    
    READY --> QUERY{Tipo de Uso}
    
    QUERY -->|Chat| CHAT[Conversação]
    QUERY -->|Visualizar| VIEW[Visualizar PDF]
    QUERY -->|Insights| INSIGHTS[Gerar Insights]
    
    CHAT --> RETRIEVE1[Recuperar Contexto]
    RETRIEVE1 --> AGENT[Agente Conversacional]
    AGENT --> RESPONSE1[Resposta ao Usuario]
    
    VIEW --> DISPLAY[Exibir PDF/Texto]
    DISPLAY --> RESPONSE2[Visualização]
    
    INSIGHTS --> TYPE{Tipo de Insight}
    TYPE -->|Resumo| SUMMARY[Resumo Executivo]
    TYPE -->|Métricas| METRICS[Extrair Métricas]
    TYPE -->|Detalhado| DETAILED[Análise Detalhada]
    
    SUMMARY --> RETRIEVE2[Buscar Documentos]
    METRICS --> RETRIEVE3[Buscar Dados Numéricos]
    DETAILED --> RETRIEVE4[Buscar por Categorias]
    
    RETRIEVE2 --> GENERATE1[Gerar com IA]
    RETRIEVE3 --> GENERATE2[Extrair com IA]
    RETRIEVE4 --> GENERATE3[Analisar com IA]
    
    GENERATE1 --> RESPONSE3[Insights Gerados]
    GENERATE2 --> RESPONSE3
    GENERATE3 --> RESPONSE3
    
    RESPONSE1 --> END([Fim])
    RESPONSE2 --> END
    RESPONSE3 --> END
```

## Funcionalidades Principais

### 1. Upload e Processamento de Documentos
- Upload de múltiplos PDFs simultaneamente
- Detecção automática de duplicatas
- Processamento com divisão inteligente em chunks
- Geração de embeddings vetoriais
- Armazenamento persistente no ChromaDB

### 2. Interface de Conversação
- Chat interativo com agente IA
- Respostas baseadas no conteúdo dos documentos
- Integração com busca web (DuckDuckGo)
- Memória de conversação persistente
- Processamento de linguagem natural

### 3. Visualização de Documentos
- Visualizador de PDF integrado
- Extração e exibição de texto formatado
- Busca dentro do texto
- Download de arquivos
- Estatísticas de documento

### 4. Geração de Insights Automáticos
- **Resumo Executivo**: Análise geral do mercado
- **Métricas Chave**: Extração de dados numéricos
- **Análise Detalhada**: Insights categorizados por:
  - FIIs Principais
  - Rendimentos e Dividendos
  - Setores de Investimento
  - Recomendações
  - Riscos e Oportunidades
  - Tendências de Mercado

### 5. Funcionalidades de Áudio
- Text-to-Speech (TTS) para resumos
- Text-to-Speech para documentos completos
- Concatenação automática de áudio
- Controles de reprodução nativos
- Download de arquivos de áudio

## Stack Tecnológico

### Frontend
- **Streamlit**: Interface web reativa
- **HTML/CSS**: Customizações de interface
- **JavaScript**: Componentes interativos

### Backend
- **Python 3.12**: Linguagem principal
- **LangChain**: Framework para LLM
- **ChromaDB**: Banco de dados vetorial
- **PyPDF**: Processamento de PDF
- **pydub**: Manipulação de áudio

### Inteligência Artificial
- **OpenAI GPT-4o-mini**: Modelo de linguagem
- **OpenAI Embeddings**: text-embedding-3-small
- **OpenAI TTS**: Síntese de voz (modelo tts-1)
- **DuckDuckGo Search**: Busca web complementar

### Infraestrutura
- **Docker**: Containerização
- **Docker Compose**: Orquestração
- **Environment Variables**: Configuração segura

## Como Usar a Aplicação

### Para Usuários

1. **Acesso Initial**
   - Abra a aplicação em http://localhost:8501
   - Visualize a interface com 3 abas principais

2. **Carregamento de Documentos**
   - Na barra lateral, use "Carregar Novos Relatórios"
   - Selecione um ou mais arquivos PDF
   - Aguarde confirmação do upload

3. **Processamento**
   - Clique em "Integrar Novos Relatórios ao Agente"
   - Observe o status de cada arquivo (Novo/Já Processado)
   - Aguarde o processamento RAG completar

4. **Uso das Funcionalidades**

   **Aba "Conversar com Agente":**
   - Digite perguntas sobre seus relatórios
   - Receba respostas contextualizadas
   - Histórico de conversação mantido

   **Aba "Visualizador de Relatório":**
   - Selecione um relatório processado
   - Escolha entre visualização PDF ou texto
   - Use funcionalidades de busca e download

   **Aba "Insights dos Relatórios":**
   - Clique em "Resumo Executivo" para análise geral
   - Use "Métricas Chave" para dados específicos
   - "Análise Detalhada" para insights categorizados

5. **Recursos Avançados**
   - Download de insights como arquivos .txt
   - Geração e download de áudios TTS
   - Visualização de estatísticas do sistema

### Para Administradores

1. **Configuração de Ambiente**
   - Configure OPENAI_API_KEY no arquivo .env
   - Ajuste parâmetros em config.py conforme necessário
   - Verifique dependências FFmpeg para TTS

2. **Monitoramento**
   - Acompanhe logs de processamento
   - Monitore uso do ChromaDB
   - Verifique métricas de performance

3. **Manutenção**
   - Limpeza periódica de arquivos duplicados
   - Backup do vector store
   - Atualizações de dependências

## Explicação Técnica Detalhada

### Arquitetura RAG (Retrieval-Augmented Generation)

A aplicação implementa um pipeline RAG completo:

1. **Ingestão de Documentos**
   ```python
   # Fluxo de processamento
   PDF → PyPDFLoader → TextSplitter → OpenAIEmbeddings → ChromaDB
   ```

2. **Recuperação (Retrieval)**
   ```python
   # Busca por similaridade
   Query → Embedding → ChromaDB.similarity_search → Documentos Relevantes
   ```

3. **Geração (Generation)**
   ```python
   # Prompt engineering
   Query + Context → OpenAI GPT → Resposta Fundamentada
   ```

### Componentes Principais

#### VectorStoreManager
- Gerencia embeddings e armazenamento vetorial
- Implementa detecção de duplicatas
- Otimiza consultas por similaridade
- Mantém metadados de documentos

```python
class VectorStoreManager:
    def add_documents_from_file(self, file_path):
        # Verificação de duplicatas
        # Chunking inteligente
        # Geração de embeddings
        # Armazenamento no ChromaDB
```

#### LLMServices
- Encapsula interações com OpenAI
- Implementa diferentes tipos de prompts
- Gerencia geração de insights
- Controla síntese de voz

```python
def generate_insights_from_documents(retriever):
    # Múltiplas queries especializadas
    # Recuperação contextual
    # Geração de insights categorizados
```

#### FileHandler
- Gerencia fluxo de arquivos
- Implementa sistema anti-duplicação
- Controla persistência de dados
- Organiza diretórios de trabalho

### Otimizações Implementadas

1. **Performance**
   - Chunking otimizado (1000 chars, 200 overlap)
   - Retrieval configurável (k=4 padrão)
   - Cache de embeddings no ChromaDB
   - Processamento assíncrono de áudio

2. **Qualidade**
   - Prompts especializados por tipo de insight
   - Temperature ajustada por caso de uso
   - Validação de entrada e saída
   - Tratamento robusto de erros

3. **Usabilidade**
   - Interface reativa com Streamlit
   - Progress bars para operações longas
   - Downloads diretos de conteúdo
   - Feedback visual consistente

### Segurança e Boas Práticas

1. **Dados Sensíveis**
   - API keys em variáveis de ambiente
   - .gitignore para dados locais
   - Não exposição de embeddings

2. **Validação**
   - Verificação de tipos de arquivo
   - Sanitização de inputs
   - Tratamento de exceções

3. **Performance**
   - Lazy loading de componentes
   - Gerenciamento eficiente de memória
   - Cleanup automático de recursos

## Configuração e Instalação

### Pré-requisitos
- Python 3.12+
- Docker e Docker Compose
- FFmpeg (para funcionalidades TTS)
- Chave API da OpenAI

### Instalação via Docker (Recomendado)

1. **Clone o repositório**
   ```bash
   git clone <repository-url>
   cd rag-investor-agent
   ```

2. **Configure variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite .env com sua OPENAI_API_KEY
   ```

3. **Execute com Docker**
   ```bash
   docker-compose up --build
   ```

### Instalação Local

1. **Ambiente Python**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # ou
   venv\Scripts\activate     # Windows
   ```

2. **Instale dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute aplicação**
   ```bash
   streamlit run app.py
   ```

## Estrutura do Projeto

```
rag-investor-agent/
├── app.py                 # Interface principal Streamlit
├── config.py             # Configurações centralizadas
├── file_handler.py       # Gerenciamento de arquivos
├── llm_services.py       # Serviços de IA e LLM
├── vector_store.py       # Gerenciador do banco vetorial
├── memory.py            # Gerenciamento de memória
├── prompts.py           # Templates de prompts
├── requirements.txt     # Dependências Python
├── Dockerfile           # Configuração Docker
├── docker-compose.yml   # Orquestração de serviços
├── .env                # Variáveis de ambiente
├── .gitignore          # Arquivos ignorados pelo Git
├── CLAUDE.md           # Documentação técnica
├── reports_new/        # Arquivos pendentes
├── reports_processed/  # Arquivos processados
└── vector_store_chroma/ # Banco de dados vetorial
```

## Contribuição

### Desenvolvimento
1. Faça fork do projeto
2. Crie branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

### Testes
- Execute `python test_rag.py` para testar pipeline RAG
- Use `python test_insights.py` para validar geração de insights
- Execute `python test_duplicates.py` para verificar anti-duplicação

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Contato

Para questões técnicas ou sugestões de melhorias, entre em contato com a equipe de desenvolvimento.