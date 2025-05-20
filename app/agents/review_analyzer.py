from app.services.google_ai import GoogleAIService
from app.services.tavily_service import TavilyService
from typing import Dict, Any
import json

class ReviewAnalyzerAgent:
    def __init__(self):
        self.ai_service = GoogleAIService()
        self.tavily_service = TavilyService()

    async def analyze_reviews(self, product_url: str, product_name: str) -> Dict[str, Any]:
        # First, fetch the reviews data from Tavily using the provided product_name
        reviews_data = await self.tavily_service.search_product_reviews(product_url, product_name)
        
        print(f"********** Reviews data: {reviews_data}")
        reviews_json = json.loads(reviews_data)

        if 'error' in reviews_data:
            return {
                'error': reviews_data['error'],
                'timestamp': reviews_data['timestamp']
            }

        prompt = f"""
        Analyze the following product reviews data and provide a comprehensive analysis:

        Product: {reviews_json['product_name']}
        Reviews Data: {reviews_json['reviews_data']}
        Raw Content: {json.dumps(reviews_json['raw_content'], indent=2)}

        Please provide a structured analysis including:
        1. Average rating (if available in the data)
        2. Total number of reviews analyzed
        3. Sentiment summary (overall tone and common themes)
        4. Key positive points (extract from the reviews)
        5. Key negative points (extract from the reviews)
        6. Overall reliability score (0-1 scale, based on review patterns and sentiment)

        Format your response as a JSON object with these exact keys:
        {{
            "average_rating": float,
            "total_reviews": int,
            "sentiment_summary": string,
            "key_positive_points": [string],
            "key_negative_points": [string],
            "reliability_score": float
        }}
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