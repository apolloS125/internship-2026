from fastapi import FastAPI, HTTPException, Request, UploadFile
from app import rag
from app.config import Settings
from app.schemas import ChatRequest, ChatResponse, DocumentInfo, UploadResponse
from app.line import parse_line_events, reply_to_line
from app.llm import generate_answer

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
rag.load_knowledge()
load_default_pdf()

# Reference: https://fastapi.tiangolo.com/tutorial/request-files/
@app.post("/documents", response_model=UploadResponse)
async def upload_document(file: UploadFile):
    filename = (file.filename or "").lower()

    if not filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are allowed.")
    content = await file.read()
    record = rag.parse_upload(file.filename or "upload", content)

    return UploadResponse(documents=[DocumentInfo(**record)])

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        return ChatResponse(message="Please provide a message to chat.")

    relevant_chunks = rag.search(message, limit=5)

    try:
        answer = await generate_answer(message, relevant_chunks, settings)
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    return ChatResponse(message=answer)

# Reference: https://github.com/line/line-bot-sdk-python
@app.post("/line/webhook")
async def line_webhook(request: Request) -> dict:
    events = await parse_line_events(request, settings)
    for event in events:
        message = event.message.text.strip()

        if not message or not event.reply_token:
            continue

        relevant_chunks = rag.search(message, limit=5)

        try:
            answer = await generate_answer(message, relevant_chunks, settings)
        except (ValueError, RuntimeError):
            answer = "please try again later. The LLM service is currently unavailable."

        try:
            await reply_to_line(event.reply_token, answer, settings)
        except RuntimeError as error:
            raise HTTPException(status_code=502, detail=str(error)) from error
    return {"status": "ok",}
