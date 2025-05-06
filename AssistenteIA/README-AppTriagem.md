# Aplicativo Principal de Triagem Clínica

Este documento explica o funcionamento do aplicativo principal de triagem clínica (`app-bd-validacao.py`).

## Visão Geral

O aplicativo principal é uma interface web construída com Streamlit que permite aos profissionais de saúde:

1. Inserir sintomas de pacientes
2. Obter classificações de risco segundo o Protocolo de Manchester
3. Enviar triagens para validação por especialistas

## Tecnologias Utilizadas

- **Streamlit**: Framework para interface web
- **LlamaIndex**: Framework para construção de aplicações com LLMs
- **Ollama/Mistral**: Modelo de linguagem local para geração de texto
- **ChromaDB**: Banco de dados vetorial para armazenamento de embeddings
- **SQLite**: Banco de dados relacional para armazenamento de triagens
- **Sentence Transformers**: Biblioteca para geração de embeddings semânticos

## Fluxo de Funcionamento

### 1. Inicialização

- Carrega o modelo de linguagem Mistral via Ollama
- Inicializa o banco de dados ChromaDB para armazenar embeddings
- Inicializa o banco de dados SQLite para armazenar triagens
- Configura a interface Streamlit

### 2. Classificação de Pacientes

Quando o usuário insere sintomas e clica em "Classificar e gerar conduta":

1. O sistema carrega o modelo de embeddings (Sentence Transformers)
2. Carrega os casos de exemplo do arquivo `casos.txt`
3. Converte os casos em embeddings e os armazena no ChromaDB (se ainda não existirem)
4. Converte os sintomas do paciente em embedding
5. Busca os 3 casos mais similares no banco de dados vetorial
6. Envia os sintomas e os casos similares para o modelo Mistral
7. Exibe a classificação de risco, justificativa e condutas sugeridas

### 3. Envio para Validação

Após a classificação, o usuário pode clicar em "Enviar para validação por especialistas":

1. O sistema gera um ID único para a triagem
2. Armazena os sintomas, a resposta e a data/hora no banco de dados SQLite
3. Exibe uma mensagem de confirmação com o ID da triagem

## Estrutura do Código

### Funções Principais

- `init_validation_db()`: Inicializa o banco de dados de validação
- `salvar_para_validacao()`: Salva uma triagem no banco de dados para validação
- `embed_text()`: Converte texto em embedding (vetor numérico)
- `load_triagem_cases()`: Carrega casos de triagem do arquivo

### Variáveis de Estado

O aplicativo utiliza o sistema de estado do Streamlit para manter informações entre interações:

- `st.session_state.resposta_atual`: Armazena a resposta atual do modelo
- `st.session_state.sintomas_atuais`: Armazena os sintomas atuais
- `st.session_state.enviado_para_validacao`: Controla se a triagem atual já foi enviada
- `st.session_state.triagem_id`: Armazena o ID da triagem enviada

## Interface do Usuário

A interface é composta por:

1. **Título**: "Assistente de Triagem Clínica - HCI"
2. **Campo de texto**: Para inserir os sintomas do paciente
3. **Botão "Classificar e gerar conduta"**: Para iniciar a classificação
4. **Resultado da triagem**: Exibe a classificação, justificativa e condutas
5. **Botão "Enviar para validação por especialistas"**: Para enviar a triagem para validação
6. **Seção "Sobre o sistema de validação"**: Informações sobre o processo de validação
7. **Seção "Área de Administração"**: Informações sobre o painel administrativo

## Como Executar

```bash
streamlit run app-bd-validacao.py
```

O aplicativo será aberto no navegador em http://localhost:8501.

## Integração com o Painel Administrativo

Este aplicativo se integra com o painel administrativo (`admin-validacao.py`) através do banco de dados SQLite. As triagens enviadas para validação podem ser acessadas e validadas pelos especialistas no painel administrativo.

## Fluxo de Dados

```
[Sintomas do Paciente] → [Embedding] → [Busca por Similaridade] → [Casos Similares]
                                                                       ↓
[Resposta Exibida] ← [Modelo Mistral] ← [Prompt com Sintomas e Casos Similares]
        ↓
[Envio para Validação] → [Banco de Dados SQLite] → [Painel Administrativo]
```

## Requisitos

- Python 3.10 ou superior
- Ollama instalado e configurado com o modelo Mistral
- Dependências Python listadas no arquivo `requirements.txt`

## Observações

- O aplicativo utiliza um modelo local (Mistral via Ollama), o que garante privacidade dos dados
- Os casos validados pelos especialistas são incorporados ao banco de conhecimento, melhorando progressivamente a precisão das classificações
- O sistema é projetado para ser usado em ambiente clínico, mas não substitui o julgamento profissional
