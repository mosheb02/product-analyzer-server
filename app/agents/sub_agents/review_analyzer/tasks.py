from crewai import Task
from crewai import Agent
import logging

logger = logging.getLogger(__name__)

class ReviewAnalyzerTasks:
    @staticmethod
    def create_review_analysis_task(agent: Agent, product_name: str, product_url: str) -> Task:
        """Create and return the review analysis task."""
        logger.info(f"Creating review analysis task for product: {product_name}")
        return Task(
            description=f"""TASK: Analyze customer reviews for the specific product: {product_name}
            URL: {product_url}
            
            CRITICAL INSTRUCTIONS:
            1. You must ONLY analyze customer reviews and experiences with this specific product
            2. Do NOT analyze company information or general company reliability
            3. Focus on what actual customers are saying about their experiences
            4. Use the web_scrape tool to get reviews from the product URL
            5. Use web_search to find additional customer reviews from other sources
            
            REQUIRED OUTPUT FORMAT:
            {{
                "average_customer_rating": <number between 0-10>,
                "total_reviews_analyzed": <number of reviews analyzed>,
                "customer_sentiment_summary": <"positive", "negative", or "neutral">,
                "key_positive_points": [
                    "<specific positive aspect from reviews>",
                    "<another positive aspect>"
                ],
                "key_negative_points": [
                    "<specific negative aspect from reviews>",
                    "<another negative aspect>"
                ],
                "common_issues": [
                    "<specific issue mentioned in reviews>",
                    "<another common issue>"
                ],
                "overall_product_reliability_score": <number between 0-10>
            }}""",
            agent=agent,
            expected_output="JSON object with review analysis"
        ) 