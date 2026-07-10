from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()
@dataclass
@dataclass(frozen=True)
class Settings:
    llm_api_key: str | None = os.getenv("API_KEY")
    model: str = os.getenv("OPENROUTER_MODEL", "qwen/qwen3.6-27b")
    base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://ai.psu.blue/v1")
    line_channel_secret: str | None = os.getenv("LINE_CHANNEL_SECRET")
    line_channel_access_token: str | None = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    pdf_path: Path = Path(os.getenv("REFERENCE_PDF_PATH", "src/REPORT2568.pdf"))
    page_start: int = int(os.getenv("REFERENCE_PAGE_START", "30"))
    page_end: int = int(os.getenv("REFERENCE_PAGE_END", "50"))
