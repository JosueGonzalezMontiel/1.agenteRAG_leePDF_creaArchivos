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

MAX_MESSAGES = 10

# SUMMARY_THRESHOLD: Cuando el historial llegue a este número de mensajes, en lugar de borrar, va a resumirlos.
SUMMARY_THRESHOLD = 15

