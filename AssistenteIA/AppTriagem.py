from typing import List # Importa o tipo de dado List usado para anotar funções
import warnings
warnings.filterwarnings("ignore", category=UserWarning) # Ignora mensagens de alerta do tipo UserWarning (apenas para deixar a interface limpa)
import streamlit as st # Importa a biblioteca de interface web Streamlit
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama 
from llama_index.core.llms import ChatMessage # Importa classes do LlamaIndex para usar um modelo de linguagem (LLM)
# Permite usar asyncio dentro do Streamlit sem conflito. Asyncio permite que múltiplas tarefas rodem ao mesmo tempo, sem travar.
import nest_asyncio
nest_asyncio.apply()  
# Importa o ChromaDB, um banco de dados vetorial para armazenar e buscar embeddings
import chromadb
# Importa sqlite3 para armazenar as respostas para validação
import sqlite3
# Importa datetime para registrar a data e hora da triagem
from datetime import datetime
# Importa uuid para gerar identificadores únicos
import uuid
from pathlib import Path

# Função para inicializar o banco de dados de validação
def init_validation_db():
    conn = sqlite3.connect('./validacao_triagem.db')
    cursor = conn.cursor()
    # Cria a tabela de validação se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS validacao_triagem (
        id TEXT PRIMARY KEY,
        sintomas TEXT NOT NULL,
        resposta TEXT NOT NULL,
        data_hora TEXT NOT NULL,
        validado INTEGER DEFAULT 0,
        feedback TEXT,
        validado_por TEXT,
        data_validacao TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Função para salvar a resposta no banco de dados de validação
def salvar_para_validacao(sintomas, resposta):
    conn = sqlite3.connect('./validacao_triagem.db')
    cursor = conn.cursor()
    
    # Gera um ID único para a triagem
    triagem_id = str(uuid.uuid4())
    
    # Obtém a data e hora atual
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Insere os dados na tabela
    cursor.execute(
        "INSERT INTO validacao_triagem (id, sintomas, resposta, data_hora) VALUES (?, ?, ?, ?)",
        (triagem_id, sintomas, str(resposta), data_hora)
    )
    
    conn.commit()
    conn.close()
    
    return triagem_id

# Função para carregar casos a partir de arquivos texto
def load_cases_from_file(filepath: Path) -> List[str]:
    """Carrega casos de um arquivo de texto"""
    if not filepath.exists():
        return []
    
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Função para carregar todos os casos a partir dos diferentes arquivos
def load_all_cases() -> List[str]:
    """Carrega todos os casos dos diferentes arquivos"""
    data_dir = Path(__file__).parent / "data"
    
    # Casos fallback (mínimo necessário para o sistema funcionar)
    fallback_cases = [
        "Paciente com dor torácica intensa, dispneia súbita. Classificação: Vermelha. Encaminhamento: Emergência.",
    ]
    
    try:
        cases = []
        
        # Carrega casos de cada arquivo
        base_cases = load_cases_from_file(data_dir / "base_cases.txt")
        new_cases = load_cases_from_file(data_dir / "new_cases.txt")
        validated_cases = load_cases_from_file(data_dir / "validated_cases.txt")
        
        # Combina todos os casos
        cases.extend(base_cases)
        cases.extend(new_cases)
        cases.extend(validated_cases)
        
        return cases if cases else fallback_cases
    except Exception as e:
        st.error(f"Erro ao carregar casos: {e}")
        return fallback_cases

# Função para salvar um novo caso no arquivo new_cases.txt
def save_new_case(case: str):
    """Salva um novo caso no arquivo new_cases.txt"""
    try:
        filepath = Path(__file__).parent / "data" / "new_cases.txt"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"\n{case}")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar novo caso: {e}")
        return False

# Função para salvar um caso validado no arquivo validated_cases.txt
def save_validated_case(case: str):
    """Salva um caso validado no arquivo validated_cases.txt"""
    try:
        filepath = Path(__file__).parent / "data" / "validated_cases.txt"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"\n{case}")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar caso validado: {e}")
        return False

# Inicializa o banco de dados de validação
init_validation_db()

# Inicializa o modelo de linguagem da Ollama com o modelo Mistral
llm = Ollama(model="mistral", request_timeout=420.0)
Settings.llm = llm

# Cria o cliente do banco de dados vetorial ChromaDB com persistência (armazenamento local no diretório chroma_db)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Define o nome da coleção (como uma "tabela") onde os dados serão armazenados
collection_name = "triagem_hci"

