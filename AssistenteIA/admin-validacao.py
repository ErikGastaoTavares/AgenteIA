import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List

# Configuração da página
st.set_page_config(
    page_title="Painel de Administração - Validação de Triagens",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        df = pd.read_sql_query(query, conn, params=(triagem_id,))
        conn.close()
        
        if df.empty:
            return None
        
        return df.iloc[0]
    except Exception as e:
        st.error(f"Erro ao obter triagem: {e}")
        conn.close()
        return None

# Função para converter texto em embedding
@st.cache_resource
def carregar_modelo_embedding():
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def embed_text(text: str) -> List[float]:
    model = carregar_modelo_embedding()
    embeddings = model.encode([text], convert_to_tensor=True)
    return embeddings.cpu().numpy()[0].tolist()

# Função para adicionar caso validado ao banco de dados vetorial
def adicionar_caso_validado(sintomas, resposta, feedback):
    try:
        # Conectar ao ChromaDB
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection_name = "triagem_hci"
        
        # Verificar se a coleção existe
        collections = chroma_client.list_collections()
        if collection_name in [col.name for col in collections]:
            collection = chroma_client.get_collection(collection_name)
        else:
            collection = chroma_client.create_collection(name=collection_name)
        
        # Extrair a classificação da resposta
        classificacao = ""
        if "vermelha" in resposta.lower():
            classificacao = "Vermelha"
        elif "laranja" in resposta.lower():
            classificacao = "Laranja"
        elif "amarela" in resposta.lower():
            classificacao = "Amarela"
        elif "verde" in resposta.lower():
            classificacao = "Verde"
        elif "azul" in resposta.lower():
            classificacao = "Azul"
        
        # Criar um caso formatado para adicionar ao banco
        caso_formatado = f"{sintomas} Classificação: {classificacao}."
        if feedback:
            caso_formatado += f" Feedback especialista: {feedback}"
        
        # Gerar embedding para o caso
        embedding = embed_text(caso_formatado)
        
        # Gerar ID único para o caso validado
        caso_id = f"validated_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Adicionar ao banco vetorial
        collection.add(
            embeddings=[embedding],
            ids=[caso_id],
            metadatas=[{"content": caso_formatado, "validated": True}]
        )
        
        return True, caso_id
    except Exception as e:
        st.error(f"Erro ao adicionar caso validado: {e}")
        return False, None

# Função para validar uma triagem
def validar_triagem(triagem_id, validado_por, feedback):
    conn = conectar_bd()
    if conn is None:
        return False
    
    try:
        # Obter os dados da triagem
        triagem = obter_triagem(triagem_id)
        if triagem is None:
            return False
        
        # Adicionar ao banco vetorial se validado positivamente
        sucesso_adicao, caso_id = adicionar_caso_validado(
            triagem['sintomas'], 
            triagem['resposta'], 
            feedback
        )
        
        # Atualizar o status no banco de dados SQLite
        cursor = conn.cursor()
        data_validacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Adicionar o ID do caso no ChromaDB ao feedback
        feedback_completo = feedback
        if sucesso_adicao:
            feedback_completo = f"{feedback}\n\nCaso adicionado ao banco de conhecimento com ID: {caso_id}"
        
        cursor.execute(
            "UPDATE validacao_triagem SET validado = 1, feedback = ?, validado_por = ?, data_validacao = ? WHERE id = ?",
            (feedback_completo, validado_por, data_validacao, triagem_id)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao validar triagem: {e}")
        if conn:
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
        return {}
    
    try:
        cursor = conn.cursor()
        
        # Total de triagens
        cursor.execute("SELECT COUNT(*) FROM validacao_triagem")
        total = cursor.fetchone()[0]
        
        # Triagens validadas
        cursor.execute("SELECT COUNT(*) FROM validacao_triagem WHERE validado = 1")
        validadas = cursor.fetchone()[0]
        
        # Triagens pendentes
        cursor.execute("SELECT COUNT(*) FROM validacao_triagem WHERE validado = 0")
        pendentes = cursor.fetchone()[0]
        
        # Validadores únicos
        cursor.execute("SELECT COUNT(DISTINCT validado_por) FROM validacao_triagem WHERE validado_por IS NOT NULL")
        validadores = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total,
            "validadas": validadas,
            "pendentes": pendentes,
            "validadores": validadores,
            "taxa_validacao": (validadas / total * 100) if total > 0 else 0
        }
    except Exception as e:
        st.error(f"Erro ao obter estatísticas: {e}")
        conn.close()
        return {}

# Função para exportar dados para CSV
def exportar_csv():
    conn = conectar_bd()
    if conn is None:
        return None
    
    try:
        df = pd.read_sql_query("SELECT * FROM validacao_triagem", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao exportar dados: {e}")
        conn.close()
        return None

# Função para obter estatísticas do banco vetorial
def obter_estatisticas_banco_vetorial():
    try:
        # Conectar ao ChromaDB
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        collection_name = "triagem_hci"
        
        # Verificar se a coleção existe
        collections = chroma_client.list_collections()
        if collection_name in [col.name for col in collections]:
            collection = chroma_client.get_collection(collection_name)
            
            # Obter todos os IDs
            todos_ids = collection.get()["ids"]
            
            # Contar casos validados (IDs que começam com "validated_")
            casos_validados = sum(1 for id in todos_ids if id.startswith("validated_"))
            
            # Contar casos originais (IDs que começam com "case_")
            casos_originais = sum(1 for id in todos_ids if id.startswith("case_"))
            
            return {
                "total": len(todos_ids),
                "casos_originais": casos_originais,
                "casos_validados": casos_validados
            }
        else:
            return {
                "total": 0,
                "casos_originais": 0,
                "casos_validados": 0
            }
    except Exception as e:
        st.error(f"Erro ao obter estatísticas do banco vetorial: {e}")
        return {
            "total": 0,
            "casos_originais": 0,
            "casos_validados": 0
        }

# Autenticação simples (em produção, use um sistema mais seguro)
def autenticar(username, password):
    # Em um sistema real, você verificaria as credenciais em um banco de dados seguro
    # Esta é apenas uma demonstração simples
    usuarios_validos = {
        "admin": "admin123",
        "medico": "medico123",
        "enfermeiro": "enfermeiro123"
    }
    
    if username in usuarios_validos and usuarios_validos[username] == password:
        return True
    return False

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
    st.title("🏥 Painel de Administração - Validação de Triagens")
    
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
        
        if submit:
            if autenticar(username, password):
                st.session_state.autenticado = True
                st.session_state.usuario = username
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
    
    # Informações de login para demonstração
    st.info("""
    ### Credenciais para demonstração:
    - **Admin**: admin / admin123
    - **Médico**: medico / medico123
    - **Enfermeiro**: enfermeiro / enfermeiro123
    """)
else:
    # Barra lateral
    with st.sidebar:
        st.title("🏥 Painel de Administração")
        st.write(f"Usuário: **{st.session_state.usuario}**")
        
        # Menu de navegação
        menu = st.radio(
            "Menu",
            ["Dashboard", "Triagens Pendentes", "Todas as Triagens", "Banco de Conhecimento", "Exportar Dados"]
        )
        
        # Filtro para triagens
        if menu in ["Triagens Pendentes", "Todas as Triagens"]:
            st.session_state.filtro = st.radio(
                "Filtrar por",
                ["todas", "pendentes", "validadas"],
                format_func=lambda x: x.capitalize()
            )
        
        # Botão de logout
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.session_state.usuario = ""
            st.rerun()
    
    # Conteúdo principal
    if menu == "Dashboard":
        st.title("Dashboard de Validação")
        
        # Estatísticas
        estatisticas = obter_estatisticas()
        estatisticas_vetorial = obter_estatisticas_banco_vetorial()
        
        if estatisticas:
            # Estatísticas de validação
            st.subheader("Estatísticas de Validação")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Triagens", estatisticas["total"])
            
            with col2:
                st.metric("Triagens Validadas", estatisticas["validadas"])
            
            with col3:
                st.metric("Triagens Pendentes", estatisticas["pendentes"])
            
            # Gráfico de progresso
            st.subheader("Taxa de Validação")
            st.progress(estatisticas["taxa_validacao"] / 100)
            st.write(f"{estatisticas['taxa_validacao']:.1f}% das triagens foram validadas")
            
            # Estatísticas do banco de conhecimento
            st.subheader("Banco de Conhecimento")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Casos", estatisticas_vetorial["total"])
            
            with col2:
                st.metric("Casos Originais", estatisticas_vetorial["casos_originais"])
            
            with col3:
                st.metric("Casos Validados", estatisticas_vetorial["casos_validados"])
            
            # Informações adicionais
            st.subheader("Informações Adicionais")
            st.write(f"Número de validadores ativos: {estatisticas['validadores']}")
        else:
            st.warning("Não foi possível obter estatísticas. Verifique se o banco de dados existe.")
    
    elif menu in ["Triagens Pendentes", "Todas as Triagens"]:
        if menu == "Triagens Pendentes":
            st.title("Triagens Pendentes de Validação")
            st.session_state.filtro = "pendentes"
        else:
            st.title("Todas as Triagens")
        
        # Obter triagens com base no filtro
        triagens = obter_triagens(st.session_state.filtro)
        
        if not triagens.empty:
            # Exibir tabela de triagens
            st.write(f"Total de registros: {len(triagens)}")
            
            # Simplificar a visualização da tabela
            tabela_triagens = triagens.copy()
            tabela_triagens['sintomas'] = tabela_triagens['sintomas'].str[:50] + "..."
            tabela_triagens['resposta'] = tabela_triagens['resposta'].str[:50] + "..."
            
            # Adicionar coluna de status
            tabela_triagens['status'] = tabela_triagens['validado'].apply(
                lambda x: "✅ Validado" if x == 1 else "⏳ Pendente"
            )
            
            # Exibir tabela
            st.dataframe(
                tabela_triagens[['id', 'sintomas', 'data_hora', 'status']],
                use_container_width=True
            )
            
            # Seleção de triagem para visualização detalhada
            triagem_id = st.selectbox(
                "Selecione uma triagem para visualizar detalhes",
                triagens['id'].tolist(),
                format_func=lambda x: f"ID: {x[:8]}... ({triagens[triagens['id'] == x]['data_hora'].values[0]})"
            )
            
            if triagem_id:
                st.session_state.triagem_selecionada = obter_triagem(triagem_id)
                
                if st.session_state.triagem_selecionada is not None:
                    st.subheader("Detalhes da Triagem")
                    
                    # Exibir informações da triagem
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**ID da Triagem:**")
                        st.code(st.session_state.triagem_selecionada['id'])
                        
                        st.write("**Data e Hora:**")
                        st.write(st.session_state.triagem_selecionada['data_hora'])
                        
                        st.write("**Status:**")
                        if st.session_state.triagem_selecionada['validado'] == 1:
                            st.success("Validado")
                            st.write(f"Validado por: {st.session_state.triagem_selecionada['validado_por']}")
                            st.write(f"Data de validação: {st.session_state.triagem_selecionada['data_validacao']}")
                        else:
                            st.warning("Pendente de validação")
                    
                    with col2:
                        if st.session_state.triagem_selecionada['validado'] == 1:
                            st.write("**Feedback:**")
                            st.write(st.session_state.triagem_selecionada['feedback'])
                    
                    # Exibir sintomas e resposta
                    st.subheader("Sintomas do Paciente")
                    st.write(st.session_state.triagem_selecionada['sintomas'])
                    
                    st.subheader("Resposta do Sistema")
                    st.write(st.session_state.triagem_selecionada['resposta'])
                    
                    # Formulário de validação (apenas para triagens pendentes)
                    if st.session_state.triagem_selecionada['validado'] == 0:
                        with st.form("validacao_form"):
                            st.subheader("Validar Triagem")
                            
                            feedback = st.text_area(
                                "Feedback (opcional)",
                                placeholder="Insira seu feedback sobre a classificação e condutas sugeridas..."
                            )
                            
                            adicionar_banco = st.checkbox(
                                "Adicionar ao banco de conhecimento", 
                                value=True,
                                help="Ao validar, este caso será adicionado ao banco de conhecimento para melhorar futuras classificações"
                            )
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                validar = st.form_submit_button("Validar Triagem")
                            
                            with col2:
                                excluir = st.form_submit_button("Excluir Triagem", type="secondary")
                            
                            if validar:
                                if validar_triagem(
                                    st.session_state.triagem_selecionada['id'],
                                    st.session_state.usuario,
                                    feedback
                                ):
                                    st.success("Triagem validada com sucesso! O caso foi adicionado ao banco de conhecimento.")
                                    st.rerun()
                            
                            if excluir:
                                if excluir_triagem(st.session_state.triagem_selecionada['id']):
                                    st.success("Triagem excluída com sucesso!")
                                    st.session_state.triagem_selecionada = None
                                    st.rerun()
                    else:
                        # Opção para excluir triagem validada
                        if st.button("Excluir Triagem"):
                            if excluir_triagem(st.session_state.triagem_selecionada['id']):
                                st.success("Triagem excluída com sucesso!")
                                st.session_state.triagem_selecionada = None
                                st.rerun()
        else:
            if st.session_state.filtro == "pendentes":
                st.info("Não há triagens pendentes de validação.")
            else:
                st.info("Não há triagens registradas no sistema.")
    
    elif menu == "Banco de Conhecimento":
        st.title("Banco de Conhecimento")
        
        # Estatísticas do banco de conhecimento
        estatisticas_vetorial = obter_estatisticas_banco_vetorial()
        
        # Exibir estatísticas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Casos", estatisticas_vetorial["total"])
        
        with col2:
            st.metric("Casos Originais", estatisticas_vetorial["casos_originais"])
        
        with col3:
            st.metric("Casos Validados", estatisticas_vetorial["casos_validados"])
        
        # Informações sobre o banco de conhecimento
        st.subheader("Sobre o Banco de Conhecimento")
        st.write("""
        O banco de conhecimento contém casos clínicos que são utilizados para classificar novos pacientes.
        Ele é composto por casos originais (pré-definidos) e casos validados por especialistas.
        
        Quando uma triagem é validada, ela é adicionada automaticamente ao banco de conhecimento,
        melhorando a precisão das futuras classificações.
        """)
        
        # Visualizar casos do banco (se possível)
        try:
            chroma_client = chromadb.PersistentClient(path="./chroma_db")
            collection_name = "triagem_hci"
            
            if collection_name in [col.name for col in chroma_client.list_collections()]:
                collection = chroma_client.get_collection(collection_name)
                
                # Obter todos os casos
                todos_casos = collection.get()
                
                # Criar DataFrame
                casos_df = pd.DataFrame({
                    "ID": todos_casos["ids"],
                    "Conteúdo": [metadata["content"] for metadata in todos_casos["metadatas"]]
                })
                
                # Adicionar coluna de tipo
                casos_df["Tipo"] = casos_df["ID"].apply(
                    lambda x: "Validado" if x.startswith("validated_") else "Original"
                )
                
                # Filtro de tipo
                tipo_filtro = st.radio(
                    "Filtrar por tipo",
                    ["Todos", "Originais", "Validados"],
                    horizontal=True
                )
                
                if tipo_filtro == "Originais":
                    casos_df = casos_df[casos_df["Tipo"] == "Original"]
                elif tipo_filtro == "Validados":
                    casos_df = casos_df[casos_df["Tipo"] == "Validado"]
                
                # Exibir tabela
                st.dataframe(
                    casos_df,
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Erro ao visualizar casos do banco de conhecimento: {e}")
    
    elif menu == "Exportar Dados":
        st.title("Exportar Dados")
        
        st.write("Exporte os dados de triagem para análise externa ou backup.")
        
        if st.button("Gerar CSV"):
            df = exportar_csv()
            
            if df is not None and not df.empty:
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="Baixar CSV",
                    data=csv,
                    file_name=f"triagens_exportadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("Não foi possível gerar o arquivo CSV.")
        
        # Opções adicionais de exportação
        st.subheader("Outras opções")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Exportar apenas validadas"):
                conn = conectar_bd()
                if conn is not None:
                    df = pd.read_sql_query("SELECT * FROM validacao_triagem WHERE validado = 1", conn)
                    conn.close()
                    
                    if not df.empty:
                        csv = df.to_csv(index=False)
                        
                        st.download_button(
                            label="Baixar CSV (Validadas)",
                            data=csv,
                            file_name=f"triagens_validadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("Não há triagens validadas para exportar.")
        
        with col2:
            if st.button("Exportar apenas pendentes"):
                conn = conectar_bd()
                if conn is not None:
                    df = pd.read_sql_query("SELECT * FROM validacao_triagem WHERE validado = 0", conn)
                    conn.close()
                    
                    if not df.empty:
                        csv = df.to_csv(index=False)
                        
                        st.download_button(
                            label="Baixar CSV (Pendentes)",
                            data=csv,
                            file_name=f"triagens_pendentes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("Não há triagens pendentes para exportar.")

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
        <p>Sistema de Validação de Triagens Clínicas - Hospital de Clínicas de Ijuí</p>
        <p>© 2025 - Todos os direitos reservados</p>
    </div>
    """,
    unsafe_allow_html=True
)
