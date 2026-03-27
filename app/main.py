# app/main.py
# Script principal que orquesta la memoria, el LLM, el prompt (reglas) y el ciclo interactivo.

from app.memory import cargar_memoria, guardar_memoria, limitar_historial, resumir_si_necesario
from app.llm import generar_respuesta
from app.agent import procesar_respuesta
from app.rag.loader import cargar_documentos
from app.rag.embeddings import obtener_embedding
from app.rag.vector_store import agregar_documento, ya_indexado

messages = cargar_memoria()

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
- NO agregues texto adicional ni Markdown extra fuera del JSON.
- Escribe el código dentro de prev_text y new_text de forma natural.

Para cualquier otra cosa, responde normal.
"""

# Asegurar que el system prompt siempre esté actualizado con las nuevas herramientas
has_system = any(m.get("role") == "system" for m in messages)
if has_system:
    # Reemplazamos el primer mensaje de sistema con el actualizado
    for m in messages:
        if m.get("role") == "system":
            m["content"] = SYSTEM_PROMPT
            break
else:
    messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

print("🔄 Comprobando documentos...")

docs = cargar_documentos()

# Agrupar chunks por archivo fuente para detectar archivos nuevos
from collections import defaultdict
chunks_por_archivo = defaultdict(list)
for texto, fuente in docs:
    chunks_por_archivo[fuente].append(texto)

nuevos = {f: chs for f, chs in chunks_por_archivo.items() if not ya_indexado(f)}

if nuevos:
    print(f"🔄 Indexando {len(nuevos)} archivo(s) nuevo(s)...")
    for fuente, chunks in nuevos.items():
        print(f"   📄 {fuente}")
        for chunk in chunks:
            emb = obtener_embedding(chunk)
            agregar_documento(chunk, emb, fuente)
    print("✅ Documentos indexados.")
else:
    print("✅ No hay documentos nuevos para indexar.")

while True:
    primera_linea = input("tu: ").strip()
    
    if not primera_linea:
        continue

    if primera_linea.lower() in ["salir", "exit", "adios"]:
        break

    lineas = [primera_linea]
    try:
        import msvcrt
        while msvcrt.kbhit():
            linea = input()
            lineas.append(linea)
    except ImportError:
        pass

    user_input = "\n".join(lineas)

    messages.append({"role": "user", "content": user_input})

    # --- CICLO INTERNO REACT (Para ejecución secuencial de herramientas) ---
    while True:
        messages = resumir_si_necesario(messages)
        messages = limitar_historial(messages)

        completion = generar_respuesta(messages, stream=False) 
        respuesta = completion.choices[0].message.content
        
        # Procesamos la respuesta para ver si quiso hacer ejecutar una herramienta
        tiene_tools, respuesta_final = procesar_respuesta(respuesta, messages)

        if tiene_tools:
            print(f"\n[Agente ejecutando herramienta...]")
            
            # 1. Guardamos la "intención" (el JSON) del agente en el historial
            messages.append({"role": "assistant", "content": respuesta})
            
            # 2. Le pasamos el resultado de la herramienta para que lo procese en la siguiente vuelta.
            messages.append({"role": "user", "content": f"Resultado de las herramientas:\n{respuesta_final}\n\nCon base en esto, ¿cuál es tu siguiente paso? (escribe JSON si usas otra herramienta; si no, responde al usuario incluyendo las fuentes copiadas exactamente igual si usaste ask_pdf)"})
            
            # El ciclo interno continúa, forzando al LLM a volver a pensar basándose en el resultado que acaba de recibir
        else:
            # Es una respuesta de texto normal
            print(f"Asistente: {respuesta_final}")
            
            # Guardamos la respuesta final en historial
            messages.append({"role": "assistant", "content": respuesta_final})
            guardar_memoria(messages)
            
            # Rompemos el ciclo interno para esperar otro prompt del humano
            break
