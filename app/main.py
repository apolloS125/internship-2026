from fastapi import FastAPI
from app.config import Settings
from app.schemas import ChatRequest, ChatResponse

from dotenv import load_dotenv

app = FastAPI("Internship-2026")
settings = Settings()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    pass