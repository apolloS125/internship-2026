from fastapi import FastAPI
from app.config import Settings
from app.schemas import ChatRequest, ChatResponse
from app import rag

from dotenv import load_dotenv

app = FastAPI("Internship-2026")
settings = Settings()

def load_default_pdf() -> None:
    if rag.chunks or not settings.pdf_path.exists():
        return

    content = settings.pdf_path.read_bytes()
    rag.add_pdf(
        settings.pdf_path.name,
        content,
        page_start=settings.page_start,
        page_end=settings.page_end,
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    pass