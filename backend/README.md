# Sistema de Triagem - Backend FastAPI

Este é o backend do Sistema de Triagem baseado no Protocolo de Manchester, desenvolvido com FastAPI e integração com Ollama Mistral.

## Requisitos

- Python 3.8+
- Ollama instalado e rodando
- Modelo Mistral baixado no Ollama
- Dependências listadas em `requirements.txt`

## Pré-requisitos do Ollama

1. Instale o Ollama:
   - Baixe de: https://ollama.ai/
   
2. Baixe o modelo Mistral:
```bash
ollama pull mistral
```

3. Inicie o servidor Ollama:
```bash
ollama serve
```

## Instalação

1. Crie um ambiente virtual:
```bash
python -m venv venv
```

2. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências:
```bash
cd backend
pip install -r requirements.txt
```

## Executando o servidor

1. Certifique-se de que o Ollama está rodando:
```bash
ollama serve
```

2. Execute o servidor FastAPI:
```bash
uvicorn main:app --reload --port 8000
```

O servidor estará disponível em `http://localhost:8000`.

## Documentação da API

A documentação interativa da API estará disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints principais

- `GET /`: Página inicial da API
- `POST /api/processar-triagem`: Processar triagem sem salvar no banco
- `POST /api/triagem`: Salvar triagem no banco para validação
- `GET /api/triagens`: Listar triagens (com filtro opcional)
- `POST /api/validar`: Validar uma triagem
- `POST /api/login`: Autenticar usuário
- `GET /api/estatisticas`: Obter estatísticas do sistema

## Estrutura do projeto

- `main.py`: Ponto de entrada da aplicação com todas as rotas e funções
- `requirements.txt`: Lista de dependências Python
- `validacao_triagem.db`: Banco de dados SQLite (criado automaticamente)
- `chroma_db/`: Banco de dados vetorial ChromaDB (criado automaticamente)

## Funcionalidades

- **Processamento com IA**: Usa modelo Mistral via Ollama para classificação
- **Embeddings**: BioBERT em português para busca de casos similares
- **Banco Vetorial**: ChromaDB para armazenar casos históricos
- **Validação**: Sistema de validação por especialistas
- **Dashboard**: Interface administrativa para monitoramento

## Troubleshooting

1. **Erro "Ollama não encontrado"**: Certifique-se de que o Ollama está instalado e rodando
2. **Erro de modelo**: Execute `ollama pull mistral` para baixar o modelo
3. **Erro de dependências**: Execute `pip install -r requirements.txt`