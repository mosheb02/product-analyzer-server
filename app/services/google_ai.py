import os
from typing import Dict, Any
import google.generativeai as genai
from datetime import datetime
import json

class GoogleAIService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyCTiMZ-PyxNp2RpiHaanFSvnlpSgv8kVG8")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    async def analyze_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            full_prompt = self._build_prompt(prompt, context)
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )
            
            return {
                "content": response.text,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _build_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        if not context:
            return prompt
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        return f"Context:\n{context_str}\n\nTask:\n{prompt}"

    def _format_response_as_json(self, response_text: str) -> Dict[str, Any]:
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response as JSON", "raw_output": response_text} 