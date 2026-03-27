# app/rag/vector_store.py
# Guarda y busca embeddings con persistencia en disco
import faiss
import numpy as np
import json
import os

dimension = 384  # all-MiniLM-L6-v2 usa 384

FAISS_PATH = "data/vector_store.index"
META_PATH  = "data/vector_store_meta.json"


if os.path.exists(FAISS_PATH):
    index = faiss.read_index(FAISS_PATH)
else:
    index = faiss.IndexFlatL2(dimension)

# Carga o crea los metadatos
if os.path.exists(META_PATH):
    with open(META_PATH, "r", encoding="utf-8") as f:
        _meta = json.load(f)
    documentos = _meta["documentos"]
    metadatos  = _meta["metadatos"]
    archivos_indexados = set(_meta.get("archivos_indexados", []))
else:
    documentos = []
    metadatos  = []
    archivos_indexados = set()


def _guardar():
    """Persiste el índice FAISS y los metadatos en disco."""
    faiss.write_index(index, FAISS_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "documentos": documentos,
            "metadatos":  metadatos,
            "archivos_indexados": list(archivos_indexados)
        }, f, ensure_ascii=False, indent=2)


def ya_indexado(nombre_archivo):
    """Devuelve True si el archivo ya fue indexado."""
    return nombre_archivo in archivos_indexados


def agregar_documento(texto, embedding, fuente):
    documentos.append(texto)
    metadatos.append(fuente)
    archivos_indexados.add(fuente)

    vector = np.array([embedding]).astype("float32")
    index.add(vector)
    _guardar()


def buscar(query_embedding, k=3):
    if index.ntotal == 0:
        return []

    query_vector = np.array([query_embedding]).astype("float32")
    distancias, indices = index.search(query_vector, k)

    resultados = []
    for i in indices[0]:
        if 0 <= i < len(documentos):
            resultados.append({
                "texto":  documentos[i],
                "fuente": metadatos[i]
            })

    return resultados