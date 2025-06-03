from typing import Dict, Optional

# Simple authentication system
# In a production environment, this should be replaced with a more secure system
# using hashed passwords stored in a database

# Dictionary of valid users and their passwords
usuarios_validos: Dict[str, str] = {
    "admin": "admin",
    "medico": "medico",
    "enfermeiro": "enfermeiro"
}

def autenticar(username: str, password: str) -> bool:
    """
    Authenticate a user with username and password
    
    Args:
        username: The username to authenticate
        password: The password to authenticate
        
    Returns:
        bool: True if authentication is successful, False otherwise
    """
    if username in usuarios_validos and usuarios_validos[username] == password:
        return True
    return False

def get_user_role(username: str) -> Optional[str]:
    """
    Get the role of a user
    
    Args:
        username: The username to get the role for
        
    Returns:
        str: The role of the user, or None if the user doesn't exist
    """
    if username == "admin":
        return "admin"
    elif username == "medico":
        return "medico"
    elif username == "enfermeiro":
        return "enfermeiro"
    return None