from fastapi import FastAPI,UploadFile,File,HTTPException
from app.config import Settings
from app.schemas import ChatRequest, ChatResponse, DocumentInfo, UploadResponse 
from app import rag

from dotenv import load_dotenv

app = FastAPI(title="Internship-2026")
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

@app.post("/documents", response_model=UploadResponse)
async def upload_documents(files: list[UploadFile] = File(...)) -> UploadResponse:
    records = []

    for file in files:
        try:
            content = await file.read()
            record = rag.parse_upload(file.filename or "upload", content)
            records.append(record)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    return UploadResponse(documents=[DocumentInfo(**record) for record in records])

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    pass