# app/llm.py
# Este archivo se encarga de la comunicación directa con la API del modelo de lenguaje (LLM), en este caso Groq.

import os
from groq import Groq
from dotenv import load_dotenv


load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generar_respuesta(messages, stream=True):
    '''
    Esta función envía todo el historial de mensajes (messages) al modelo y pide una respuesta.
    '''
    return client.chat.completions.create(
        model="openai/gpt-oss-120b", 
        messages=messages,           
        temperature=0.7,             
        max_completion_tokens=16384,  
        top_p=1,                     
        reasoning_effort="medium",   
        stream=False,                
    )

def resumir_texto(texto):
    '''
    Esta es una función de utilidad. Crea un pequeño chat independiente donde le decimos al 
    agente que su única tarea es resumir el texto que le estamos pasando.
    Se usa en memory.py para achicar el historial cuando se hace muy largo.
    '''
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        # Aquí estamos creando un mini-historial en "crudo" de un solo mensaje para pedirle el resumen al modelo.
        messages=[{"role": "user", "content": f"Resume el siguiente chat conservando la información crucial:\n{texto}"}]
    )
    # Volvemos solo el contenido de texto puro de su respuesta.
    return completion.choices[0].message.content