from fastapi import FastAPI
from pydantic import BaseModel
from app.agent_core import Agent
from app.memory import cargar_memoria

app = FastAPI()

from app.config import SYSTEM_PROMPT

agent = Agent(system_prompt=SYSTEM_PROMPT)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    messages = cargar_memoria()
    response = agent.run(req.message, messages)
    return {"response": response}