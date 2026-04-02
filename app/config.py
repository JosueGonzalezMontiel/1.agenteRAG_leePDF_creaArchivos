import os



# BASE_DIR calcula la ruta absoluta de la carpeta principal de tu proyecto.
# __file__ es una variable especial de Python que contiene la ruta de este archivo (config.py).
# os.path.dirname saca la carpeta padre. Lo llamamos dos veces para salir de la carpeta 'app/' 
# y llegar a la carpeta principal del proyecto ('agentes ia/').
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# MEMORY_FILE es la ruta exacta donde guardaremos el historial de chat.
# os.path.join es mejor que unir strings con '+' porque pone automáticamente las barras correctas
# dependiendo de si estás en Windows (\) o Mac/Linux (/).
MEMORY_FILE = os.path.join(BASE_DIR, "data", "memoria.json")

SAFE_BASE_DIR = os.path.join(BASE_DIR, "workspace")

#crear carpeta si no existe
os.makedirs(SAFE_BASE_DIR, exist_ok=True)

MAX_MESSAGES = 10

# SUMMARY_THRESHOLD: Cuando el historial llegue a este número de mensajes, en lugar de borrar, va a resumirlos.
SUMMARY_THRESHOLD = 15

SYSTEM_PROMPT = """
Eres un asistente que habla español y es concreto.

Tienes acceso a las siguientes herramientas:
1. Listar archivos
2. Leer archivos
3. Editar o crear archivos
4. Consultar información de documentos PDF (RAG)

REGLAS:
- Si el usuario pide ver archivos, listar directorios, leer código, editar/crear archivos, o buscar información en PDFs, SIEMPRE debes usar la herramienta correspondiente.
- NO respondas con texto normal en esos casos, SOLO usa el JSON válido.
- NUNCA uses la característica nativa de herramientas o "Tool Calling" de la API, sólo imprime el texto manualmente.
- SOLO responde en JSON válido EXACTAMENTE en estos formatos, según lo que necesites hacer:

Para listar archivos:
{"tool": "list_files", "directory": "ruta"}

Para leer un archivo:
{"tool": "read_file", "file_path": "ruta"}

Para editar o crear un archivo:
{"tool": "edit_file", "file_path": "ruta", "prev_text": "texto viejo a reemplazar (o null si es nuevo)", "new_text": "texto nuevo"}

Para leer información de PDFs:
{"tool": "ask_pdf", "question": "pregunta clara y especifica sobre la informacion que buscas"}

- IMPORTANTE: Puedes usar múltiples herramientas de forma secuencial.
- IMPORTANTE: Cuando uses "ask_pdf", yo te devolveré un resultado con el contexto de "Fuente principal" y "Fragmento usado". En tu Siguiente Turno, DEBES TRANSCRIBIR EXACTAMENTE el resultado junto a sus fuentes si es la información que el usuario pidió, sin cortarlo ni resumirlo.
- NO agregues texto adicional ni Markdown extra fuera del JSON si usas una herramienta.
- Escribe el código dentro de prev_text y new_text de forma natural.

Para cualquier otra cosa, responde normal sin usar JSON.
"""
