from io import BytesIO
from pathlib import Path
import re
from PyPDF2 import PdfReader

KNOWLEDGE_FILE = Path("knowledge.txt")
THAI_MARKS = re.compile(r"[\u0e31\u0e34-\u0e3a\u0e47-\u0e4e]")

def save_text(title, text):
    if not text.strip():
        return
    with KNOWLEDGE_FILE.open("a", encoding="utf-8") as file:
        file.write(f"\n\n{title}\n{text.strip()}\n")

def add_pdf(filename, content, page_start=None, page_end=None):
    reader = PdfReader(BytesIO(content))
    total_pages = len(reader.pages)

    page_start = page_start or 1
    page_end = page_end or total_pages
    if page_start > total_pages:
        page_start, page_end = 1, total_pages

    text = ""
    for i in range(page_start, min(page_end, total_pages) + 1):
        page_text = reader.pages[i - 1].extract_text() or ""
        if page_text.strip():
            text += f"{filename} page {i}\n{page_text}\n\n"

    save_text(filename, text)
    return {"filename": filename, "chunks": len(chunk_text(text))}

def chunk_text(text, size=1200):
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [text[i:i + size] for i in range(0, len(text), size)]

def parse_upload(filename, content):
    ext = Path(filename).suffix.lower()

    if ext == ".txt":
        text = content.decode("utf-8", errors="ignore")
        save_text(filename, text)
        return {"filename": filename, "chunks": len(chunk_text(text))}

    if ext == ".pdf":
        return add_pdf(filename, content)

    raise ValueError("Support only .pdf and .txt files")