from datetime import datetime
from sentence_transformers import SentenceTransformer
from typing import List
from pathlib import Path
import streamlit as st
import sqlite3
import pandas as pd
import os

# Configuração do tema personalizado do HCI
st.set_page_config(
    page_title="Painel de Administração",
    page_icon="https://hci.org.br/wp-content/uploads/2023/07/cropped-fav-32x32.png",
    layout="wide",
    initial_sidebar_state="expanded"
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

    /* Estilo para cards */
    .card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid var(--hci-azul);
    }
    
    .card-success {
        border-left-color: var(--hci-verde);
    }
    
    .card-warning {
        border-left-color: #FF7F00;
    }
    
    .card-danger {
        border-left-color: #FF0000;
    }

    /* Estilo para inputs */
    .stTextInput>div>div>input {
        font-family: 'Montserrat', sans-serif !important;
        border: 2px solid var(--hci-azul) !important;
        border-radius: 5px !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        caret-color: var(--hci-azul) !important; /* Cor do cursor */
    }

    /* Estilo para inputs com foco */
    .stTextInput>div>div>input:focus {
        border-color: var(--hci-azul-claro) !important;
        box-shadow: 0 0 0 2px rgba(0, 59, 113, 0.2) !important;
        outline: none !important;
        caret-color: var(--hci-azul-claro) !important; /* Cor do cursor quando focado */
        animation: blink 1s infinite; /* Animação de piscar */
    }

    /* Animação do cursor piscante */
    @keyframes blink {
        0%, 50% { caret-color: var(--hci-azul-claro); }
        51%, 100% { caret-color: transparent; }
    }

    /* Estilo para campos de senha */
    .stTextInput>div>div>input[type="password"] {
        font-family: 'Montserrat', sans-serif !important;
        border: 2px solid var(--hci-azul) !important;
        border-radius: 5px !important;
        background-color: #ffffff !important;
        color: #000000 !important;
        caret-color: var(--hci-azul) !important;
    }

    .stTextInput>div>div>input[type="password"]:focus {
        border-color: var(--hci-azul-claro) !important;
        box-shadow: 0 0 0 2px rgba(0, 59, 113, 0.2) !important;
        outline: none !important;
        caret-color: var(--hci-azul-claro) !important;
        animation: blink 1s infinite;
    }

    /* Estilo para selectbox */
    .stSelectbox>div>div>select {
        font-family: 'Montserrat', sans-serif !important;
        border: 2px solid var(--hci-azul) !important;
        border-radius: 5px !important;
        background-color: #ffffff !important;
        color: #000000 !important;
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
        <h2 style='color: #009B3A; font-size: 1.5rem; margin-top: 0; font-family: Montserrat, sans-serif;'>Painel de Validação de Triagens</h2>
    </div>
""", unsafe_allow_html=True)

# Função para verificar se o banco de dados existe
def verificar_banco_dados():
    return os.path.exists('./validacao_triagem.db')

# Função para conectar ao banco de dados
def conectar_bd():
    if not verificar_banco_dados():
        st.error("Banco de dados de validação não encontrado. Execute o aplicativo principal primeiro para criar o banco de dados.")
        return None
    
    try:
        conn = sqlite3.connect('./validacao_triagem.db')
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para obter todas as triagens
def obter_triagens(filtro="todas"):
    conn = conectar_bd()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = "SELECT id, sintomas, resposta, data_hora, validado, feedback, validado_por, data_validacao FROM validacao_triagem"
        
        if filtro == "pendentes":
            query += " WHERE validado = 0"
        elif filtro == "validadas":
            query += " WHERE validado = 1"
            
        query += " ORDER BY data_hora DESC"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao obter triagens: {e}")
        conn.close()
        return pd.DataFrame()

# Função para obter uma triagem específica
def obter_triagem(triagem_id):
    conn = conectar_bd()
    if conn is None:
        return None
    
    try:
        query = "SELECT * FROM validacao_triagem WHERE id = ?"
        cursor = conn.cursor()
        cursor.execute(query, (triagem_id,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado
    except Exception as e:
        st.error(f"Erro ao obter triagem: {e}")
        conn.close()
        return None

# Função para converter texto em embedding
@st.cache_resource
def carregar_modelo_embedding():
    return SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text: str) -> List[float]:
    model = carregar_modelo_embedding()
    embeddings = model.encode([text], convert_to_tensor=True)
    return embeddings.cpu().numpy()[0].tolist()

# Função para adicionar caso validado ao banco de dados vetorial
def adicionar_caso_validado(sintomas, resposta, feedback):
    try:
        # Implementar lógica para adicionar ao banco vetorial
        pass
    except Exception as e:
        st.error(f"Erro ao adicionar caso validado: {e}")

# Função para validar uma triagem
def validar_triagem(triagem_id, validado_por, feedback):
    conn = conectar_bd()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        data_validacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE validacao_triagem SET validado = 1, feedback = ?, validado_por = ?, data_validacao = ? WHERE id = ?",
            (feedback, validado_por, data_validacao, triagem_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao validar triagem: {e}")
        conn.close()
        return False

# Função para excluir uma triagem
def excluir_triagem(triagem_id):
    conn = conectar_bd()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM validacao_triagem WHERE id = ?", (triagem_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir triagem: {e}")
        conn.close()
        return False

# Função para obter estatísticas
def obter_estatisticas():
    conn = conectar_bd()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM validacao_triagem")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM validacao_triagem WHERE validado = 1")
        validadas = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM validacao_triagem WHERE validado = 0")
        pendentes = cursor.fetchone()[0]
        conn.close()
        return {"total": total, "validadas": validadas, "pendentes": pendentes}
    except Exception as e:
        st.error(f"Erro ao obter estatísticas: {e}")
        conn.close()
        return None

# Função para exportar dados para CSV
def exportar_csv():
    conn = conectar_bd()
    if conn is None:
        return None
    
    try:
        df = pd.read_sql_query("SELECT * FROM validacao_triagem", conn)
        conn.close()
        return df.to_csv(index=False)
    except Exception as e:
        st.error(f"Erro ao exportar dados: {e}")
        conn.close()
        return None

# Autenticação simples (em produção, use um sistema mais seguro)
def autenticar(username, password):
    usuarios_validos = {
        "admin": "admin",
        "medico": "medico",
        "enfermeiro": "enfermeiro"
    }
    
    if username in usuarios_validos and usuarios_validos[username] == password:
        return True
    return False

# Função para salvar casos validados no arquivo
def save_to_validated_cases(case: str):
    try:
        with open("validated_cases.txt", "a", encoding="utf-8") as f:
            f.write(f"{case}\n")
    except Exception as e:
        st.error(f"Erro ao salvar caso validado: {e}")

# Inicialização da sessão
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = ""
if 'triagem_selecionada' not in st.session_state:
    st.session_state.triagem_selecionada = None
if 'filtro' not in st.session_state:
    st.session_state.filtro = "todas"

# Tela de login
if not st.session_state.autenticado:
    # Centraliza o formulário de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; margin: 2rem 0;'>
            <h2 style='color: #003B71; font-size: 2rem; margin-bottom: 2rem; font-family: Montserrat, sans-serif;'>
                🔐 Login do Sistema
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Container usando CSS diretamente no estilo
        st.markdown("""
        <div style='
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            margin: 1rem 0;
        '>
        """, unsafe_allow_html=True)
        
         # Formulário de login
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "👤 Usuário",
                placeholder="Digite seu usuário"
            )
            password = st.text_input(
                "🔒 Senha", 
                type="password",
                placeholder="Digite sua senha"
            )

            # Captura o clique do botão (estilizado para combinar com o botão ENTRAR)
            submitted = st.form_submit_button("ENTRAR", type="primary")  # Botão de submit com o mesmo texto do botão customizado
            
            # CSS para estilizar o botão de submit padrão para parecer com o botão ENTRAR
            st.markdown("""
            <style>
                /* Estiliza o botão de submit padrão para parecer com o botão ENTRAR */
                [data-testid="stFormSubmitButton"] button {
                    background-color: var(--hci-azul) !important;
                    color: white !important;
                    font-weight: 900 !important;
                    text-transform: uppercase !important;
                    font-family: 'Montserrat Bold', sans-serif !important;
                    border: none !important;
                    padding: 0.6rem 1.2rem !important;
                    text-align: center !important;
                    border-radius: 5px !important;
                    width: 100% !important;
                    max-width: 250px !important;
                    margin: 0 auto !important;
                    display: block !important;
                }
                
                /* Esconde o botão HTML customizado, já que agora estamos usando o botão de submit estilizado */
                .stButton button[type="submit"] {
                    display: none !important;
                }
            </style>
            """, unsafe_allow_html=True)

            if submitted:
                if autenticar(username, password):
                    st.session_state.autenticado = True
                    st.session_state.usuario = username
                    st.success("✅ Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha inválidos!")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Informações de demonstração
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #009B3A 0%, #00b347 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-top: 2rem;
            text-align: center;
        '>
            <h3 style='color: white; margin-bottom: 1rem;'>📋 Credenciais para Demonstração</h3>
            <div style='display: flex; justify-content: space-around; flex-wrap: wrap;'>
                <div style='margin: 0.5rem;'>
                    <strong>👨‍💼 Admin:</strong><br>
                    admin / admin
                </div>
                <div style='margin: 0.5rem;'>
                    <strong>👨‍⚕️ Médico:</strong><br>
                    medico / medico
                </div>
                <div style='margin: 0.5rem;'>
                    <strong>👩‍⚕️ Enfermeiro:</strong><br>
                    enfermeiro / enfermeiro
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Barra lateral
    with st.sidebar:
        # Header da sidebar com estilo
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #003B71 0%, #0072C6 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            text-align: center;
        '>
            <h3 style='color: white; margin: 0;'>👤 Bem-vindo!</h3>
            <p style='color: white; margin: 0.5rem 0 0 0; font-weight: bold;'>{st.session_state.usuario.title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Menu de navegação
        st.markdown("### 🧭 Navegação")
        menu = st.selectbox(
            "Selecione uma opção:",
            ["📊 Dashboard", "⏳ Triagens Pendentes", "📋 Todas as Triagens", "📚 Banco de Conhecimento", "📤 Exportar Dados"],
            format_func=lambda x: x
        )
        
        st.markdown("---")
        
        # Botão de logout estilizado
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario = ""
            st.rerun()
    
    # Conteúdo principal - ajustar os nomes dos menus
    menu_clean = menu.split(" ", 1)[1]  # Remove o emoji para comparação
    
    if "Dashboard" in menu:
        st.markdown("""
        <div style='
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #003B71;
            margin-bottom: 2rem;
        '>
            <h2 style='color: #003B71; margin: 0;'>📊 Dashboard - Estatísticas do Sistema</h2>
        </div>
        """, unsafe_allow_html=True)
        
        stats = obter_estatisticas()
        if stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style='
                    background: white;
                    padding: 2rem;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid #003B71;
                    text-align: center;
                '>
                    <h3 style='color: #003B71; margin-bottom: 1rem;'>📋 Total de Triagens</h3>
                    <h1 style='color: #003B71; font-size: 3rem; margin: 0;'>{stats['total']}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='
                    background: white;
                    padding: 2rem;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid #009B3A;
                    text-align: center;
                '>
                    <h3 style='color: #009B3A; margin-bottom: 1rem;'>✅ Validadas</h3>
                    <h1 style='color: #009B3A; font-size: 3rem; margin: 0;'>{stats['validadas']}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style='
                    background: white;
                    padding: 2rem;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid #FF7F00;
                    text-align: center;
                '>
                    <h3 style='color: #FF7F00; margin-bottom: 1rem;'>⏳ Pendentes</h3>
                    <h1 style='color: #FF7F00; font-size: 3rem; margin: 0;'>{stats['pendentes']}</h1>
                </div>
                """, unsafe_allow_html=True)
    
    elif "Triagens Pendentes" in menu or "Todas as Triagens" in menu:
        filtro = "pendentes" if "Pendentes" in menu else "todas"
        titulo = "Triagens Pendentes" if "Pendentes" in menu else "Todas as Triagens"
        
        st.markdown(f"""
        <div style='
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #003B71;
            margin-bottom: 2rem;
        '>
            <h2 style='color: #003B71; margin: 0;'>📋 {titulo}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        df = obter_triagens(filtro)
        
        if not df.empty:
            for _, row in df.iterrows():
                border_color = "#009B3A" if row['validado'] == 1 else "#FF7F00"
                status_text = "✅ Validada" if row['validado'] == 1 else "⏳ Pendente"
                
                st.markdown(f"""
                <div style='
                    background: white;
                    padding: 1.5rem;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid {border_color};
                    margin-bottom: 1rem;
                '>
                    <h4 style='color: #003B71; margin-bottom: 0.5rem;'>ID: {row['id'][:8]}... | {status_text}</h4>
                    <p style='margin: 0.25rem 0; color: #58595B;'><strong>Data:</strong> {row['data_hora']}</p>
                    <p style='margin: 0.25rem 0; color: #58595B;'><strong>Sintomas:</strong> {row['sintomas'][:100]}...</p>
                </div>
                """, unsafe_allow_html=True)
                
                if row['validado'] == 0:
                    if st.button(f"✅ Validar triagem {row['id'][:8]}", key=f"validar_{row['id']}"):
                        st.session_state.triagem_selecionada = row['id']
                        
                        st.markdown("### 📝 Validação da Triagem")
                        feedback = st.text_area("Feedback do especialista:")
                        
                        if st.button("✅ Confirmar Validação"):
                            if validar_triagem(row['id'], st.session_state.usuario, feedback):
                                st.success("✅ Triagem validada com sucesso!")
                                st.rerun()
        else:
            st.info("ℹ️ Nenhuma triagem encontrada.")
    
    elif "Banco de Conhecimento" in menu:
        st.markdown("""
        <div style='
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #003B71;
            margin-bottom: 2rem;
        '>
            <h2 style='color: #003B71; margin: 0;'>📚 Banco de Conhecimento</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("🚧 Funcionalidade em desenvolvimento - Visualização de casos validados e padrões identificados.")
    
    elif "Exportar Dados" in menu:
        st.markdown("""
        <div style='
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #003B71;
            margin-bottom: 2rem;
        '>
            <h2 style='color: #003B71; margin: 0;'>📤 Exportar Dados</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Gerar CSV", use_container_width=True):
            csv_data = exportar_csv()
            if csv_data:
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"triagens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

# Rodapé
st.markdown("---")
st.markdown("""
<div style='
    text-align: center;
    font-family: Montserrat, sans-serif;
    color: #58595B;
    padding: 2rem 0;
'>
    <p style='margin: 0.5rem 0; font-weight: bold;'>Sistema de Validação de Triagens Clínicas</p>
    <p style='margin: 0.5rem 0;'>Hospital de Clínicas de Ijuí</p>
    <p style='margin: 0.5rem 0;'>© 2025 - Todos os direitos reservados</p>
</div>
""", unsafe_allow_html=True)
