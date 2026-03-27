

import json
import re 
# Importamos las herramientas (incluyendo la nueva de RAG: ask_pdf)
from app.tools.file_tools import list_files_in_dir, read_file, edit_file
from app.tools.pdf_tools import ask_pdf


def ejecutar_tool(data):
    '''
    Recibe un diccionario (ya parseado desde JSON) y ejecuta la herramienta correspondiente.
    Devuelve el resultado como string, o None si no es una herramienta válida.
    '''
    tool_name = data.get("tool")

    if tool_name == "list_files":
        directory = data.get("directory", ".")
        return list_files_in_dir(directory)

    elif tool_name == "read_file":
        file_path = data.get("file_path")
        if file_path:
            return read_file(file_path)
        return "Error: no se proporcionó file_path"

    elif tool_name == "edit_file":
        file_path = data.get("file_path")
        prev_text = data.get("prev_text")
        new_text = data.get("new_text")
        if file_path and new_text:
            return edit_file(file_path, prev_text, new_text)
        return "Error: faltan parámetros file_path o new_text"

    elif tool_name == "ask_pdf":
        question = data.get("question")
        if question:
            return ask_pdf(question)
        return "Error: no se proporcionó la pregunta (question)"

    # Si no reconoce la herramienta, devuelve None
    return None


def extraer_jsons(texto):
    '''
    Extrae todos los bloques JSON válidos del texto.
    Maneja tanto un solo JSON como múltiples JSONs (uno por línea).
    Devuelve una lista de diccionarios parseados.
    '''
    resultados = []

    # Primero intentamos parsear todo el bloque como un solo JSON
    start = texto.find('{')
    end = texto.rfind('}')

    if start == -1 or end == -1 or end <= start:
        return resultados

    bloque = texto[start:end+1]

    try:
        # strict=False permite saltos de línea reales dentro de strings (común en LLMs)
        data = json.loads(bloque, strict=False)
        # Si funcionó como un solo JSON, lo devolvemos
        resultados.append(data)
        return resultados
    except json.JSONDecodeError:
        pass

    # Si falló, probablemente hay múltiples JSONs (uno por línea)
    # Dividimos por líneas e intentamos parsear cada una
    for linea in texto.split('\n'):
        linea = linea.strip()
        if not linea or '{' not in linea:
            continue
        try:
            s = linea.find('{')
            e = linea.rfind('}')
            if s != -1 and e != -1 and e > s:
                data = json.loads(linea[s:e+1], strict=False)
                resultados.append(data)
        except json.JSONDecodeError:
            continue

    return resultados


def procesar_respuesta(respuesta, messages):
    '''
    Revisa la 'respuesta' en texto plano enviada por el LLM.
    Ahora soporta múltiples herramientas en una sola respuesta (una por línea).
    Devuelve el resultado final (resultado de la herramienta o la plática normal).
    '''
    # .strip() elimina espacios o saltos de línea al principio y al final del texto.
    respuesta = respuesta.strip()

    # Extraemos todos los JSONs válidos de la respuesta
    jsons = extraer_jsons(respuesta)

    if not jsons:
        # No hay JSONs, es una respuesta normal de texto
        return False, respuesta

    # Ejecutamos cada herramienta encontrada y acumulamos los resultados
    resultados = []
    for data in jsons:
        try:
            resultado = ejecutar_tool(data)
            if resultado is not None:
                resultados.append(resultado)
        except Exception as e:
            print("Error ejecutando tool:", e)
            resultados.append(f"Error: {e}")

    if resultados:
        # Unimos todos los resultados con un separador visual
        respuesta_final = "\n---\n".join(resultados)

        # Retornamos True (hubo herramientas) y los resultados
        return True, respuesta_final

    # Si ningún JSON era una herramienta válida, devolvemos False y la respuesta original
    return False, respuesta