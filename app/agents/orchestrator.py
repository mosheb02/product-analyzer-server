from crewai import Agent, Task, Crew, Process
from app.services.google_ai import GoogleAIService
from app.tools.crew_tools import WebSearchTool, WebScrapingTool
from typing import Dict, Any
import uuid
from datetime import datetime
import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorAgent:
    def __init__(self):
        logger.info("Initializing OrchestratorAgent")
        self.ai_service = GoogleAIService()
        self.web_search = WebSearchTool()
        self.web_scrape = WebScrapingTool()
        
        # Using the provided API key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key="AIzaSyC9CGxIjXQjBPSPudmZYSiGTC7p44wHF94"
        )
        logger.info("OrchestratorAgent initialized successfully")

    def _parse_agent_result(self, result: str) -> Dict[str, Any]:
        logger.info(f"******Parsing agent result: {result}")
        try:
            # Clean up the result string by removing markdown code blocks
            cleaned_result = result.replace("```json", "").replace("```", "").strip()
            # Parse the cleaned JSON
            parsed_result = json.loads(cleaned_result)
            
            # Calculate grade based on reliability score
            if "reliability_score" in parsed_result:
                score = parsed_result["reliability_score"]
                if isinstance(score, (int, float)):
                    if score >= 9:
                        grade = "A+"
                    elif score >= 8:
                        grade = "A"
                    elif score >= 7:
                        grade = "B+"
                    elif score >= 6:
                        grade = "B"
                    elif score >= 5:
                        grade = "C"
                    else:
                        grade = "D"
                    parsed_result["grade"] = grade
            
            logger.info("Successfully parsed agent result as JSON")
            return parsed_result
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse result as JSON: {str(e)}, returning as raw text")
            return {"error": f"Failed to parse result: {str(e)}"}

    async def analyze_product(self, product_url: str, product_name: str) -> Dict[str, Any]:
        analysis_id = str(uuid.uuid4())
        logger.info(f"Starting product analysis - ID: {analysis_id}, Product: {product_name}, URL: {product_url}")
        
        try:
            # Create CrewAI agents
            logger.info("Creating CrewAI agents")
            review_analyzer = Agent(
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

            company_analyzer = Agent(
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
            logger.info("CrewAI agents created successfully")

            # Create tasks
            logger.info("Creating analysis tasks")
            review_task = Task(
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
                }}
                
                EXAMPLE:
                {{
                    "average_customer_rating": 8.5,
                    "total_reviews_analyzed": 500,
                    "customer_sentiment_summary": "positive",
                    "key_positive_points": [
                        "Excellent picture quality",
                        "Good sound system",
                        "Easy to set up"
                    ],
                    "key_negative_points": [
                        "Expensive compared to competitors",
                        "Some software glitches",
                        "Remote control issues"
                    ],
                    "common_issues": [
                        "Occasional software freezes",
                        "Remote control connectivity problems",
                        "Initial setup can be confusing"
                    ],
                    "overall_product_reliability_score": 8
                }}""",
                agent=review_analyzer
            )

            company_task = Task(
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
                }}
                
                EXAMPLE:
                {{
                    "company_name": "LG Electronics",
                    "years_in_market": "Since 1958",
                    "safety_issues": "Some reported issues with older TV models",
                    "legal_issues": "Past patent disputes and class action lawsuits",
                    "company_reliability_score": 7,
                    "market_position": "Leading manufacturer in premium TV segment"
                }}""",
                agent=company_analyzer
            )
            logger.info("Analysis tasks created successfully")

            # Create and run the crew
            logger.info("Creating and running the crew")
            crew = Crew(
                agents=[review_analyzer, company_analyzer],
                tasks=[review_task, company_task],
                process=Process.sequential,
                verbose=True
            )

            # Execute the analysis
            logger.info("Starting crew execution")
            result = crew.kickoff()
            logger.info(f"Crew execution completed with result type: {type(result)}")
            logger.info(f"Raw crew result: {result}")
            
            if not result:
                logger.error("Crew execution returned empty result")
                return {
                    "analysis_id": analysis_id,
                    "status": "error",
                    "error_message": "Crew execution returned empty result",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Parse and structure the results
            logger.info("Parsing and structuring results")
            logger.info(f"Result type: {type(result)}")
            
            # Initialize results
            review_result = {"error": "No review analysis result"}
            company_result = {"error": "No company analysis result"}
            
            try:
                # Get both task outputs from the crew
                task_outputs = []
                for task in crew.tasks:
                    if hasattr(task, 'output') and task.output:
                        task_outputs.append(task.output)
                
                logger.info(f"Found {len(task_outputs)} task outputs")
                
                # Process each task output
                for output in task_outputs:
                    try:
                        logger.info(f"#############TASK OUTPUT: {output}")
                        # Get the result from the TaskOutput object
                        if hasattr(output, 'result'):                            
                            logger.info(f"+++++++++Processing task output result: {output.result[:200]}...")
                            cleaned_output = output.result.replace("```json", "").replace("```", "").strip()
                            parsed_output = json.loads(cleaned_output)
                            logger.info(f"%%%%%%%%%%%parsed_output: {parsed_output}")

                            # Determine which analysis this is
                            if "average_customer_rating" in parsed_output:
                                logger.info("Found review analysis")
                                review_result = parsed_output
                            elif "company_name" in parsed_output:
                                logger.info("Found company analysis")
                                company_result = parsed_output
                        else:
                            logger.warning("Task output has no result attribute")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse task output: {str(e)}")
                    except Exception as e:
                        logger.error(f"Error processing task output: {str(e)}")
                
                if not task_outputs:
                    logger.warning("No task outputs found")
            except Exception as e:
                logger.error(f"Error processing results: {str(e)}")
            
            # Calculate final grade
            final_grade = "N/A"
            if "overall_product_reliability_score" in review_result and "company_reliability_score" in company_result:
                try:
                    review_score = float(review_result["overall_product_reliability_score"])
                    company_score = float(company_result["company_reliability_score"])
                    avg_score = (review_score + company_score) / 2
                    logger.info(f"Calculated average score: {avg_score}")
                    
                    if avg_score >= 9:
                        final_grade = "A+"
                    elif avg_score >= 8:
                        final_grade = "A"
                    elif avg_score >= 7:
                        final_grade = "B+"
                    elif avg_score >= 6:
                        final_grade = "B"
                    elif avg_score >= 5:
                        final_grade = "C"
                    else:
                        final_grade = "D"
                    logger.info(f"Final grade: {final_grade}")
                except (ValueError, TypeError) as e:
                    logger.error(f"Error calculating final grade: {str(e)}")
                    final_grade = "N/A"
            
            final_result = {
                "analysis_id": analysis_id,
                "status": "completed",
                "review_analysis": review_result,
                "company_analysis": company_result,
                "final_grade": final_grade,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Analysis completed successfully - ID: {analysis_id}")
            return final_result
            
        except Exception as e:
            logger.error(f"Error during crew execution: {str(e)}")
            return {
                "analysis_id": analysis_id,
                "status": "error",
                "error_message": f"Crew execution failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            } 