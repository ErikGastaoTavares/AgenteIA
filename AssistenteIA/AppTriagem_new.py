from typing import List # Importa o tipo de dado List usado para anotar funções
import warnings
warnings.filterwarnings("ignore", category=UserWarning) # Ignora mensagens de alerta do tipo UserWarning (apenas para deixar a interface limpa)
import streamlit as st # Importa a biblioteca de interface web Streamlit
from llama_index.core import Settings
from llama_index_llms_ollama.ollama import Ollama
from llama_index.core.llms import ChatMessage # Importa classes do LlamaIndex para usar um modelo de linguagem (LLM)
import nest_asyncio
nest_asyncio.apply()
import chromadb
import sqlite3
from datetime import datetime
import uuid
from pathlib import Path

# ... rest of the code ...
