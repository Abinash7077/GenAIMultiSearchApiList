import asyncio
from fastapi import APIRouter, HTTPException
from .models import SearchRequest, SearchResponse
from .service import SearchService

router = APIRouter()
service = SearchService()

@router.post("/query", response_model=SearchResponse)
async def search_query(request: SearchRequest):
    """
    Main search endpoint - handles general queries
    """
    try:
        result = await service.perform_search(request.query)
        return SearchResponse(
            ok=True,
            query=request.query,
            response=result
        )
    except Exception as e:
        return SearchResponse(
            ok=False,
            query=request.query,
            response=f"Error: {str(e)}"
        )

@router.get("/status")
async def get_status():
    """Check search engine status"""
    return {
        "status": "operational",
        "model": "gemini-3-flash-preview"
    }
