# Assistente de IA para Triagem Clínica com Sistema de Validação

Este projeto implementa um assistente de IA com interface web para triagem clínica automatizada, utilizando **embeddings semânticos**, **banco vetorial (ChromaDB)**, um **modelo local (Mistral via Ollama)** e um **sistema de validação por especialistas**.

---

## Visão Geral

O assistente recebe **sintomas clínicos** como entrada, busca **casos semelhantes** em um banco vetorial e classifica o paciente conforme o **Protocolo de Manchester**, fornecendo também **condutas iniciais**. As classificações podem ser enviadas para validação por especialistas clínicos, permitindo a melhoria contínua do sistema.

### Funcionamento geral do assistente

<img src="figs/AgenteIA.png" alt="Fluxo do Assistente de IA" width="500"/>

### Cores e classificações do Protocolo de Manchester

<img src="figs/infografico-protocolo-manchester.jpg" alt="Protocolo de Manchester" width="450"/>

---

## Pré-requisitos

- **Sistema operacional:** Windows 10 ou superior  
- **Memória RAM recomendada:** 8 GB ou mais  
- **Espaço em disco:** 10 GB ou mais  

---

## Etapas de Instalação

### 1. Instalar o Ollama

> O Ollama roda modelos LLM localmente. Requer suporte à virtualização.

- Baixe: [https://ollama.com/download](https://ollama.com/download)
- Após a instalação, teste no terminal:

```bash
ollama list
```

---

### 2. Baixar o modelo `mistral`

```bash
ollama pull mistral
```

> Obs.: O modelo `llama3` pode exigir mais memória RAM.

---

### 3. Instalar Python 3.10.x

- Baixe: [Python 3.10.11](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
- Marque a opção **Add Python to PATH**
- Verifique a versão instalada:

```bash
python --version
```

---

### 4. Criar ambiente virtual

```powershell
cd "C:\Users\SEU_USUARIO\Documents\Projetos\AgenteIA"
python -m venv venv310
.\venv310\Scripts\Activate.ps1
```

---

### 5. Instalar dependências

```bash
pip install --upgrade pip
pip install streamlit
pip install llama-index
pip install chromadb
pip install sentence-transformers
pip install nest_asyncio
pip install pandas
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## Executar o Aplicativo

### Aplicativo Principal de Triagem

```powershell
streamlit run app-bd-validacao.py
```

Abra o navegador em:

[http://localhost:8501](http://localhost:8501)

### Painel de Administração para Validação

```powershell
streamlit run admin-validacao.py
```

Abra o navegador em:

[http://localhost:8501](http://localhost:8501)

> Nota: Se o aplicativo principal já estiver em execução, o painel de administração será aberto na porta 8502.

---

## Arquivos do Projeto

- **app.py**: Versão básica do assistente (sem persistência)
- **app-bd.py**: Versão com persistência de dados usando ChromaDB
- **app-bd-validacao.py**: Versão com persistência e sistema de validação
- **admin-validacao.py**: Painel administrativo para validação de triagens
- **casos.txt**: Base de conhecimento com casos clínicos classificados
- **teste.txt**: Casos de teste para validação do sistema

---

## Sistema de Validação

O sistema de validação permite que especialistas clínicos revisem as classificações e condutas geradas pelo assistente de IA, garantindo a qualidade e precisão das triagens.

### Fluxo de Validação

1. **Triagem do Paciente**: O profissional de saúde insere os sintomas do paciente no aplicativo principal
2. **Classificação pela IA**: O sistema classifica o paciente conforme o Protocolo de Manchester
3. **Envio para Validação**: O profissional envia a triagem para validação por especialistas
4. **Revisão por Especialistas**: Especialistas clínicos acessam o painel administrativo para revisar as triagens
5. **Feedback e Validação**: Os especialistas fornecem feedback e validam ou rejeitam as triagens
6. **Melhoria Contínua**: Os dados validados são automaticamente incorporados à base de conhecimento

### Painel de Administração

O painel administrativo oferece as seguintes funcionalidades:

- **Dashboard**: Visualização de estatísticas de validação
- **Triagens Pendentes**: Lista de triagens aguardando validação
- **Todas as Triagens**: Visualização de todas as triagens (pendentes e validadas)
- **Banco de Conhecimento**: Visualização dos casos originais e validados
- **Exportar Dados**: Exportação de dados para análise externa ou backup

### Credenciais de Acesso (Demonstração)

- **Admin**: admin / admin123
- **Médico**: medico / medico123
- **Enfermeiro**: enfermeiro / enfermeiro123

---

## Interface do Aplicativo Principal

- Campo para **descrição dos sintomas**
- Botão **"Classificar e gerar conduta"**
- Botão **"Enviar para validação por especialistas"** (após classificação)
- Resultado com:
  - **Classificação de risco**
  - **Justificativa clínica**
  - **Condutas iniciais recomendadas**

#### Exemplo da interface em execução:

<img src="figs/interface.png" alt="Interface do Assistente de Triagem" width="600"/>

---

## Banco de Dados

O sistema utiliza dois bancos de dados:

1. **ChromaDB**: Banco de dados vetorial para armazenar embeddings e buscar casos similares
2. **SQLite**: Banco de dados relacional para armazenar as triagens para validação

### Visualizar dados com DB Browser for SQLite

1. Baixe: [https://sqlitebrowser.org](https://sqlitebrowser.org)
2. Abra os arquivos:
   - `./chroma_db/` (banco de dados vetorial)
   - `./validacao_triagem.db` (banco de dados de validação)

---

## Exemplos de Casos Armazenados

```text
case_0: Paciente do sexo masculino, 58 anos, com dor torácica intensa...
case_7: Paciente com falta de ar aos mínimos esforços, tosse produtiva...
case_15: Paciente com dispneia súbita, cianose e confusão...
case_19: Paciente com perda súbita de força no braço esquerdo...
```

---

## Aprendizado Contínuo

O sistema implementa um ciclo de aprendizado contínuo:

1. **Coleta de Dados**: Triagens realizadas pelos profissionais de saúde
2. **Validação por Especialistas**: Revisão das classificações e condutas
3. **Incorporação ao Banco de Conhecimento**: Casos validados são automaticamente adicionados ao banco vetorial
4. **Melhoria das Classificações**: Novas triagens se beneficiam dos casos validados anteriormente

Este ciclo permite que o sistema melhore progressivamente com o uso, tornando-se cada vez mais preciso nas classificações.

---

## Links Úteis

- [LlamaIndex](https://docs.llamaindex.ai/en/stable/)
- [ChromaDB](https://docs.trychroma.com/)
- [Ollama](https://ollama.com/)
- [Streamlit](https://streamlit.io/)
- [SQLite](https://www.sqlite.org/index.html)
- [Protocolo de Manchester](https://www.gov.br/saude/pt-br/composicao/saes/dahu/sistema-de-classificacao-de-risco)
