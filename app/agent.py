

import json
import re 
# Importamos las herramientas (incluyendo la nueva de RAG: ask_pdf)
from app.tools import TOOLS
from app.logger import logger


def ejecutar_tool(data):
    tool_name = data.get("tool")
    
    tool = TOOLS.get(tool_name)

    if not tool:
        return f"Tool {tool_name} no encontrada"

    try:
        # quitamos la clave "tool" y pasamos lo demás como kwargs
        params = {k: v for k, v in data.items() if k != "tool"}
        return tool(**params)

    except TypeError as e:
        return f"Error en parámetros de la tool {tool_name}: {e}"
    except Exception as e:
        return f"Error ejecutando {tool_name}: {e}"


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
            logger.error("Error ejecutando tool", exc_info=True)
            resultados.append(f"Error: {e}")

    if resultados:
        # Unimos todos los resultados con un separador visual
        respuesta_final = "\n---\n".join(resultados)

        # Retornamos True (hubo herramientas) y los resultados
        return True, respuesta_final

    # Si ningún JSON era una herramienta válida, devolvemos False y la respuesta original
    return False, respuesta