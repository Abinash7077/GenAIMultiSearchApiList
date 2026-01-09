
import os
import asyncio
import uuid
from typing import List, Dict
from google import genai
import PyPDF2
from io import BytesIO

class KnowledgeChatbotService:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
        self.model = "gemini-3-flash-preview"
        
        # In-memory knowledge base (simple implementation)
        # In production, use a vector database like Pinecone, Weaviate, or Chroma
        self.knowledge_base: Dict[str, Dict] = {}
    
    async def add_document(self, filename: str, content: bytes) -> str:
        """Add document to knowledge base"""
        doc_id = str(uuid.uuid4())
        
        # Extract text based on file type
        if filename.endswith('.pdf'):
            text = self._extract_pdf_text(content)
        else:  # txt file
            text = content.decode('utf-8')
        
        # Store document
        self.knowledge_base[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "content": text,
            "chunks": self._chunk_text(text)
        }
        
        return doc_id
    
    def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            raise Exception(f"Failed to extract PDF text: {str(e)}")
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks for better retrieval"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def _search_relevant_chunks(self, question: str, top_k: int = 3) -> List[str]:
        """
        Simple keyword-based search for relevant chunks
        In production, use vector embeddings and similarity search
        """
        all_chunks = []
        
        for doc in self.knowledge_base.values():
            for chunk in doc["chunks"]:
                all_chunks.append({
                    "text": chunk,
                    "source": doc["filename"]
                })
        
        if not all_chunks:
            return []
        
        # Simple keyword matching (case-insensitive)
        question_words = set(question.lower().split())
        
        scored_chunks = []
        for chunk_data in all_chunks:
            chunk_words = set(chunk_data["text"].lower().split())
            score = len(question_words.intersection(chunk_words))
            scored_chunks.append((score, chunk_data))
        
        # Sort by score and get top_k
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        
        return [chunk_data["text"] for score, chunk_data in scored_chunks[:top_k]]
    
    async def answer_question(self, question: str) -> str:
        """Answer question using RAG approach"""
        
        # Check if knowledge base is empty
        if not self.knowledge_base:
            return "⚠️ Knowledge base is empty. Please upload documents first using /api/chatbot/upload"
        
        # Retrieve relevant chunks
        relevant_chunks = self._search_relevant_chunks(question, top_k=3)
        
        if not relevant_chunks:
            return "I couldn't find relevant information in the knowledge base to answer your question."
        
        # Build context from retrieved chunks
        context = "\n\n".join([f"[Context {i+1}]:\n{chunk}" 
                               for i, chunk in enumerate(relevant_chunks)])
        
        # Create RAG prompt
        rag_prompt = f"""
You are a helpful AI assistant that answers questions based ONLY on the provided context.

Context from knowledge base:
{context}

User Question: {question}

Instructions:
- Answer the question using ONLY information from the provided context
- If the context doesn't contain enough information, say so honestly
- Be concise and accurate
- Cite which context section you used if relevant
- DO NOT make up information or use external knowledge

Answer:
"""
        
        # Generate response
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=rag_prompt,
            config={
                "temperature": 0.3,  # Lower temperature for factual answers
                "max_output_tokens": 600
            }
        )
        
        return response.text
    
    def list_documents(self) -> List[Dict]:
        """List all documents in knowledge base"""
        return [
            {
                "id": doc["id"],
                "filename": doc["filename"],
                "size": len(doc["content"])
            }
            for doc in self.knowledge_base.values()
        ]
    
    async def delete_document(self, doc_id: str):
        """Delete document from knowledge base"""
        if doc_id not in self.knowledge_base:
            raise Exception(f"Document {doc_id} not found")
        
        del self.knowledge_base[doc_id]
    
    def reset(self):
        """Clear entire knowledge base"""
        self.knowledge_base.clear()
    
    def get_current_sources(self) -> List[str]:
        """Get list of document sources"""
        return [doc["filename"] for doc in self.knowledge_base.values()]

