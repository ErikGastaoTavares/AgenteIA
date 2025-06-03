import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Optional

# Define the device (GPU if available, otherwise CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Global variables for tokenizer and model
tokenizer = None
model = None

def load_model():
    """
    Load the tokenizer and model for text embedding
    """
    global tokenizer, model
    try:
        tokenizer = AutoTokenizer.from_pretrained("pucpr/biobertpt-clin")
        model = AutoModel.from_pretrained("pucpr/biobertpt-clin")
        model = model.to(device)
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

def embed_text(text: str) -> Optional[List[float]]:
    """
    Convert text to embedding vector
    
    Args:
        text: The text to convert to embedding
        
    Returns:
        List[float]: The embedding vector, or None if there was an error
    """
    global tokenizer, model
    
    if tokenizer is None or model is None:
        if not load_model():
            return None
    
    try:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :]
        return embeddings.cpu().numpy()[0].tolist()
    except Exception as e:
        print(f"Error embedding text: {e}")
        return None