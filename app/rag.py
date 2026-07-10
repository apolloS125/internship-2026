from io import BytesIO
from pathlib import Path
import re
from PyPDF2 import PdfReader

KNOWLEDGE_FILE = Path("knowledge.txt")
THAI_MARKS = re.compile(r"[\u0e31\u0e34-\u0e3a\u0e47-\u0e4e]")

documents = []
chunks = []

def chunk_text(text, size=1200):
    text = re.sub("\s+"," ", text).strip()
    
    if not text:
        return []
    
    return [text[i:i + size] for i in range(0, len(text), size)]

def load_knowledge():
    KNOWLEDGE_FILE.touch()
    documents.clear()
    chunks.clear()
    
    text = KNOWLEDGE_FILE.read_text(encoding="utf-8")
    for i, chunk in enumerate(chunk_text(text), start=1):
        chunks.append(
            {
                "document_id": "knowledge",
                "filename": "knowledge.txt",
                "source": f"knowledge.txt chunk {i}",
                "text": chunk,
            }
        )

    if chunks:
        documents.append(
            {
                "document_id": "knowledge",
                "filename": "knowledge.txt",
                "chunks": len(chunks),
            }
        )
