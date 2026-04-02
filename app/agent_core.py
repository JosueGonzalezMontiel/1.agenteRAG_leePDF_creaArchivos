from app.memory import *
from app.llm import generar_respuesta
from app.agent import procesar_respuesta

class Agent:

    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    def run(self, user_input, messages):
        # Asegurar system prompt
        has_system = any(m.get("role") == "system" for m in messages)

        if not has_system:
            messages.insert(0, {"role": "system", "content": self.system_prompt})
        else:
            for m in messages:
                if m.get("role") == "system":
                    m["content"] = self.system_prompt
                    break
        
        messages.append({"role": "user", "content": user_input})

        while True:
            messages = resumir_si_necesario(messages)
            messages = limitar_historial(messages)

            completion = generar_respuesta(messages)
            raw = completion.choices[0].message.content

            tiene_tools, respuesta_final = procesar_respuesta(raw, messages)

            if tiene_tools:
                messages.append({"role": "assistant", "content": raw})
                messages.append({
                    "role": "user",
                    "content": f"Resultado:\n{respuesta_final}"
                })
            else:
                messages.append({"role": "assistant", "content": respuesta_final})
                guardar_memoria(messages)
                return respuesta_final