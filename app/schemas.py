from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field()

class ChatResponse(BaseModel):
    message: str = Field()

class DocumentInfo(BaseModel):
    filename: str = Field()
    chunks: int = Field()

class UploadResponse(BaseModel):
    documents: list[DocumentInfo]