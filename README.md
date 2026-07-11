## Personal Info

Jetesada Kaewmanee 2026

## Video Link

https://youtu.be/sgGNflQutOw

## Installation and Environment Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Fill in `.env`:

```bash
API_KEY=your_api_key
OPENROUTER_MODEL=qwen/qwen3.6-27b
OPENROUTER_BASE_URL=https://ai.psu.blue/v1
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
```

## Execution

```bash
uvicorn app.main:app --reload
```

- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`
- LINE webhook URL: `https://your-tunnel-domain/line/webhook`

## LINE Setup

1. Set `LINE_CHANNEL_SECRET` and `LINE_CHANNEL_ACCESS_TOKEN` in `.env`.
2. Expose this application through a public HTTPS URL.
3. Set the Messaging API webhook URL to
   `https://your-domain/line/webhook` in LINE Developers Console.
4. Enable **Use webhook**, then click **Verify**.
5. Add the LINE Official Account as a friend and send a text message.

The webhook verifies `x-line-signature`, accepts text message events, retrieves
document context, calls the LLM, and replies using the event's one-time
`reply_token`.

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/documents` | Upload one `.pdf` or `.txt` file using form field `file` |
| `POST` | `/chat` | Ask a question with optional conversation context |
| `POST` | `/line/webhook` | Receive LINE webhook events and reply to text messages |

## Examples

Upload a document:

```bash
curl -F "file=@src/REPORT2568.pdf" http://127.0.0.1:8000/documents
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"demo-user","message":"ห้วยกรอกเคียน สนับสนุนพื้นที่เศรษฐกิจใด"}'
```

Ask a follow-up using the same `conversation_id`:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id":"demo-user","message":"แล้วมีความจุเท่าไร"}'
```

## Code References

The implementation was written for this project. The following official
documentation and examples were used as references:

| Area | Reference | Used in |
|---|---|---|
| Python style | [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) | Imports, naming, spacing, comments, and docstrings |
| FastAPI file uploads | [FastAPI: Request Files](https://fastapi.tiangolo.com/tutorial/request-files/) | Single `UploadFile` handling in `app/main.py` |
| RAG workflow | [LangChain: Build a semantic search engine](https://docs.langchain.com/oss/python/langchain/knowledge-base) and (https://github.com/GiovanniPasq/agentic-rag-for-dummies/blob/main/notebooks/agentic_rag.ipynb) | Document loading, splitting, embedding, and retrieval in `app/rag.py` |
| PDF loading | [LangChain: Document loaders](https://docs.langchain.com/oss/python/integrations/document_loaders/) | `PyPDFLoader` in `app/rag.py` |
| Text splitting | [LangChain: Recursive text splitter](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter) | `RecursiveCharacterTextSplitter` in `app/rag.py` |
| Embeddings | [LangChain: Embedding integrations](https://docs.langchain.com/oss/python/integrations/embeddings/) | `HuggingFaceEmbeddings` in `app/rag.py` |
| Vector search | [LangChain: Vector stores](https://docs.langchain.com/oss/python/integrations/vectorstores/) | FAISS indexing and semantic retrieval in `app/rag.py` |
| Chat message roles | [LangChain: Messages](https://docs.langchain.com/oss/python/langchain/messages) | `system`, `user`, and `assistant` message history passed to the LLM in `app/llm.py` |
| Chunk sizing | [How to Set the Chunk Size in Document Splitter](https://www.youtube.com/watch?v=1bbDH3kyf9I&t=282s) | Initial chunk-size learning reference |
| Async HTTP | [HTTPX: Async Support](https://www.python-httpx.org/async/) | `AsyncClient` in `app/llm.py` |
| LINE SDK | [LINE Bot SDK for Python](https://github.com/line/line-bot-sdk-python) | Webhook parsing and message replies in `app/line.py` |
| LINE webhook security | [LINE: Verify webhook signature](https://developers.line.biz/en/docs/messaging-api/verify-webhook-signature/) | `x-line-signature` validation in `app/line.py` |
| LINE conversation scope | [LINE: Webhook source objects](https://developers.line.biz/en/reference/messaging-api/#source-user) | `userId`, `groupId`, and `roomId` used to separate LINE conversation history |

and orther from private repo from my old project with my partner