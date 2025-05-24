from crewai import Task
from crewai import Agent
import logging

logger = logging.getLogger(__name__)

class CompanyAnalyzerTasks:
    @staticmethod
    def create_company_analysis_task(agent: Agent, product_name: str, product_url: str) -> Task:
        """Create and return the company analysis task."""
        logger.info(f"Creating company analysis task for product: {product_name}")
        return Task(
            description=f"""TASK: Analyze company information for: {product_name}
            URL: {product_url}
            
            CRITICAL INSTRUCTIONS:
            1. You must ONLY analyze company-level information
            2. Do NOT analyze specific product reviews or customer experiences
            3. Focus on the company's history, legal issues, safety records, and market position
            4. Use web_search to find company information
            
            REQUIRED OUTPUT FORMAT:
            {{
                "company_name": "<name of the company>",
                "years_in_market": "<how long the company has been in business>",
                "safety_issues": "<any reported safety concerns at company level>",
                "legal_issues": "<any legal challenges or lawsuits>",
                "company_reliability_score": <number between 0-10>,
                "market_position": "<company's position in the market>"
            }}""",
            agent=agent,
            expected_output="JSON object with company analysis"
        ) 