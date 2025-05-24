from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools.crew_tools import WebSearchTool, WebScrapingTool
import logging

logger = logging.getLogger(__name__)

class ReviewAnalyzerAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI, web_search: WebSearchTool, web_scrape: WebScrapingTool):
        self.llm = llm
        self.web_search = web_search
        self.web_scrape = web_scrape

    def create_agent(self) -> Agent:
        """Create and return the review analyzer agent."""
        logger.info("Creating Review Analyzer Agent")
        return Agent(
            role='Customer Review Analyst',
            goal='Analyze and summarize customer reviews and experiences with the specific product',
            backstory="""You are an expert in analyzing customer reviews and product experiences. 
            Your specialty is reading through customer feedback, identifying patterns, and providing 
            actionable insights about specific products. You focus ONLY on what actual customers 
            are saying about their experiences with the product, not about the company in general.""",
            tools=[self.web_search, self.web_scrape],
            llm=self.llm,
            verbose=True
        ) 