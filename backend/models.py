from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TriagemRequest(BaseModel):
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

class Triagem(BaseModel):
    id: str
    sintomas: str
    resposta: str
    data_hora: str
    validado: int
    feedback: Optional[str] = None
    validado_por: Optional[str] = None
    data_validacao: Optional[str] = None

class Estatisticas(BaseModel):
    total: int
    validadas: int
    pendentes: int