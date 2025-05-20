from app.agents.review_analyzer import ReviewAnalyzerAgent
from app.agents.company_analyzer import CompanyAnalyzerAgent
from typing import Dict, Any
import uuid
from datetime import datetime

class OrchestratorAgent:
    def __init__(self):
        self.review_analyzer = ReviewAnalyzerAgent()
        self.company_analyzer = CompanyAnalyzerAgent()

    async def analyze_product(self, product_url: str, product_name: str) -> Dict[str, Any]:
        analysis_id = str(uuid.uuid4())
        
        try:
            # Execute analysis directly using sub-agents, passing product_name to review_analyzer
            review_result = await self.review_analyzer.analyze_reviews(product_url, product_name)
            company_result = await self.company_analyzer.analyze_company(product_url)
            
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "review_analysis": review_result,
                "company_analysis": company_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "analysis_id": analysis_id,
                "status": "error",
                "error_message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            } 