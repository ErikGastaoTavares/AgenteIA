# Sistema de Triagem Clínica com IA

## Visão Geral
Sistema web completo para triagem clínica automatizada baseado no Protocolo de Manchester:
- **Frontend**: Interface web moderna com Next.js
- **Backend**: API REST com FastAPI
- **IA**: Modelo Mistral via Ollama para classificação
- **Embeddings**: BioBERT português para análise semântica
- **Banco Vetorial**: ChromaDB para casos similares

## Arquitetura do Sistema

```
AgenteIA/
├── frontend/          # Interface web (Next.js)
│   ├── pages/         # Páginas da aplicação
│   ├── components/    # Componentes reutilizáveis
│   └── package.json   # Dependências do frontend
└── backend/           # API REST (FastAPI)
    ├── main.py        # Servidor principal
    ├── requirements.txt # Dependências Python
    └── README.md      # Documentação da API
```

## Requisitos do Sistema
- Windows 10 ou superior
- Python 3.8+
- Node.js 16+
- 8 GB+ RAM recomendado
- 10 GB+ espaço em disco

## Instalação

### 1. Pré-requisitos - Ollama e Modelo
```bash
# 1. Instalar Ollama de https://ollama.com/download
# 2. Baixar e iniciar modelo
ollama pull mistral
ollama serve
```

### 2. Backend (FastAPI)
```bash
cd backend

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar servidor
uvicorn main:app --reload --port 8000
```

### 3. Frontend (Next.js)
```bash
cd frontend

# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev
```

## Acesso ao Sistema

- **Interface Principal**: http://localhost:3000
- **Área Administrativa**: http://localhost:3000/admin
- **API Backend**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs

## Funcionalidades

### 🩺 Interface de Triagem
- Campo para descrição de sintomas
- Classificação automática por cores (Protocolo Manchester)
- Análise clínica detalhada
- Condutas recomendadas
- Envio para validação por especialistas

### 👨‍⚕️ Área Administrativa
- Sistema de autenticação (admin/médico/enfermeiro)
- Dashboard com estatísticas do sistema
- Validação de triagens pendentes
- Histórico de casos validados
- Visualização de casos similares

### 🤖 Processamento com IA
- **Classificação**: Modelo Mistral analisa sintomas
- **Embeddings**: BioBERT para busca semântica
- **Casos Similares**: ChromaDB encontra padrões
- **Aprendizado**: Sistema melhora com validações

## Protocolo de Manchester

<img src="figs/infografico-protocolo-manchester.webp" alt="Protocolo de Manchester" width="450"/>

### Classificações:
- 🔴 **VERMELHO**: Emergência (imediato)
- 🟠 **LARANJA**: Muito urgente (10 min)
- 🟡 **AMARELO**: Urgente (60 min)
- 🟢 **VERDE**: Pouco urgente (120 min)
- 🔵 **AZUL**: Não urgente (240 min)

## Banco de Dados

### Estrutura Automática
Os bancos são criados automaticamente na primeira execução:

- **SQLite** (`validacao_triagem.db`):
  - Triagens realizadas
  - Validações de especialistas
  - Usuários e autenticação
  - Estatísticas do sistema

- **ChromaDB** (`chroma_db/`):
  - Embeddings semânticos
  - Base de conhecimento
  - Casos similares
  - Aprendizado contínuo

### Consultas Úteis
```sql
-- Ver triagens pendentes
SELECT * FROM validacao_triagem WHERE validado = 0;

-- Estatísticas por classificação
SELECT classificacao, COUNT(*) FROM validacao_triagem GROUP BY classificacao;

-- Triagens validadas hoje
SELECT * FROM validacao_triagem WHERE data_validacao LIKE '2025-%';
```

## API Endpoints

### Principais Rotas:
- `POST /api/processar-triagem` - Processar sintomas (não salva)
- `POST /api/triagem` - Salvar triagem para validação
- `GET /api/triagens` - Listar triagens (filtros opcionais)
- `POST /api/validar` - Validar triagem
- `POST /api/login` - Autenticação
- `GET /api/estatisticas` - Dashboard

Ver documentação completa em: http://localhost:8000/docs

## Fluxo de Uso

### 1. Triagem Inicial
1. Profissional descreve sintomas na interface
2. IA processa e classifica automaticamente
3. Sistema exibe análise e condutas
4. Opcional: Enviar para validação

### 2. Validação Especializada
1. Especialista acessa área administrativa
2. Revisa triagens pendentes
3. Adiciona feedback e valida
4. Casos validados alimentam o aprendizado

### 3. Aprendizado Contínuo
1. Casos validados são processados
2. Embeddings são armazenados no ChromaDB
3. Sistema melhora busca por similaridade
4. Classificações futuras ficam mais precisas

## Troubleshooting

### Problemas Comuns:

**Ollama não encontrado:**
```bash
# Verificar se está rodando
ollama list
ollama serve
```

**Erro de dependências:**
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

**Banco não criado:**
- Os bancos são criados automaticamente na primeira execução
- Verifique se o backend está rodando

**Modelo não responde:**
```bash
# Verificar modelo
ollama pull mistral
ollama run mistral
```

## Desenvolvimento

### Estrutura de Desenvolvimento:
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend  
cd frontend
npm run dev

# Terminal 3 - Ollama
ollama serve
```

### Variáveis de Ambiente:
```bash
# backend/.env (se necessário)
OLLAMA_URL=http://localhost:11434
```

## Monitoramento

- **Logs Backend**: Console do uvicorn
- **Logs Frontend**: Console do navegador
- **Banco de Dados**: DB Browser for SQLite
- **API Status**: http://localhost:8000/

## Links de Referência
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [Ollama](https://ollama.com/)
- [ChromaDB](https://docs.trychroma.com/)
- [BioBERT](https://huggingface.co/pucpr/biobertpt-clin)
