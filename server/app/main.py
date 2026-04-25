from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.Settings import settings
from app.schemas import AskRequest, AskResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_url.rstrip("/")], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def get_ai_request(data: AskRequest):
    return AskResponse(status="success", answer=f"Получено: {data.text}")

@app.post("/storage")
async def get_sotrage_files():
    pass