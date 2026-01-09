from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from .models import ChatRequest, ChatResponse, DocumentUploadResponse
from .service import KnowledgeChatbotService

router = APIRouter()
service = KnowledgeChatbotService()

@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question based on uploaded knowledge base
    """
    try:
        answer = await service.answer_question(request.question)
        return ChatResponse(
            ok=True,
            question=request.question,
            answer=answer,
            sources=service.get_current_sources()
        )
    except Exception as e:
        return ChatResponse(
            ok=False,
            question=request.question,
            answer=f"Error: {str(e)}",
            sources=[]
        )

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload document to knowledge base (PDF, TXT)
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.txt')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        # Process and store document
        doc_id = await service.add_document(file.filename, content)
        
        return DocumentUploadResponse(
            ok=True,
            message=f"Document '{file.filename}' uploaded successfully",
            document_id=doc_id,
            filename=file.filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents():
    """List all documents in knowledge base"""
    documents = service.list_documents()
    return {
        "ok": True,
        "count": len(documents),
        "documents": documents
    }

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from knowledge base"""
    try:
        await service.delete_document(doc_id)
        return {"ok": True, "message": "Document deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/reset")
async def reset_knowledge_base():
    """Clear entire knowledge base"""
    service.reset()
    return {"ok": True, "message": "Knowledge base cleared"}

@router.get("/status")
async def get_status():
    """Get chatbot status"""
    return {
        "status": "operational",
        "model": "gemini-3-flash-preview",
        "documents_count": len(service.list_documents()),
        "rag_enabled": True
    }