# Lista as coleções existentes no banco de dados (SELECT * FROM collections)
collections = chroma_client.list_collections()

# Verifica se a coleção já existe. Se sim, obtém ela. Caso contrário, cria uma nova.
if collection_name in [col.name for col in collections]:
    collection = chroma_client.get_collection(collection_name)
else:
    collection = chroma_client.create_collection(name=collection_name)

# Inicializa variáveis de estado da sessão
if 'resposta_atual' not in st.session_state:
    st.session_state.resposta_atual = None
if 'sintomas_atuais' not in st.session_state:
    st.session_state.sintomas_atuais = None
if 'enviado_para_validacao' not in st.session_state:
    st.session_state.enviado_para_validacao = False
if 'triagem_id' not in st.session_state:
    st.session_state.triagem_id = None

# Mostra o título da interface da aplicação no navegador
st.title("Assistente de Triagem Clínica - HCI")

# Cria um campo de texto onde enfermeiro(a) (ou outro profissional de saúde) pode informar os sintomas do paciente
new_case = st.text_area("Descreva os sintomas do paciente na triagem")

# Quando o botão é clicado, o sistema começa a análise
if st.button("Classificar e gerar conduta"):
    # Reseta o estado de envio para validação
    st.session_state.enviado_para_validacao = False
    
    # Verifica se o campo de texto com os sintomas foi preenchido
    if new_case:
        # Mostra um spinner (indicador visual) enquanto o processamento ocorre
        with st.spinner("Classificando..."):

            # Importa e carrega o modelo de embeddings (vetorização) 
            from sentence_transformers import SentenceTransformer
            # Carrega um modelo pré-treinado de embeddings semânticos chamado all-MiniLM-L6-v2, 
            # disponibilizado pela Sentence Transformers, uma biblioteca baseada no Hugging Face e no PyTorch
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

            # Função que converte um texto em vetor numérico (embedding)
            def embed_text(text: str) -> List[float]:
                # Aplica o modelo para transformar o texto em vetor (tensor)
                embeddings = model.encode([text], convert_to_tensor=True)
                # Converte o tensor para lista de floats e retorna
                return embeddings.cpu().numpy()[0].tolist()            # Os casos base já foram inicializados pela função init_base_cases

            # Função para carregar casos iniciais do SQLite
            def carregar_casos_iniciais():
                """Carrega casos iniciais do SQLite"""
                try:
                    conn = sqlite3.connect('./validacao_triagem.db')
                    cursor = conn.cursor()
                    
                    # Busca casos ativos
                    cursor.execute("SELECT sintomas, classificacao, encaminhamento FROM casos_iniciais WHERE ativo = 1")
                    casos = cursor.fetchall()
                    conn.close()
                    
                    # Formata casos para o formato padrão
                    casos_formatados = []
                    for sintomas, classificacao, encaminhamento in casos:
                        caso = f"{sintomas}. Classificação: {classificacao}. Encaminhamento: {encaminhamento}."
                        casos_formatados.append(caso)
                        
                    return casos_formatados
                except Exception as e:
                    st.error(f"Erro ao carregar casos iniciais: {e}")
                    return []

            # Inicializa o banco com casos base
            def init_base_cases(collection):
                """Inicializa o banco com casos base se estiver vazio"""
                # Verifica se já existem casos no banco
                existing_cases = collection.get()
                if len(existing_cases["ids"]) > 0:
                    return

                # Carrega casos do SQLite
                casos_base = carregar_casos_iniciais()
                
                # Adiciona cada caso ao banco
                for i, caso in enumerate(casos_base):
                    case_id = f"base_case_{i}"
                    embedding = embed_text(caso)
                    collection.add(
                        embeddings=[embedding],
                        ids=[case_id],
                        metadatas=[{"content": caso}]
                    )

            # Inicializa o banco com casos base
            init_base_cases(collection)

            # Converte os sintomas informados pelo usuário em vetor (embedding)
            query_embedding = embed_text(new_case)

            # Consulta no banco vetorial os 3 casos mais semelhantes ao novo caso informado.
            # O ChromaDB utiliza o vetor de embedding gerado para o novo caso (query_embedding)
            # e compara esse vetor com todos os vetores previamente armazenados na coleção.
            # Essa comparação é feita usando uma métrica de similaridade (como produto interno ou cosseno),
            # retornando os 'n_results' casos com maior similaridade semântica.
            # O resultado inclui os metadados dos casos mais parecidos, que serão usados para orientar a resposta do LLM.
            results = collection.query(query_embeddings=[query_embedding], n_results=3)

            # Extrai os conteúdos (textos) dos casos similares retornados
            similar_cases = [metadata["content"] for metadata in results['metadatas'][0]]

            # Monta o prompt com os sintomas e os casos similares
            input_text = f"Sintomas do novo caso: {new_case}\n\nCasos Similares: {' '.join(similar_cases)}"

            # Cria a sequência de mensagens para enviar ao modelo de linguagem
            messages = [
                # Mensagem inicial: define o comportamento do assistente como um profissional da saúde
                ChatMessage(
                    role="system",
                    content="Você é um profissional de saúde responsável pela triagem clínica no Hospital de Clínicas de Ijuí. Seu objetivo é analisar os sintomas do paciente e classificá-lo conforme o protocolo de Manchester, indicando a prioridade de atendimento e orientações clínicas iniciais."
                ),
                # Mensagem com os sintomas e os casos similares
                ChatMessage(role="user", content=input_text),
                # Solicita resposta estruturada com classificação, justificativa e conduta
                ChatMessage(
                    role="user",
                    content="Com base nos casos similares, forneça a classificação de risco (vermelha, laranja, amarela, verde ou azul), justifique essa classificação e sugira condutas iniciais. Não inclua informações irrelevantes ou fora do contexto clínico."
                ),
            ]

            # Tenta executar a consulta ao modelo (via Ollama)
            try:
                resposta = llm.chat(messages)  # Envia as mensagens para o modelo e recebe resposta
                
                # Armazena a resposta e os sintomas na sessão para uso posterior
                st.session_state.resposta_atual = resposta
                st.session_state.sintomas_atuais = new_case
                
                # Exibe o resultado na interface web
                st.subheader("Resultado da Triagem")
                st.write(str(resposta))
                
            except Exception as e:
                # Em caso de erro, mostra uma mensagem de erro na interface
                st.error(f"Ocorreu um erro ao consultar o modelo: {e}")
    else:
        # Caso o usuário não preencha os sintomas, exibe aviso
        st.warning("Por favor, insira os sintomas do paciente.")

