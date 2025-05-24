from crewai import Task
from crewai import Agent
import logging

logger = logging.getLogger(__name__)

class ReviewAnalyzerTasks:
    @staticmethod
    def create_review_analysis_task(agent: Agent, product_name: str, product_url: str, brand_name: str = None) -> Task:
        """Create and return the review analysis task."""
        logger.info(f"Creating review analysis task for product: {product_name}, brand: {brand_name}")
        return Task(
            description=f"""TASK: Analyze customer reviews for the specific product: {product_name}
            Brand: {brand_name if brand_name else 'Not specified'}
            URL: {product_url}
            
            CRITICAL INSTRUCTIONS:
            1. You must ONLY analyze customer reviews and experiences with this specific product
            2. Do NOT analyze company information or general company reliability
            3. Focus on what actual customers are saying about their experiences
            4. You MUST find and analyze at least 20 reviews from different sources
            5. If you can't find enough reviews, use web_search to find more sources
            6. Be thorough in identifying both positive and negative aspects
            
            AVAILABLE TOOLS:
            1. web_scrape: Use this to get reviews directly from the product URL
            2. web_search: Use this to find additional customer reviews from other sources
            3. product_review_search: Use this to analyze reviews from multiple sources
            4. product_specification_analyzer: Use this to understand product specifications
            5. safety_analysis: Use this to check product safety records
            6. price_analysis: Use this to assess product value and pricing
            
            TOOL USAGE GUIDELINES:
            1. Always include the brand name in web_search queries
            2. Use product_review_search for comprehensive review analysis
            3. Use safety_analysis to identify any safety concerns
            4. Use price_analysis to assess value for money
            5. Use product_specification_analyzer to understand product features
            
            AGGRESSIVE REVIEW GATHERING STRATEGY:
            1. First, use web_scrape on the product URL to get direct reviews
            2. Then, use web_search with these queries:
               - "{product_name} {brand_name} reviews"
               - "{product_name} {brand_name} customer feedback"
               - "{product_name} {brand_name} problems"
               - "{product_name} {brand_name} complaints"
               - "{product_name} {brand_name} pros and cons"
            3. Use product_review_search to analyze reviews from multiple sources
            4. If still not enough reviews, try:
               - Searching on specific review sites (Amazon, Trustpilot, etc.)
               - Looking for forum discussions
               - Checking social media mentions
            
            REVIEW ANALYSIS REQUIREMENTS:
            1. You MUST identify at least 3 key positive points
            2. You MUST identify at least 3 key negative points
            3. You MUST identify at least 2 common issues
            4. If you can't find enough information, explain why in the output
            5. Include specific quotes from reviews when possible
            6. Consider both recent and older reviews for a complete picture
            7. You MUST provide a final_summary: a single sentence (max 50 words) summarizing the most important review findings.
            
            REQUIRED OUTPUT FORMAT:
            {{
                "average_customer_rating": <number between 0-10>,
                "total_reviews_analyzed": <number of reviews analyzed>,
                "customer_sentiment_summary": <"positive", "negative", or "neutral">,
                "key_positive_points": [
                    "<specific positive aspect from reviews with supporting evidence>",
                    "<another positive aspect with supporting evidence>",
                    "<at least one more positive aspect>"
                ],
                "key_negative_points": [
                    "<specific negative aspect from reviews with supporting evidence>",
                    "<another negative aspect with supporting evidence>",
                    "<at least one more negative aspect>"
                ],
                "common_issues": [
                    "<specific issue mentioned in reviews with frequency>",
                    "<another common issue with frequency>"
                ],
                "review_sources": [
                    "<list of sources where reviews were found>"
                ],
                "overall_product_reliability_score": <number between 0-10>,
                "brand_name": "{brand_name if brand_name else 'Not specified'}",
                "analysis_confidence": <"high", "medium", or "low">,
                "missing_information": <"explanation if any required information is missing">,
                "final_summary": "<one-sentence summary of the review findings, max 50 words>"
            }}""",
            agent=agent,
            expected_output="JSON object with review analysis"
        ) 