import sqlite3
from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional, Tuple

# Database initialization
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
        data_validacao TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Save triage for validation
def salvar_para_validacao(sintomas: str, resposta: str) -> str:
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

# Load validated cases
def carregar_casos_validados() -> List[Tuple[str, str]]:
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

# Get all triages with optional filter
def obter_triagens(filtro: str = "todas") -> List[Dict[str, Any]]:
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

# Get a specific triage by ID
def obter_triagem(triagem_id: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect('./validacao_triagem.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM validacao_triagem WHERE id = ?", (triagem_id,))
    triagem = cursor.fetchone()
    conn.close()
    
    if triagem:
        return {
            "id": triagem[0],
            "sintomas": triagem[1],
            "resposta": triagem[2],
            "data_hora": triagem[3],
            "validado": triagem[4],
            "feedback": triagem[5],
            "validado_por": triagem[6],
            "data_validacao": triagem[7]
        }
    
    return None

# Validate a triage
def validar_triagem(triagem_id: str, validado_por: str, feedback: str) -> bool:
    try:
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
    except Exception as e:
        print(f"Error validating triage: {e}")
        return False

# Delete a triage
def excluir_triagem(triagem_id: str) -> bool:
    try:
        conn = sqlite3.connect('./validacao_triagem.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM validacao_triagem WHERE id = ?", (triagem_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting triage: {e}")
        return False

# Get statistics
def obter_estatisticas() -> Dict[str, int]:
    try:
        conn = sqlite3.connect('./validacao_triagem.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM validacao_triagem")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM validacao_triagem WHERE validado = 1")
        validadas = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM validacao_triagem WHERE validado = 0")
        pendentes = cursor.fetchone()[0]
        conn.close()
        
        return {
            "total": total,
            "validadas": validadas,
            "pendentes": pendentes
        }
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {"total": 0, "validadas": 0, "pendentes": 0}