# Botão para enviar para validação (aparece apenas se houver uma resposta)
if st.session_state.resposta_atual is not None and not st.session_state.enviado_para_validacao:
    if st.button("Enviar para validação por especialistas"):
        # Salva a resposta no banco de dados de validação
        triagem_id = salvar_para_validacao(
            st.session_state.sintomas_atuais, 
            st.session_state.resposta_atual
        )
        
        # Atualiza o estado da sessão
        st.session_state.enviado_para_validacao = True
        st.session_state.triagem_id = triagem_id
        
        # Exibe mensagem de sucesso
        st.success(f"Triagem enviada para validação com sucesso! ID: {triagem_id}")
        
        # Adiciona informações sobre o processo de validação
        st.info("A triagem será revisada por especialistas clínicos para garantir a precisão da classificação e das condutas sugeridas.")

# Exibe mensagem se já foi enviado para validação
if st.session_state.enviado_para_validacao:
    st.success(f"Esta triagem já foi enviada para validação. ID: {st.session_state.triagem_id}")

# Adiciona uma seção de informações sobre o sistema de validação
with st.expander("Sobre o sistema de validação"):
    st.markdown("""
    ### Sistema de Validação de Triagens
    
    As triagens enviadas para validação são armazenadas em um banco de dados seguro e revisadas por profissionais de saúde especializados.
    
    **Processo de validação:**
    1. A triagem é enviada e recebe um ID único
    2. Especialistas clínicos revisam a classificação e as condutas sugeridas
    3. Feedback é registrado para melhorar o sistema
    4. Casos validados são incorporados à base de conhecimento
    
    **Benefícios:**
    - Garantia de qualidade nas classificações
    - Melhoria contínua do sistema de IA
    - Segurança para os pacientes
    - Conformidade com protocolos clínicos
    """)

# Adiciona uma seção para administradores (apenas para demonstração)
with st.expander("Área de Administração (acesso restrito)"):
    st.markdown("""
    ### Painel de Administração
    
    Esta área é restrita a administradores do sistema e profissionais autorizados.
    
    Para acessar o painel completo de validação, utilize o aplicativo de administração separado.
    
    **Funcionalidades do painel administrativo:**
    - Visualização de todas as triagens pendentes de validação
    - Interface para revisão e feedback
    - Estatísticas de precisão do sistema
    - Gerenciamento de usuários e permissões
    """)
