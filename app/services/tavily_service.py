import os
from typing import Dict, Any, List
import requests
from datetime import datetime
import json

class TavilyService:
    def __init__(self):
        self.api_key = "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"
        self.base_url = "https://api.tavily.com"

    async def search_product_reviews(self, product_url: str, product_name: str) -> Dict[str, Any]:
        try:
            # Use the provided product_name directly
            search_query = f"Amazon reviews for {product_name}"
            response = requests.post(
                f"{self.base_url}/search",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": search_query,
                    "topic": "general",
                    "search_depth": "advanced",
                    "chunks_per_source": 3,
                    "max_results": 10,
                    "include_answer": True,
                    "include_raw_content": True
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Tavily API error: {response.text}")
            else:
                print(f"Tavily API response: {response.text}")
            data = response.json()
            return json.dumps({
                'product_name': product_name,
                'reviews_data': data.get('answer', ''),
                'raw_content': data.get('raw_content', []),
                'timestamp': datetime.utcnow().isoformat()
            })

        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def search_company_info(self, product_url: str) -> Dict[str, Any]:
        try:
            # Extract company name from URL or use the URL itself
            company_name = self._extract_company_name(product_url)
            
            # Search for company information
            search_query = f"Company information, history, and reliability for {company_name}"
            response = requests.post(
                f"{self.base_url}/search",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": search_query,
                    "topic": "general",
                    "search_depth": "advanced",
                    "chunks_per_source": 3,
                    "max_results": 10,
                    "include_answer": True,
                    "include_raw_content": True
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Tavily API error: {response.text}")

            data = response.json()
            return {
                'company_name': company_name,
                'company_data': data.get('answer', ''),
                'raw_content': data.get('raw_content', []),
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _extract_company_name(self, url: str) -> str:
        # This is a simplified version - in production, you'd want to use a more robust method
        try:
            # For Amazon products, we'd need to first get the company name from the product page
            # For now, we'll use a placeholder
            return "Company Name from Product"
        except:
            return "Unknown Company" 