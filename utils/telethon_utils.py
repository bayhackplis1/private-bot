# utils/telethon_utils.py
import random
import string
import time

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_session(session_name, api_id, api_hash):
    # Función para obtener la sesión de Telethon
    pass
    