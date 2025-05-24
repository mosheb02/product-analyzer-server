from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools.crew_tools import WebSearchTool, WebScrapingTool
from app.tools.product_analysis import (
    ProductReviewSearchTool,
    ProductSpecificationTool,
    SafetyAnalysisTool,
    PriceAnalysisTool
)
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ReviewAnalyzerAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI, web_search: WebSearchTool, web_scrape: WebScrapingTool):
        self.llm = llm
        self.web_search = web_search
        self.web_scrape = web_scrape
        # Initialize product analysis tools
        self.review_search = ProductReviewSearchTool()
        self.spec_analyzer = ProductSpecificationTool()
        self.safety_analyzer = SafetyAnalysisTool()
        self.price_analyzer = PriceAnalysisTool()

    def create_agent(self, dry_run: bool = False) -> Agent:
        """Create and return the review analyzer agent."""
        logger.info(f"Creating Review Analyzer Agent (dry_run: {dry_run})")
        
        if dry_run:
            # In dry run mode, we don't need to create a real agent
            return None
            
        return Agent(
            role='Customer Review Analyst',
            goal='Analyze and summarize customer reviews and experiences with the specific product',
            backstory="""You are an expert in analyzing customer reviews and product experiences. 
            Your specialty is reading through customer feedback, identifying patterns, and providing 
            actionable insights about specific products. You focus ONLY on what actual customers 
            are saying about their experiences with the product, not about the company in general.""",
            tools=[
                self.web_search,
                self.web_scrape,
                self.review_search,
                self.spec_analyzer,
                self.safety_analyzer,
                self.price_analyzer
            ],
            llm=self.llm,
            verbose=True
        )

    def generate_mock_analysis(self, product_name: str) -> Dict[str, Any]:
        """Generate a mock review analysis for testing."""
        logger.info(f"Generating mock review analysis for: {product_name}")
        return {
            "average_customer_rating": 8.5,
            "total_reviews_analyzed": 150,
            "customer_sentiment_summary": "positive",
            "key_positive_points": [
                "Excellent build quality",
                "Great value for money",
                "Easy to use",
                "Reliable performance",
                "Good customer support"
            ],
            "key_negative_points": [
                "Some minor quality control issues",
                "Documentation could be better",
                "Slightly expensive"
            ],
            "common_issues": [
                "Occasional software glitches",
                "Some users report shipping delays",
                "Minor assembly issues"
            ],
            "overall_product_reliability_score": 8.5,
            "safety_analysis": {
                "safety_score": 9.0,
                "certifications": ["CE", "UL", "RoHS"],
                "safety_features": [
                    "Overload protection",
                    "Automatic shutoff",
                    "Child safety lock"
                ]
            },
            "price_analysis": {
                "value_score": 8.5,
                "price_range": {
                    "min": 89.99,
                    "max": 129.99,
                    "average": 109.99
                }
            }
        } 