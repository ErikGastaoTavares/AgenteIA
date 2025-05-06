from typing import List
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import streamlit as st
from llama_index.core.llms import ChatMessage
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
import nest_asyncio
import chromadb

# Aplicar nest_asyncio
nest_asyncio.apply()

# Configuração do LLM
llm = Ollama(model="mistral", request_timeout=420.0)
Settings.llm = llm

# Inicializar cliente ChromaDB
chroma_client = chromadb.Client()
collection_name = "triagem_hci"
collections = chroma_client.list_collections()

# Criar ou obter coleção
if collection_name in [col.name for col in collections]:
    collection = chroma_client.get_collection(collection_name)
else:
    collection = chroma_client.create_collection(name=collection_name)

# Interface Streamlit
st.title("Assistente de Triagem Clínica - HCI")

new_case = st.text_area("Descreva os sintomas do paciente na triagem")

if st.button("Classificar e gerar conduta"):
    if new_case:
        with st.spinner("Classificando..."):

            # Carrega apenas agora
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

            # Função de embedding
            def embed_text(text: str) -> List[float]:
                embeddings = model.encode([text], convert_to_tensor=True)
                return embeddings.cpu().numpy()[0].tolist()

            # Carrega casos simulados e popula coleção
            def load_triagem_cases(filepath: str) -> List[str]:
                with open(filepath, "r", encoding="utf-8") as file:
                    return [line.strip() for line in file if line.strip()]

            triagem_cases = load_triagem_cases("casos.txt")

            for i, case in enumerate(triagem_cases):
                embedding = embed_text(case)
                collection.add(embeddings=[embedding], ids=[f"case_{i}"], metadatas=[{"content": case}])

            # Buscar casos similares
            query_embedding = embed_text(new_case)
            results = collection.query(query_embeddings=[query_embedding], n_results=3)
            similar_cases = [metadata["content"] for metadata in results['metadatas'][0]]

            # Construção do prompt
            input_text = f"Sintomas do novo caso: {new_case}\n\nCasos Similares: {' '.join(similar_cases)}"
            messages = [
                ChatMessage(
                    role="system",
                    content="Você é um profissional de saúde responsável pela triagem clínica no Hospital de Clínicas de Ijuí. Seu objetivo é analisar os sintomas do paciente e classificá-lo conforme o protocolo de Manchester, indicando a prioridade de atendimento e orientações clínicas iniciais."
                ),
                ChatMessage(role="user", content=input_text),
                ChatMessage(
                    role="user",
                    content="Com base nos casos similares, forneça a classificação de risco (vermelha, laranja, amarela, verde ou azul), justifique essa classificação e sugira condutas iniciais. Não inclua informações irrelevantes ou fora do contexto clínico."
                ),
            ]

            try:
                resposta = llm.chat(messages)
                st.subheader("Resultado da Triagem")
                st.write(str(resposta))
            except Exception as e:
                st.error(f"Ocorreu um erro ao consultar o modelo: {e}")
    else:
        st.warning("Por favor, insira os sintomas do paciente.")
