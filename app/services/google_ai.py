import os
from typing import Dict, Any
import google.generativeai as genai
from datetime import datetime
import json

class GoogleAIService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyD_-2oHMj8mcrS82_nt55Htn9EufPNFyUA")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    async def analyze_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"*********STARTING ANALYSIS*********")
        try:
            full_prompt = self._build_prompt(prompt, context)
            print(f"*********STARTING ANALYSIS1*********")
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            print(f"*********STARTING ANALYSIS2*********")
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )
            print(f"*********STARTING ANALYSIS3*********")
            result = {
                "content": response.text,
                "raw_input": full_prompt,
                "raw_output": response.text,
                "timestamp": datetime.utcnow().isoformat()
            }
            print(f"*********STARTING ANALYSIS4*********")
            print(f"Raw input: {full_prompt}")  # Log the raw input
            print(f"*********STARTING ANALYSIS5*********")
            print(f"Result: {result}")
            print(f"Result: {json.dumps(result)}")
            return json.dumps(result)
        except Exception as e:
            result = {
                "error": str(e),
                "raw_input": full_prompt,
                "raw_output": None,
                "timestamp": datetime.utcnow().isoformat()
            }
            print(f"Error raw input: {full_prompt}")  # Log the raw input on error
            return json.dumps(result)

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