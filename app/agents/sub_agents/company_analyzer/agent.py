from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools.crew_tools import WebSearchTool
import logging

logger = logging.getLogger(__name__)

class CompanyAnalyzerAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI, web_search: WebSearchTool):
        self.llm = llm
        self.web_search = web_search

    def create_agent(self) -> Agent:
        """Create and return the company analyzer agent."""
        logger.info("Creating Company Analyzer Agent")
        return Agent(
            role='Company Reliability Analyst',
            goal='Analyze company-level information and reliability metrics',
            backstory="""You are a seasoned company analyst specializing in evaluating business 
            reliability and market position. You focus on company-level information such as 
            corporate history, legal issues, safety records, and market standing. You do NOT 
            analyze specific product reviews or customer experiences.""",
            tools=[self.web_search],
            llm=self.llm,
            verbose=True
        ) 