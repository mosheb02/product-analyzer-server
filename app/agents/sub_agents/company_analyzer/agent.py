from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools.crew_tools import WebSearchTool
from app.tools.product_analysis import (
    CompanyReputationTool,
    ProductSpecificationTool,
    SafetyAnalysisTool
)
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CompanyAnalyzerAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI, web_search: WebSearchTool):
        self.llm = llm
        self.web_search = web_search
        # Initialize product analysis tools
        self.reputation_analyzer = CompanyReputationTool()
        self.spec_analyzer = ProductSpecificationTool()
        self.safety_analyzer = SafetyAnalysisTool()

    def create_agent(self, dry_run: bool = False) -> Agent:
        """Create and return the company analyzer agent."""
        logger.info(f"Creating Company Analyzer Agent (dry_run: {dry_run})")
        
        if dry_run:
            # In dry run mode, we don't need to create a real agent
            return None
            
        return Agent(
            role='Company Reliability Analyst',
            goal='Analyze company-level information and reliability metrics',
            backstory="""You are a seasoned company analyst specializing in evaluating business 
            reliability and market position. You focus on company-level information such as 
            corporate history, legal issues, safety records, and market standing. You do NOT 
            analyze specific product reviews or customer experiences.""",
            tools=[
                self.web_search,
                self.reputation_analyzer,
                self.spec_analyzer,
                self.safety_analyzer
            ],
            llm=self.llm,
            verbose=True
        )

    def generate_mock_analysis(self, product_name: str) -> Dict[str, Any]:
        """Generate a mock company analysis for testing."""
        logger.info(f"Generating mock company analysis for: {product_name}")
        return {
            "company_name": "Example Corp",
            "years_in_market": "15+ years",
            "safety_issues": "No major safety concerns reported",
            "legal_issues": "Minor patent disputes resolved in 2022",
            "company_reliability_score": 8.0,
            "market_position": "Leading manufacturer in the mid-range segment",
            "reputation_analysis": {
                "reputation_score": 8.5,
                "social_media_presence": {
                    "twitter_followers": "10K+",
                    "facebook_likes": "50K+"
                },
                "recent_news": [
                    {
                        "title": "Company Expands Operations",
                        "date": "2024-02-15T00:00:00Z",
                        "sentiment": "positive"
                    }
                ]
            },
            "safety_analysis": {
                "safety_score": 9.0,
                "certifications": ["CE", "UL", "RoHS"],
                "safety_features": [
                    "Quality control system",
                    "Safety testing protocols",
                    "Compliance monitoring"
                ]
            }
        } 