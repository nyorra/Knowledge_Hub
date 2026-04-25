import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .Settings import settings


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_url.rstrip("/")], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

first_mes = "HelloWorld"

@app.get("/main")
async def get_main_page():
    return {
        "status": first_mes,
        "backend_url": settings.client_url
    }

@app.post("/ask")
async def ask_ai(payload: dict):
    user_text = payload.get("text")
    print(f"Дошло до питона: {user_text}")
    return {"answer": f"ИИ получил твой текст: {user_text}"}
