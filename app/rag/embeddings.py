# app/embeddings.py
#Convierte texto → vector

from sentence_transformers import SentenceTransformer

# modelo ligero y bueno
model = SentenceTransformer('all-MiniLM-L6-v2')

def obtener_embedding(texto):
    return model.encode(texto)