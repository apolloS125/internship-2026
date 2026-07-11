from pathlib import Path
from tempfile import TemporaryDirectory
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

KNOWLEDGE_FILE = Path("knowledge.txt")
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=120,
)

chunks = []
vector_store = None
embedding_model = None

def get_embeddings():
    global embedding_model

    if embedding_model is None:
        embedding_model = HuggingFaceEmbeddings(
            model_name=MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    return embedding_model

def load_knowledge():
    global chunks, vector_store

    KNOWLEDGE_FILE.touch()
    text = KNOWLEDGE_FILE.read_text(encoding="utf-8")

    if not text.strip():
        chunks = []
        vector_store = None
        return

    document = Document(
        page_content=text,
        metadata={
            "document_id": "knowledge",
            "filename": KNOWLEDGE_FILE.name,
            "source": KNOWLEDGE_FILE.name,
        },
    )

    chunks = text_splitter.split_documents([document])
    vector_store = FAISS.from_documents(chunks, get_embeddings())

def save_text(title, text):
    if not text.strip():
        return
    with KNOWLEDGE_FILE.open("a", encoding="utf-8") as file:
        file.write(f"\n\n{title}\n{text.strip()}\n")

    # Read and embed the updated knowledge again.
    load_knowledge()

def add_pdf(filename, content, page_start=None, page_end=None):
    with TemporaryDirectory() as directory:
        pdf_path = Path(directory, Path(filename).name)
        pdf_path.write_bytes(content)
        documents = PyPDFLoader(str(pdf_path)).load()

    total_pages = len(documents)
    page_start = page_start or 1
    page_end = page_end or total_pages
    if page_start > total_pages:
        page_start = 1
        page_end = total_pages
    selected_pages = documents[page_start - 1 : min(page_end, total_pages)]
    text = ""

    for document in selected_pages:
        if document.page_content.strip():
            page_number = document.metadata["page"] + 1
            text += f"{filename} page {page_number}\n{document.page_content}\n\n"

    save_text(filename, text)
    return {
        "filename": filename,
        "chunks": len(text_splitter.split_text(text)),
    }

def parse_upload(filename, content):
    file_type = Path(filename).suffix.lower()

    if file_type == ".txt":
        text = content.decode("utf-8", errors="ignore")
        save_text(filename, text)
        return {
            "filename": filename,
            "chunks": len(text_splitter.split_text(text)),
        }

    if file_type == ".pdf":
        return add_pdf(filename, content)

    raise ValueError("Support only .pdf and .txt files")

def search(query, limit=5):
    if not query.strip() or limit < 1 or vector_store is None:
        return []
    retriever = vector_store.as_retriever(
        search_kwargs={"k": min(limit, len(chunks))}
    )
    documents = retriever.invoke(query)
    results = []

    for document in documents:
        results.append(
            {
                "document_id": document.metadata.get("document_id", "knowledge"),
                "filename": document.metadata.get("filename", KNOWLEDGE_FILE.name),
                "source": document.metadata.get("source", KNOWLEDGE_FILE.name),
                "page_number": document.metadata.get("page", 0) + 1,
                "text": document.page_content,
            }
        )
    return results