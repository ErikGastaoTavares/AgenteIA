# =============================================
# IMPORTS E CONFIGURAÇÕES INICIAIS
# =============================================
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
from transformers import AutoTokenizer, AutoModel
import torch



# Configuração do tema personalizado do HCI
st.set_page_config(
    page_title="Triagem Inteligente HCI",
    page_icon="https://hci.org.br/wp-content/uploads/2023/07/cropped-fav-32x32.png",
    layout="wide"
)

# Aplica o estilo customizado com as cores do HCI
css = '''
<style>
    @font-face {
    font-family: 'Montserrat';
    src: url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap') format('woff2');
    font-weight: Bold;
    font-style: normal;
    font-display: swap;
    }    
    
    /* Importa as fontes do Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    
    /* Cores principais do HCI */
    :root {
        --color-scheme: light !important;
        --hci-azul: #003B71;
        --hci-azul-claro: #0072C6;
        --hci-verde: #009B3A;
        --hci-cinza: #58595B;
        --hci-branco: #FFFFFF;
        --hci-font: 'Montserrat', sans-serif;
    }
    
    /* Define o fundo branco para toda a aplicação */
    section[data-testid="stSidebar"],
    .main,
    [data-testid="stAppViewContainer"] {
        background-color: white !important;
    }    
    
    /* Define a fonte e cor do texto para toda a aplicação */
    * {
        font-family: var(--hci-font) !important;
    }
    
    .stMarkdown, 
    .stText,
    p, 
    span,
    div:not([class*="st-"]),
    input,
    textarea,
    placeholder,
    .stTextArea,
    button,
    label,
    .stSelectbox,
    .stMultiSelect,
    .stSlider,
    .stNumberInput,
    .stDateInput,
    .stTimeInput,
    .stFileUploader,
    .stColorPicker,
    .stCheckbox,
    .stRadio,
    .stExpander,
    .stContainer,
    .stColumns,
    .stTabs,
    .stSidebar,
    .stMetric,
    .stAlert,
    .stSuccess,
    .stInfo,
    .stWarning,
    .stError,
    .stException,
    .stSpinner,
    .stProgress,
    .stCaption,
    .stCode,
    .stJson,
    .stDataFrame,
    .stTable,
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--hci-font) !important;
        color: black !important;
    }
    
    /* Estilo do cabeçalho */
    .stApp header {
        background-color: var(--hci-azul) !important;
    }
    
    /* Título principal */
    .title {
        color: var(--hci-azul);
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
      /* Botões */
    .stButton>button {
        background-color: var(--hci-azul) !important;
        color: hci-branco !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        font-family: 'Montserrat Bold', sans-serif !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        text-align: center !important;
    }

    /* Corrige a cor e destaque do texto dentro do botão */
    .stButton p {
        color: white !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05rem !important;
        margin: 0 !important;  /* remove espaçamento padrão do <p> */
    }
        
    .stButton>button:hover {
        background-color: var(--hci-azul-claro) !important;
    }

      /* Área de texto */
    .stTextArea>div>div>textarea {
        font-family: 'Montserrat', sans-serif !important;
        border: 2px solid var(--hci-azul) !important;
        border-radius: 5px !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        padding: 0.75rem !important;
        forced-color-adjust: none !important;
    }

    .stTextArea>div>div>textarea::placeholder {
        color: var(--hci-cinza) !important;
        opacity: 1 !important;                /* sem transparência */
        font-family: 'Montserrat', sans-serif !important;
    }
    
    /* Containers e seções */
    .stTab {
        font-family: 'Montserrat', sans-serif !important;
        background-color: #ffffff !important;
        padding: 1rem !important;
        border-radius: 5px !important;
        margin-bottom: 1rem !important;
        forced-color-adjust: none !important;
    }

    /* Links */
    a {
        color: var(--hci-azul) !important;
    }
    
    a:hover {
        color: var(--hci-azul) !important;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: var(--hci-azul) !important;
    }
    
    /* Textos de status */
    .success {
        color: var(--hci-verde) !important;
    }

    /* Estilo para seções de debug */
    .debug-section {
        color: white !important;
        background-color: #333 !important;
        padding: 1rem !important;
        border-radius: 5px !important;
        margin: 1rem 0 !important;
    }
    
    .debug-section h3 {
        color: white !important;
        margin: 0 !important;
    }
    
    .debug-section p, .debug-section div {
        color: white !important;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)

# Adiciona o logo do HCI
st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <img src="https://hci.org.br/wp-content/uploads/2024/09/logo.png" 
             alt="Logo HCI" 
             style="max-width: 300px; margin-bottom: 1rem;">
        <h2 style='color: #009B3A; font-size: 1.5rem; margin-top: 0; font-family: Montserrat, sans-serif;'>Sistema de Triagem</h2>
    </div>
""", unsafe_allow_html=True)

# Define o dispositivo como CUDA (GPU) se disponível, caso contrário, utiliza CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Carrega o tokenizer e o modelo sem mover para o dispositivo imediatamente
tokenizer = AutoTokenizer.from_pretrained("pucpr/biobertpt-clin")
model = AutoModel.from_pretrained("pucpr/biobertpt-clin")

# Move o modelo para o dispositivo
model = model.to(device)

# =============================================
# FUNÇÕES DE BANCO DE DADOS E VALIDAÇÃO
# =============================================

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
    triagem_id = str(uuid.uuid4())
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO validacao_triagem (id, sintomas, resposta, data_hora) VALUES (?, ?, ?, ?)",
        (triagem_id, sintomas, str(resposta), data_hora)
    )
    conn.commit()
    conn.close()
    return triagem_id

# =============================================
# INICIALIZAÇÃO DE COMPONENTES
# =============================================
# Inicializa o modelo de linguagem
llm = Ollama(model="mistral", request_timeout=420.0)
Settings.llm = llm

# Inicializa o ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection_name = "triagem_hci"

# Tenta obter a coleção existente ou criar uma nova
try:
    # Primeiro tenta obter a coleção existente
    collection = chroma_client.get_collection(name=collection_name)
    # Se conseguir obter, deleta para recriar limpa
    chroma_client.delete_collection(collection_name)
    collection = chroma_client.create_collection(name=collection_name)
except ValueError:
    # Se a coleção não existir, cria uma nova
    collection = chroma_client.create_collection(name=collection_name)
except Exception as e:
    # Para qualquer outro erro, tenta criar diretamente
    try:
        collection = chroma_client.create_collection(name=collection_name)
    except:
        # Se ainda falhar, obtém a coleção existente
        collection = chroma_client.get_collection(name=collection_name)

# =============================================
# CONFIGURAÇÃO DA INTERFACE STREAMLIT
# =============================================
# Inicializa variáveis de estado da sessão
if 'resposta_atual' not in st.session_state:
    st.session_state.resposta_atual = None
if 'sintomas_atuais' not in st.session_state:
    st.session_state.sintomas_atuais = None
if 'enviado_para_validacao' not in st.session_state:
    st.session_state.enviado_para_validacao = False
if 'triagem_id' not in st.session_state:
    st.session_state.triagem_id = None

# =============================================
# PROCESSAMENTO DA TRIAGEM
# =============================================
def carregar_casos_validados():
    """Carrega casos validados do banco de dados"""
    try:
        conn = sqlite3.connect('./validacao_triagem.db')
        cursor = conn.cursor()
        
        # Busca casos que foram validados (validado = 1)
        cursor.execute("SELECT sintomas, resposta FROM validacao_triagem WHERE validado = 1")
        casos = cursor.fetchall()
        conn.close()
        
        return casos
    except Exception as e:
        st.error(f"Erro ao carregar casos validados: {e}")
        return []

def embed_text(text: str) -> List[float]:
    # Processa o texto e gera embeddings
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        # Pega o embedding do token [CLS] (primeiro token)
        embeddings = outputs.last_hidden_state[:, 0, :]
    # Converte para numpy, depois para lista e garante que é uma lista 1D
    return embeddings.cpu().numpy()[0].tolist()

# Carrega os casos validados do banco de dados
casos_validados = carregar_casos_validados()

# Insere os casos validados no banco vetorial
for i, (sintomas, resposta) in enumerate(casos_validados):
    case_id = f"validated_case_{i}"
    try:        # Gera embedding apenas dos sintomas, pois é o que usaremos para comparação
        embedding = embed_text(sintomas)
        collection.add(
            embeddings=[embedding],
            ids=[case_id],
            metadatas=[{"content": sintomas, "resposta": resposta}]
        )
    except Exception as e:
        st.error(f"Erro ao processar o caso validado {case_id}: {str(e)}")

# =============================================
# INTERFACE PRINCIPAL
# =============================================


# Cria um campo de texto onde enfermeiro(a) (ou outro profissional de saúde) pode informar os sintomas do paciente
new_case = st.text_area( 
    "Descreva os sintomas do paciente",
    value="",
    placeholder="Exemplo: Paciente masculino apresenta febre alta, tosse seca e dificuldade para respirar."
    )

# Quando o botão é clicado, o sistema começa a análise
if st.button("Classificar e gerar conduta"):
    # Reseta o estado de envio para validação
    st.session_state.enviado_para_validacao = False
    
    # Verifica se o campo de texto com os sintomas foi preenchido
    if new_case:
        # Mostra um spinner (indicador visual) enquanto o processamento ocorre
        with st.spinner("Classificando..."):

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
                ChatMessage(
                    role="system",
                    content="""Você é um assistente especializado em triagem clínica baseado no Protocolo de Manchester.

ESTRUTURA OBRIGATÓRIA DA RESPOSTA:
Classificação
[COR_ÚNICA]

Justificativa
[Análise clínica detalhada sem mencionar cores]

Condutas
[Procedimentos e encaminhamentos específicos]

REGRAS PARA CLASSIFICAÇÃO:
- VERMELHO: Risco de vida imediato (parada cardiorrespiratória, choque, inconsciência)
- LARANJA: Muito urgente (dor torácica intensa, dispneia grave, alteração neurológica aguda)
- AMARELO: Urgente (febre alta, dor moderada a intensa, vômitos persistentes)
- VERDE: Pouco urgente (sintomas leves, condições estáveis)
- AZUL: Não urgente (condições crônicas estáveis, consultas de rotina)

INSTRUÇÕES ESPECÍFICAS:
1. Na seção "Classificação": Use APENAS uma palavra (vermelho, laranja, amarelo, verde ou azul)
2. Na seção "Justificativa": 
   - NÃO mencione nenhuma cor
   - Analise sintomas, sinais vitais e fatores de risco
   - Explique o raciocínio clínico baseado nos achados
   - Cite protocolos relevantes quando aplicável
3. Na seção "Condutas":
   - Liste procedimentos imediatos
   - Indique exames necessários
   - Especifique encaminhamentos
   - Defina tempo máximo para reavaliação

EXEMPLO DE RESPOSTA CORRETA:
Classificação
amarelo

Justificativa
Paciente apresenta sintomas compatíveis com processo infeccioso agudo. A febre elevada associada à taquicardia sugere necessidade de avaliação médica em prazo reduzido para investigação etiológica e início de tratamento apropriado.

Condutas
- Verificar sinais vitais completos
- Solicitar hemograma completo e PCR
- Administrar antitérmico se necessário
- Reavaliação médica em até 60 minutos"""
                ),
                ChatMessage(role="user", content=input_text),
            ]
            # Tenta executar a consulta ao modelo (via Ollama)
            try:
                resposta = llm.chat(messages)  # Envia as mensagens para o modelo e recebe resposta
                
                # Armazena a resposta e os sintomas na sessão para uso posterior
                st.session_state.resposta_atual = resposta
                st.session_state.sintomas_atuais = new_case

                # CÓDIGO DE DEBUG - Para visualizar a resposta completa
                st.markdown("<div class='debug-section'><h3>🔍 Debug - Texto bruto</h3></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='debug-section'><p>Cores detectadas: {resposta}</p></div>", unsafe_allow_html=True)
                st.markdown("---")
                
                # Exibe o resultado formatado
                st.subheader("Resultado da Triagem")
                
                # Remove palavras indesejadas do texto da resposta
                texto_limpo = str(resposta).replace("assistant:", "").replace("Justificativa:", "").replace("Justificativa", "")
                
                # CÓDIGO DE DEBUG - Para visualizar o texto limpo
                st.markdown("<div class='debug-section'><h3>🔍 Debug - Texto Limpo</h3></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='debug-section'><p>Cores detectadas: {texto_limpo}</p></div>", unsafe_allow_html=True)
                st.markdown("---")

                # Extrai a classificação de risco do texto da resposta (usando o texto limpo)
                texto_resposta = texto_limpo.lower()
                
                # CÓDIGO DE DEBUG - Para verificar detecção de cores
                st.markdown("<div class='debug-section'><h3>🔍 Debug - Detecção de Cores</h3></div>", unsafe_allow_html=True)
                cores_detectadas = []
                if "vermelho" in texto_resposta:
                    cores_detectadas.append("VERMELHO")
                if "laranja" in texto_resposta:
                    cores_detectadas.append("LARANJA")
                if "amarelo" in texto_resposta:
                    cores_detectadas.append("AMARELO")
                if "verde" in texto_resposta:
                    cores_detectadas.append("VERDE")
                if "azul" in texto_resposta:
                    cores_detectadas.append("AZUL")
                
                st.markdown(f"<div class='debug-section'><p>Cores detectadas: {cores_detectadas}</p></div>", unsafe_allow_html=True)
                st.markdown("---")

                # Exibe a classificação colorida
                if "vermelho" in texto_resposta:
                    st.markdown("<div style='background-color: #FF0000; color: white; padding: 1rem; border-radius: 5px; margin: 1rem 0; font-family: Montserrat, sans-serif;'><h3 style='margin:0; font-family: Montserrat, sans-serif;'>🔴 Classificação: EMERGÊNCIA (VERMELHO)</h3></div>", unsafe_allow_html=True)
                elif "laranja" in texto_resposta:
                    st.markdown("<div style='background-color: #FF7F00; color: white; padding: 1rem; border-radius: 5px; margin: 1rem 0; font-family: Montserrat, sans-serif;'><h3 style='margin:0; font-family: Montserrat, sans-serif;'>🟠 Classificação: MUITO URGENTE (LARANJA)</h3></div>", unsafe_allow_html=True)
                elif "amarelo" in texto_resposta:
                    st.markdown("<div style='background-color: #FFFF00; color: #333; padding: 1rem; border-radius: 5px; margin: 1rem 0; font-family: Montserrat, sans-serif;'><h3 style='margin:0; font-family: Montserrat, sans-serif;'>🟡 Classificação: URGENTE (AMARELO)</h3></div>", unsafe_allow_html=True)
                elif "verde" in texto_resposta:
                    st.markdown("<div style='background-color: #00FF00; color: #333; padding: 1rem; border-radius: 5px; margin: 1rem 0; font-family: Montserrat, sans-serif;'><h3 style='margin:0; font-family: Montserrat, sans-serif;'>🟢 Classificação: POUCO URGENTE (VERDE)</h3></div>", unsafe_allow_html=True)
                elif "azul" in texto_resposta:
                    st.markdown("<div style='background-color: #0000FF; color: white; padding: 1rem; border-radius: 5px; margin: 1rem 0; font-family: Montserrat, sans-serif;'><h3 style='margin:0; font-family: Montserrat, sans-serif;'>🔵 Classificação: NÃO URGENTE (AZUL)</h3></div>", unsafe_allow_html=True)
                else:
                    # Se nenhuma cor for detectada, exibe uma mensagem padrão
                    st.warning("⚠️ Classificação não detectada automaticamente. Verifique a resposta abaixo.")
                
                # Divide a resposta em seções
                partes = texto_limpo.split("Condutas")

                # Extrai a classificação para remover da análise clínica
                classificacao_detectada = ""
                if "vermelho" in texto_resposta:
                    classificacao_detectada = "vermelho"
                elif "laranja" in texto_resposta:
                    classificacao_detectada = "laranja"
                elif "amarelo" in texto_resposta:
                    classificacao_detectada = "amarelo"
                elif "verde" in texto_resposta:
                    classificacao_detectada = "verde"
                elif "azul" in texto_resposta:
                    classificacao_detectada = "azul"

                # Exibe a análise clínica (removendo a classificação)
                st.markdown("### Análise Clínica")
                primeira_parte = partes[0].strip()
                
                # Remove a seção "Classificação" e limpa a justificativa
                if "Classificação" in primeira_parte:
                    # Pega apenas a parte da justificativa
                    if "Justificativa" in primeira_parte:
                        justificativa = primeira_parte.split("Justificativa")[1].strip()
                    else:
                        # Se não tem "Justificativa", pega tudo após "Classificação"
                        justificativa = primeira_parte.split("Classificação")[1].strip()
                        # Remove a primeira linha (que é só a cor)
                        linhas_justificativa = justificativa.split('\n')
                        if len(linhas_justificativa) > 1:
                            justificativa = '\n'.join(linhas_justificativa[1:]).strip()
                else:
                    justificativa = primeira_parte
                
                # Remove a cor da classificação se aparecer no início da justificativa
                if classificacao_detectada and justificativa.lower().startswith(classificacao_detectada):
                    justificativa = justificativa[len(classificacao_detectada):].strip()
                    # Remove traço se existir
                    if justificativa.startswith("-"):
                        justificativa = justificativa[1:].strip()
                
                # Validação adicional para garantir que há conteúdo na justificativa
                if not justificativa or len(justificativa.strip()) < 10:
                    justificativa = "Análise clínica baseada nos sintomas apresentados e protocolos de triagem aplicáveis."
                
                st.write(justificativa)
                
                # ...existing code...
                # Exibe as condutas se existirem
                st.markdown("### Condutas Recomendadas")
                condutas_texto = ""
                if len(partes) > 1:
                    condutas_texto = partes[1].strip()
                elif "Condutas" in str(resposta):
                    condutas_partes = str(resposta).split("Condutas")
                    if len(condutas_partes) > 1:
                        condutas_texto = condutas_partes[1].strip()
                
                if condutas_texto:
                    st.write(condutas_texto)
                else:
                    st.write("Condutas específicas a serem determinadas pelo profissional de saúde conforme avaliação clínica.")
                
            except Exception as e:
                # Em caso de erro, mostra uma mensagem de erro na interface
                st.error(f"Erro ao processar a triagem: {str(e)}")
                st.error("Por favor, tente novamente ou contate o suporte técnico.")
            else:
                    # Caso o usuário não preencha os sintomas, exibe aviso
                    st.warning("Por favor, insira os sintomas do paciente.")

# =============================================
# SEÇÃO DE VALIDAÇÃO E CONTROLE DE QUALIDADE
# =============================================
st.markdown("---")
st.subheader("📋 Validação e Controle de Qualidade")

# Container para o botão e status de validação
validacao_container = st.container()
with validacao_container:
    # Botão para enviar para validação (aparece apenas se houver uma resposta)
    if st.session_state.resposta_atual is not None and not st.session_state.enviado_para_validacao:
        col1, col2 = st.columns([2,1])
        with col1:
            if st.button("📤 Enviar para validação por especialistas", use_container_width=True):
                # Salva a resposta no banco de dados de validação
                triagem_id = salvar_para_validacao(
                    st.session_state.sintomas_atuais, 
                    st.session_state.resposta_atual
                )
                
                # Atualiza o estado da sessão
                st.session_state.enviado_para_validacao = True
                st.session_state.triagem_id = triagem_id
                
                # Exibe mensagem de sucesso
                st.success(f"✅ Triagem enviada para validação com sucesso!")
                st.info(f"🔍 ID de Rastreamento: {triagem_id}")
                st.info("👨‍⚕️ A triagem será revisada por especialistas clínicos para garantir a precisão da classificação e das condutas sugeridas.")

    # Exibe mensagem se já foi enviado para validação
    if st.session_state.enviado_para_validacao:
        st.success(f"✅ Esta triagem já foi enviada para validação")
        st.info(f"🔍 ID de Rastreamento: {st.session_state.triagem_id}")

# =============================================
# INFORMAÇÕES DO SISTEMA
# =============================================
tab1, tab2 = st.tabs(["ℹ️ Sobre o Sistema de Validação", "🔐 Área Administrativa"])

with tab1:
    st.markdown("""
    ### Sistema de Validação de Triagens
    
    O processo de validação garante a qualidade e segurança das triagens realizadas.
    
    **📝 Processo de validação:**
    1. 🏷️ Atribuição de ID único para rastreamento
    2. 👨‍⚕️ Revisão por especialistas clínicos
    3. 📊 Registro de feedback e melhorias
    4. 🔄 Incorporação à base de conhecimento
    
    **✨ Benefícios:**
    - 🎯 Garantia de qualidade nas classificações
    - 📈 Melhoria contínua do sistema de IA
    - 🏥 Segurança para os pacientes
    - ✅ Conformidade com protocolos clínicos
    """)

with tab2:
    st.markdown("""
    ### 🔐 Painel Administrativo
    
    *Acesso restrito a profissionais autorizados*
    
    **⚙️ Funcionalidades disponíveis:**
    - 📋 Visualização de triagens pendentes
    - ✍️ Interface de revisão e feedback
    - 📊 Estatísticas e métricas do sistema
    - 👥 Gerenciamento de usuários
    
    Para acessar o painel completo de validação, utilize o aplicativo administrativo separado (`AppAdminMedico.py`).
    """)

# =============================================================================
# RODAPÉ
# =============================================================================
st.markdown("---")
st.caption("Sistema desenvolvido conforme o Protocolo de Manchester")