from crewai import Task
from crewai import Agent
import logging

logger = logging.getLogger(__name__)

class CompanyAnalyzerTasks:
    @staticmethod
    def create_company_analysis_task(agent: Agent, product_name: str, product_url: str, brand_name: str = None) -> Task:
        """Create and return the company analysis task."""
        logger.info(f"Creating company analysis task for product: {product_name}, brand: {brand_name}")
        return Task(
            description=f"""TASK: Analyze company information for: {product_name}
            Brand: {brand_name if brand_name else 'Not specified'}
            URL: {product_url}
            
            CRITICAL INSTRUCTIONS:
            1. You must ONLY analyze company-level information
            2. Do NOT analyze specific product reviews or customer experiences
            3. Focus on the company's history, legal issues, safety records, and market position
            
            AVAILABLE TOOLS:
            1. web_search: Use this to find company information from various sources
            2. company_reputation_analyzer: Use this to analyze company reputation and market position
            3. product_specification_analyzer: Use this to understand product specifications
            4. safety_analysis: Use this to check company safety records and recalls
            
            TOOL USAGE GUIDELINES:
            1. Always include the brand name in web_search queries
            2. Use company_reputation_analyzer for comprehensive company analysis
            3. Use safety_analysis to identify any company-level safety issues
            4. Use product_specification_analyzer to understand product quality standards
            
            COMPANY ANALYSIS REQUIREMENTS:
            1. You MUST provide a final_summary: a single sentence (max 50 words) summarizing the most important company findings.
            
            REQUIRED OUTPUT FORMAT:
            {{
                "company_name": "{brand_name if brand_name else 'Not specified'}",
                "years_in_market": "<how long the company has been in business>",
                "safety_issues": "<any reported safety concerns at company level>",
                "legal_issues": "<any legal challenges or lawsuits>",
                "company_reliability_score": <number between 0-10>,
                "market_position": "<company's position in the market>",
                "brand_name": "{brand_name if brand_name else 'Not specified'}",
                "final_summary": "<one-sentence summary of the company findings, max 50 words>"
            }}""",
            agent=agent,
            expected_output="JSON object with company analysis"
        ) 