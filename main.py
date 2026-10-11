import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq

app = FastAPI()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class PromptModel(BaseModel):
    prompt: str

@app.post("/api/v1/chat")
def procesar_chat(data: PromptModel):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Eres el núcleo de inteligencia de un asistente local en Windows. Responde de forma directa, precisa y concisa."},
                {"role": "user", "content": data.prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
        )
        respuesta = chat_completion.choices[0].message.content
        return {"response": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))