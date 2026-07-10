import httpx
import numpy as np
import numpy as np
import requests
from pathlib import Path
from sentence_transformers import SentenceTransformer
from app.config import Settings

try:
    import faiss
except Exception:
    faiss = None

SYSTEM_PROMPT = """
<system_prompt>
<role>
You are a helpful RAG chatbot for the Royal Irrigation Department annual report.
</role>
<instructions>
    <instruction>Answer in the same language as the user.</instruction>
    <instruction>Use only the provided context.</instruction>
    <instruction>If the context is not enough, say that the uploaded documents do not contain enough information.</instruction>
</instructions>
</system_prompt>
"""
def make_context(chunks: list[dict]) -> str:
    context = ""
    for chunk in chunks:
        context += f"Page {chunk['page_number']}:\n{chunk['text']}\n\n"
    return context.strip()

async def generate_answer(message: str, chunks: list[dict], settings: Settings) -> str:
    
    if not settings.llm_api_key:
        raise ValueError("LLM API key is not set in the environment variables.")
    payload = {
        "model": settings.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{make_context(chunks)}\nQuestion:\n{message}"},
        ],
        "temperature": 0.2, #try 0.1 later
        "stream": False,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except httpx.RequestError as e:
        raise RuntimeError(f"An error occurred while requesting the LLM API: {e}")