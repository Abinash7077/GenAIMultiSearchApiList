
from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question")

class ChatResponse(BaseModel):
    ok: bool
    question: str
    answer: str
    sources: List[str] = []

class DocumentUploadResponse(BaseModel):
    ok: bool
    message: str
    document_id: str
    filename: str