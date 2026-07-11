import httpx

from app.config import Settings

# Message format reference:
# https://docs.langchain.com/oss/python/langchain/messages
SYSTEM_PROMPT = """
<system_prompt>
<role>
You are a helpful RAG chatbot for the Royal Irrigation Department annual report.
</role>
<instructions>
    <instruction>Answer in the same language as the user.</instruction>
    <instruction>Use only the provided context.</instruction>
    <instruction>If the context is not enough, say that the uploaded documents do not contain enough information.</instruction>
    <instruction>Awlays answer in thai language.</instruction>
</instructions>
</system_prompt>
"""

def make_context(chunks: list[dict]) -> str:
    context = ""
    for chunk in chunks:
        context += f"Page {chunk['page_number']}:\n{chunk['text']}\n\n"
    return context.strip()

async def generate_answer(
    message: str,
    chunks: list[dict],
    settings: Settings,
    history: list[dict] | None = None,
) -> str:
    if not settings.llm_api_key:
        raise ValueError("LLM API key is not set in the environment variables.")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history or [])
    messages.append(
        {
            "role": "user",
            "content": (
                f"Context:\n{make_context(chunks)}\nQuestion:\n{message}"
            ),
        }
    )

    payload = {
        "model": settings.model,
        "messages": messages,
        "temperature": 0.2,
        "stream": False,
    }

    # Reference: https://www.python-httpx.org/async/
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
    except httpx.HTTPError as error:
        raise RuntimeError(
            f"An error occurred while requesting the LLM API: {error}"
        ) from error
