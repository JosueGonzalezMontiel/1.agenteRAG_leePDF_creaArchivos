

import json
import os
from app.config import MEMORY_FILE, MAX_MESSAGES, SUMMARY_THRESHOLD
from app.llm import resumir_texto

def cargar_memoria():
    '''
    Esta función lee el disco duro y busca el archivo memoria.json.
    Si existe, lo abre, lee el JSON y lo convierte en una lista de diccionarios de Python.
    Si no existe, devuelve una lista vacía [].
    '''
    # os.path.exists verifica si la ruta del archivo existe de verdad
    if os.path.exists(MEMORY_FILE):

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f) 
    return []

def guardar_memoria(messages):
    '''
    Toma la lista actual de todos los mensajes y la sobrescribe en memoria.json
    '''
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:

        json.dump(messages, f, ensure_ascii=False, indent=2)

def limitar_historial(messages):
    '''
    Borra los mensajes viejos, dejando solo los MAX_MESSAGES más recientes para evitar 
    que se gaste el presupuesto en tokens. Pero asegura no borrar nunca las REGLAS del sistema.
    '''

    system_msgs = [m for m in messages if m.get("role") == "system"]
    resto = [m for m in messages if m.get("role") != "system"]
    
    return system_msgs + resto[-MAX_MESSAGES:]

def resumir_si_necesario(messages):

    if len(messages) < SUMMARY_THRESHOLD:
        return messages

    system_msgs = [m for m in messages if m.get("role") == "system"]
    
    texto = "\n".join([str(m.get("content", "")) for m in messages if m.get("role") != "system"])
    
    resumen = resumir_texto(texto)
    base_system = [system_msgs[0]] if system_msgs else []

    return base_system + [{
        "role": "system",
        "content": f"Resumen previo de la conversación: {resumen}"
    }]