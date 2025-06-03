from fastapi import FastAPI, HTTPException, Depends, status, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import uuid
from datetime import datetime
import os
import torch
from transformers import AutoTokenizer, AutoModel
import chromadb
from dotenv import load_dotenv
import requests
import json

# Initialize FastAPI app
app = FastAPI(
    title="Sistema de Triagem API",
    description="API para o Sistema de Triagem baseado no Protocolo de Manchester",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load tokenizer and model
try:
    tokenizer = AutoTokenizer.from_pretrained("pucpr/biobertpt-clin")
    model = AutoModel.from_pretrained("pucpr/biobertpt-clin")
    model = model.to(device)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    tokenizer = None

# Initialize ChromaDB
try:
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection_name = "triagem_hci"
    
    try:
        collection = chroma_client.get_collection(name=collection_name)
        chroma_client.delete_collection(collection_name)
        collection = chroma_client.create_collection(name=collection_name)
    except ValueError:
        collection = chroma_client.create_collection(name=collection_name)
    except Exception:
        try:
            collection = chroma_client.create_collection(name=collection_name)
        except:
            collection = chroma_client.get_collection(name=collection_name)
except Exception as e:
    print(f"Error initializing ChromaDB: {e}")
    collection = None

# Pydantic models
class TriagemRequest(BaseModel):
    sintomas: str
    classificacao: str = None
    justificativa: str = None
    condutas: str = None

class TriagemProcessar(BaseModel):
    sintomas: str

class TriagemResponse(BaseModel):
    id: str
    sintomas: str
    resposta: str
    classificacao: str
    justificativa: str
    condutas: str
    data_hora: str

class ValidationRequest(BaseModel):
    triagem_id: str
    validado_por: str
    feedback: str

class ValidationResponse(BaseModel):
    success: bool
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[str] = None

# Helper functions (definir ANTES dos endpoints)
async def call_ollama_mistral(prompt: str) -> str:
    """Chama o modelo Mistral via Ollama"""
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 1000
            }
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
        
    except Exception as e:
        print(f"Erro ao chamar Ollama: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar com IA: {str(e)}")

def embed_text(text: str) -> List[float]:
    if tokenizer is None or model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]
    return embeddings.cpu().numpy()[0].tolist()

def process_llm_response(response_text):
    # Extract classification, justification, and recommendations
    classification = ""
    justification = ""
    recommendations = ""
    
    # Clean up the response
    texto_limpo = response_text.replace("assistant:", "").replace("Justificativa:", "").replace("Justificativa", "")
    texto_resposta = texto_limpo.lower()
    
    # Detect classification color
    if "vermelho" in texto_resposta:
        classification = "VERMELHO"
    elif "laranja" in texto_resposta:
        classification = "LARANJA"
    elif "amarelo" in texto_resposta:
        classification = "AMARELO"
    elif "verde" in texto_resposta:
        classification = "VERDE"
    elif "azul" in texto_resposta:
        classification = "AZUL"
    
    # Extract justification and recommendations
    partes = texto_limpo.split("Condutas")
    
    if "Classificação" in partes[0]:
        if "Justificativa" in partes[0]:
            justification = partes[0].split("Justificativa")[1].strip()
        else:
            justification = partes[0].split("Classificação")[1].strip()
            linhas_justificativa = justification.split('\n')
            if len(linhas_justificativa) > 1:
                justification = '\n'.join(linhas_justificativa[1:]).strip()
    else:
        justification = partes[0]
    
    if classification.lower() in justification.lower():
        justification = justification[len(classification):].strip()
        if justification.startswith("-"):
            justification = justification[1:].strip()
    
    if len(partes) > 1:
        recommendations = partes[1].strip()
    
    return classification, justification, recommendations

