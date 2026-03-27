# app/loader.py
#carga documentos desde la carpeta data/docs y devuelve una lista de textos
import os
import pypdf

#se agrega para dividir en varios embeddings el texto de un doc
def dividir_en_chunks(texto, tamaño=300, solapamiento=50):
    chunks = []
    inicio = 0

    while inicio < len(texto):  
        fin = inicio + tamaño
        chunk = texto[inicio:fin]
        chunks.append(chunk)
        inicio += tamaño - solapamiento

    return chunks

def cargar_documentos(path="data/docs"):
    textos = []

    for archivo in os.listdir(path):
        ruta = os.path.join(path, archivo)

        if archivo.endswith(".txt"):
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
                #aqui se divide el contenido del doc en chunks para crear varios embeddings
                chunks = dividir_en_chunks(contenido)
                
                
                for chunk in chunks:
                    textos.append((chunk, archivo)) #se guarda el chunk junto con el nombre del archivo como fuente
                
        elif archivo.endswith(".pdf"):
            try:
                with open(ruta, "rb") as f:
                    reader = pypdf.PdfReader(f)
                    contenido = ""
                    for page in reader.pages:
                        texto_pagina = page.extract_text()
                        if texto_pagina:
                            contenido += texto_pagina + "\n"
                chunks = dividir_en_chunks(contenido)
                for chunk in chunks:
                    textos.append((chunk, archivo))
            except Exception as e:
                print(f"⚠️  Error leyendo {archivo}: {e}")

    return textos