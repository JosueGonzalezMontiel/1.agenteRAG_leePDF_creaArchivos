# app/main.py
# Script principal que orquesta la memoria, el LLM, el prompt (reglas) y el ciclo interactivo.

from app.memory import cargar_memoria, guardar_memoria, limitar_historial, resumir_si_necesario
from app.agent_core import Agent
from app.rag.loader import cargar_documentos
from app.rag.embeddings import obtener_embedding
from app.rag.vector_store import agregar_documento, ya_indexado


from app.config import SYSTEM_PROMPT
# AGENTE
agent = Agent(SYSTEM_PROMPT)

# MEMORIA
messages = cargar_memoria()

# RAG (INDEXACIÓN)
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
    
    respuesta = agent.run(user_input, messages)

    print(f"Asistente: {respuesta}\n")