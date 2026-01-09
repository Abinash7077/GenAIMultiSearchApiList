import os
import asyncio
from google import genai

class SearchService:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
        self.model = "gemini-3-flash-preview"

    async def perform_search(self, query: str) -> str:
        system_prompt = """
You are an expert AI assistant similar to ChatGPT.

Rules:
- Give detailed explanations when asked.
- Give short answers for simple questions.
- Provide examples when helpful.
- Provide code when requested.
- Provide advantages & disadvantages when asked.
- Do not force unnecessary formatting.
- Be natural, clear, and professional.
"""

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=[
                {
                    "role": "system",
                    "parts": [{"text": system_prompt}]
                },
                {
                    "role": "user",
                    "parts": [{"text": query}]
                }
            ],
            config={
                "temperature": 0.7,
                "top_p": 0.95,
                "max_output_tokens": 2048
            }
        )

        return response.text
