from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field()
    conversation_id: str = Field(default="default", min_length=1, max_length=100)

class ChatResponse(BaseModel):
    message: str = Field()

class DocumentInfo(BaseModel):
    filename: str = Field()
    chunks: int = Field()

class UploadResponse(BaseModel):
    documents: list[DocumentInfo]