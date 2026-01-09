import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import httpx

# Load .env
load_dotenv()
API_KEY = os.getenv("GENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("GENAI_API_KEY environment variable not set")

# Configure Gemini client with timeout settings
client = genai.Client(
    api_key=API_KEY,
    http_options={
        "timeout": 60  # seconds (INT only)
    }
)


# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    ok: bool
    query: str
    response: str

# Search endpoint with optimized config
@app.post("/search")
async def search(request: SearchRequest):
    try:
        # Generate with faster settings
        response = client.models.generate_content(
            model="gemini-1.5-flash",  # Faster than gemini-3-flash-preview
            contents=request.query,
            config={
                "temperature": 0.7,
                "max_output_tokens": 512,  # Limit response length for speed
                "top_p": 0.95,
                "top_k": 40
            }
        )
        return SearchResponse(
            ok=True,
            query=request.query,
            response=response.text
        )
    except Exception as e:
        return SearchResponse(
            ok=False,
            query=request.query,
            response=f"Error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)