from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")

class SearchResponse(BaseModel):
    ok: bool
    query: str
    response: str