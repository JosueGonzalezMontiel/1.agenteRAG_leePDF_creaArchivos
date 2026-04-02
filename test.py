import sys
from app.api import agent
from app.memory import cargar_memoria

print("Test script started")
messages = []
respuesta = agent.run("quien falto en la semana?", messages)
print("FINAL RESPONSE:", respuesta)
print("MESSAGES HISTORY:")
for m in messages:
    print(m)
