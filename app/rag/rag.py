# app/rag.py
#rag es un enfoque que combina recuperación de información (IR) con generación de lenguaje natural (NLG). En lugar de depender únicamente del conocimiento almacenado en el modelo, RAG permite al modelo recuperar información relevante de una base de datos o corpus externo y luego generar respuestas basadas en esa información.
from app.rag.embeddings import obtener_embedding
from app.rag.vector_store import buscar
from app.llm import generar_respuesta

def responder_con_rag(pregunta):
    # 1. embedding de la pregunta
    query_embedding = obtener_embedding(pregunta)

    # 2. buscar contexto relevante
    docs = buscar(query_embedding)

    contexto = "\n\n".join([d["texto"] for d in docs])
    

    # 3. prompt
    prompt = f"""
Responde SOLO con base en el contexto.

Contexto:
{contexto}

Pregunta:
{pregunta}
"""

    # 4. llamar al LLM
    completion = generar_respuesta(
        [{"role": "user", "content": prompt}],
        stream=False
    )


    respuesta = completion.choices[0].message.content

    # (respuesta + fuentes)
    #  7. mejor resultado
    mejor_doc = docs[0]

    fuente_principal = mejor_doc["fuente"]
    fragmento = mejor_doc["texto"]

    #  opcional: otras fuentes
    otras_fuentes = list(set([d["fuente"] for d in docs]))

    # 8. devolver todo
    return f"""
    {respuesta}

    Fuente principal: {fuente_principal}

    Fragmento usado:
    "{fragmento}"

    Otras fuentes consideradas: {', '.join(otras_fuentes)}
    """
