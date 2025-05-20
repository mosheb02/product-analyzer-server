from app.services.google_ai import GoogleAIService
from app.services.tavily_service import TavilyService
from typing import Dict, Any
import json

class CompanyAnalyzerAgent:
    def __init__(self):
        self.ai_service = GoogleAIService()
        self.tavily_service = TavilyService()

    async def analyze_company(self, product_url: str) -> Dict[str, Any]:
        # Fetch company information from Tavily
        company_data = await self.tavily_service.search_company_info(product_url)
        print(f"********** Company data: {company_data}")
        company_json = json.loads(company_data)

        if 'error' in company_data:
            return {
                'error': company_data['error'],
                'timestamp': company_data['timestamp']
            }

        prompt = f"""
        Analyze the following company information and provide a comprehensive analysis:

        Company: {company_json['company_name']}
        Company Data: {company_json['company_data']}
        Raw Content: {json.dumps(company_json['raw_content'], indent=2)}

        Please provide a structured analysis including:
        1. Company name
        2. Years in market (if available)
        3. Any safety issues or recalls
        4. Notable lawsuits or legal issues
        5. Reliability score (0-1 scale, based on company history and reputation)
        6. Market position and reputation

        Format your response as a JSON object with these exact keys:
        {{
            "company_name": string,
            "years_in_market": int,
            "safety_issues": [string],
            "lawsuits": [string],
            "reliability_score": float,
            "market_position": string
        }}
        make sure to return a valid parserable json object!!!!
        """
        
        result = await self.ai_service.analyze_text(prompt)
        
        if 'error' in result:
            return result
            
        try:
            # Parse the AI response as JSON
            analysis = json.loads(result['content'])
            return {
                'content': analysis,
                'timestamp': result['timestamp']
            }
        except json.JSONDecodeError:
            return {
                'error': 'Failed to parse AI response as JSON',
                'timestamp': result['timestamp']
            } 