# Database functions
def init_validation_db():
    conn = sqlite3.connect('./validacao_triagem.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS validacao_triagem (
        id TEXT PRIMARY KEY,
        sintomas TEXT NOT NULL,
        resposta TEXT NOT NULL,
        data_hora TEXT NOT NULL,
        validado INTEGER DEFAULT 0,
        feedback TEXT,
        validado_por TEXT,
        data_validacao TEXT,
        classificacao TEXT,
        justificativa TEXT,
        condutas TEXT
    )
    ''')
    conn.commit()
    conn.close()

def salvar_para_validacao(sintomas, resposta, classificacao="", justificativa="", condutas=""):
    conn = sqlite3.connect('./validacao_triagem.db')
    cursor = conn.cursor()
    triagem_id = str(uuid.uuid4())
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO validacao_triagem (id, sintomas, resposta, data_hora, classificacao, justificativa, condutas) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (triagem_id, sintomas, str(resposta), data_hora, classificacao, justificativa, condutas)
    )
    conn.commit()
    conn.close()
    return triagem_id

def carregar_casos_validados():
    try:
        conn = sqlite3.connect('./validacao_triagem.db')
        cursor = conn.cursor()
        cursor.execute("SELECT sintomas, resposta FROM validacao_triagem WHERE validado = 1")
        casos = cursor.fetchall()
        conn.close()
        return casos
    except Exception as e:
        print(f"Error loading validated cases: {e}")
        return []

def obter_triagens(filtro="todas"):
    conn = sqlite3.connect('./validacao_triagem.db')
    cursor = conn.cursor()
    
    query = "SELECT id, sintomas, resposta, data_hora, validado, feedback, validado_por, data_validacao FROM validacao_triagem"
    
    if filtro == "pendentes":
        query += " WHERE validado = 0"
    elif filtro == "validadas":
        query += " WHERE validado = 1"
        
    query += " ORDER BY data_hora DESC"
    
    cursor.execute(query)
    triagens = cursor.fetchall()
    conn.close()
    
    result = []
    for triagem in triagens:
        result.append({
            "id": triagem[0],
            "sintomas": triagem[1],
            "resposta": triagem[2],
            "data_hora": triagem[3],
            "validado": triagem[4],
            "feedback": triagem[5],
            "validado_por": triagem[6],
            "data_validacao": triagem[7]
        })
    
    return result

def validar_triagem(triagem_id, validado_por, feedback):
    conn = sqlite3.connect('./validacao_triagem.db')
    cursor = conn.cursor()
    data_validacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "UPDATE validacao_triagem SET validado = 1, feedback = ?, validado_por = ?, data_validacao = ? WHERE id = ?",
        (feedback, validado_por, data_validacao, triagem_id)
    )
    conn.commit()
    conn.close()
    return True

def autenticar(username, password):
    usuarios_validos = {
        "admin": "admin",
        "medico": "medico",
        "enfermeiro": "enfermeiro"
    }
    
    if username in usuarios_validos and usuarios_validos[username] == password:
        return True
    return False

# Initialize database
init_validation_db()

# Load validated cases
casos_validados = carregar_casos_validados()

# Insert validated cases into vector database
if collection is not None:
    for i, (sintomas, resposta) in enumerate(casos_validados):
        case_id = f"validated_case_{i}"
        try:
            embedding = embed_text(sintomas)
            collection.add(
                embeddings=[embedding],
                ids=[case_id],
                metadatas=[{"content": sintomas, "resposta": resposta}]
            )
        except Exception as e:
            print(f"Error processing validated case {case_id}: {str(e)}")

# API endpoints
@app.get("/")
async def root():
    return {"message": "Sistema de Triagem API"}

@app.post("/api/processar-triagem")
async def processar_triagem(triagem: TriagemProcessar):
    """Endpoint para apenas processar a triagem (NÃO salva no banco)"""
    try:
        if not triagem.sintomas.strip():
            raise HTTPException(status_code=400, detail="Sintomas são obrigatórios")
        
        temp_id = str(uuid.uuid4())
        
        prompt = f"""Você é um especialista em triagem hospitalar seguindo o Protocolo de Manchester.

Analise os seguintes sintomas e classifique a urgência:
Sintomas: {triagem.sintomas}

Responda EXATAMENTE no seguinte formato:

Classificação
[vermelho|laranja|amarelo|verde|azul]

Justificativa
[Explicação clínica detalhada baseada nos sintomas apresentados]

Condutas
[Procedimentos médicos recomendados, exames e cuidados específicos]"""

        ai_response = await call_ollama_mistral(prompt)
        classificacao, justificativa, condutas = process_llm_response(ai_response)
        
        return {
            "id": temp_id,
            "classificacao": classificacao.lower(),
            "justificativa": justificativa,
            "condutas": condutas,
            "success": True
        }
        
    except Exception as e:
        print(f"Erro ao processar triagem: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/triagem")
async def salvar_triagem(triagem: TriagemRequest):
    """Endpoint para salvar triagem no banco (para validação)"""
    try:
        if not triagem.sintomas.strip():
            raise HTTPException(status_code=400, detail="Sintomas são obrigatórios")
        
        # Salvar no banco de validação
        triagem_id = salvar_para_validacao(
            triagem.sintomas, 
            "Triagem processada",
            triagem.classificacao or "",
            triagem.justificativa or "",
            triagem.condutas or ""
        )
        
        return {
            "success": True,
            "id": triagem_id,
            "message": "Triagem salva com sucesso"
        }
        
    except Exception as e:
        print(f"Erro ao salvar triagem: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")