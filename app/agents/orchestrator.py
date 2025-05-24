from crewai import Crew, Process
from app.services.google_ai import GoogleAIService
from app.tools.crew_tools import WebSearchTool, WebScrapingTool
from typing import Dict, Any
import uuid
from datetime import datetime
import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
import os

from app.agents.sub_agents.review_analyzer.agent import ReviewAnalyzerAgent
from app.agents.sub_agents.company_analyzer.agent import CompanyAnalyzerAgent
from app.agents.sub_agents.review_analyzer.tasks import ReviewAnalyzerTasks
from app.agents.sub_agents.company_analyzer.tasks import CompanyAnalyzerTasks

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
        
        # Initialize sub-agents
        self.review_analyzer = ReviewAnalyzerAgent(self.llm, self.web_search, self.web_scrape)
        self.company_analyzer = CompanyAnalyzerAgent(self.llm, self.web_search)
        
        logger.info("OrchestratorAgent initialized successfully")

    def _generate_mock_review_analysis(self, product_name: str) -> Dict[str, Any]:
        """Generate a mock review analysis for testing."""
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
            "overall_product_reliability_score": 8.5
        }

    def _generate_mock_company_analysis(self, product_name: str) -> Dict[str, Any]:
        """Generate a mock company analysis for testing."""
        return {
            "company_name": "Example Corp",
            "years_in_market": "15+ years",
            "safety_issues": "No major safety concerns reported",
            "legal_issues": "Minor patent disputes resolved in 2022",
            "company_reliability_score": 8.0,
            "market_position": "Leading manufacturer in the mid-range segment"
        }

    async def analyze_product(self, product_url: str, product_name: str, brand_name: str = None, dry_run: bool = False) -> Dict[str, Any]:
        analysis_id = str(uuid.uuid4())
        logger.info(f"Starting product analysis - ID: {analysis_id}, Product: {product_name}, Brand: {brand_name}, URL: {product_url}, Dry Run: {dry_run}")
        
        try:
            if dry_run:
                logger.info("Running in dry run mode - generating mock responses")
                review_result = self.review_analyzer.generate_mock_analysis(product_name)
                company_result = self.company_analyzer.generate_mock_analysis(product_name)
                
                # Add brand name to results
                if brand_name:
                    review_result["brand_name"] = brand_name
                    company_result["brand_name"] = brand_name
                    company_result["company_name"] = brand_name
                # Add final_summary to results
                review_result["final_summary"] = f"{product_name} by {brand_name or 'the manufacturer'} is generally well-received, with most customers highlighting its reliability and value, though some minor issues are noted."
                company_result["final_summary"] = f"{brand_name or 'The company'} is regarded as reliable with a strong market position and few safety or legal concerns."
                # Compose root-level final_summary
                combined_summary = f"{review_result['final_summary']} {company_result['final_summary']} Overall, the product and its manufacturer are considered trustworthy and a good choice in their category."
                # Ensure we don't cut mid-sentence
                root_final_summary = combined_summary[:350]  # Start with ~50 words
                last_period = root_final_summary.rfind('.')
                if last_period > 0:
                    root_final_summary = root_final_summary[:last_period + 1]
                
                # Calculate final grade
                final_grade = "N/A"
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
                
                return {
                    "analysis_id": analysis_id,
                    "status": "completed",
                    "review_analysis": review_result,
                    "company_analysis": company_result,
                    "final_grade": final_grade,
                    "timestamp": datetime.utcnow().isoformat(),
                    "dry_run": True,
                    "brand_name": brand_name,
                    "final_summary": root_final_summary
                }

            # Create agents
            logger.info("Creating agents")
            review_agent = self.review_analyzer.create_agent(dry_run=dry_run)
            company_agent = self.company_analyzer.create_agent(dry_run=dry_run)
            logger.info("Agents created successfully")

            # Create tasks
            logger.info("Creating analysis tasks")
            review_task = ReviewAnalyzerTasks.create_review_analysis_task(review_agent, product_name, product_url, brand_name)
            company_task = CompanyAnalyzerTasks.create_company_analysis_task(company_agent, product_name, product_url, brand_name)
            logger.info("Analysis tasks created successfully")

            # Create and run the crew
            logger.info("Creating and running the crew")
            crew = Crew(
                agents=[review_agent, company_agent],
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
                            # Clean the output and extract just the JSON part
                            cleaned_output = output.result.replace("```json", "").replace("```", "").strip()
                            
                            # Find the first complete JSON object
                            try:
                                # Find the first occurrence of a complete JSON object
                                start_idx = cleaned_output.find('{')
                                if start_idx != -1:
                                    # Find the matching closing brace
                                    brace_count = 1
                                    end_idx = start_idx + 1
                                    while brace_count > 0 and end_idx < len(cleaned_output):
                                        if cleaned_output[end_idx] == '{':
                                            brace_count += 1
                                        elif cleaned_output[end_idx] == '}':
                                            brace_count -= 1
                                        end_idx += 1
                                    
                                    if brace_count == 0:
                                        # Extract just the JSON object
                                        json_str = cleaned_output[start_idx:end_idx]
                                        parsed_output = json.loads(json_str)
                                        logger.info(f"%%%%%%%%%%%parsed_output: {parsed_output}")
                                        
                                        # Determine which analysis this is
                                        if "average_customer_rating" in parsed_output:
                                            logger.info("Found review analysis")
                                            review_result = parsed_output
                                        elif "company_name" in parsed_output:
                                            logger.info("Found company analysis")
                                            company_result = parsed_output
                                    else:
                                        logger.error("Could not find complete JSON object")
                                else:
                                    logger.error("No JSON object found in output")
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse JSON: {str(e)}")
                        else:
                            logger.warning("Task output has no result attribute")
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
            
            # Compose root-level final_summary
            root_final_summary = ""
            try:
                review_summary = review_result.get("final_summary", "")
                company_summary = company_result.get("final_summary", "")
                if review_summary and company_summary:
                    combined_summary = f"{review_summary} {company_summary} Overall, the product and its manufacturer are considered trustworthy and a good choice in their category."
                    # Ensure we don't cut mid-sentence
                    root_final_summary = combined_summary[:350]  # Start with ~50 words
                    last_period = root_final_summary.rfind('.')
                    if last_period > 0:
                        root_final_summary = root_final_summary[:last_period + 1]
                else:
                    root_final_summary = "Summary information from one or both agents is missing."
            except Exception as e:
                root_final_summary = f"Could not generate overall summary: {str(e)}"
            
            # Ensure all required fields are present
            final_result = {
                "analysis_id": analysis_id,
                "status": "completed",
                "review_analysis": review_result if review_result else {"error": "No review analysis available"},
                "company_analysis": company_result if company_result else {"error": "No company analysis available"},
                "final_grade": final_grade,
                "timestamp": datetime.utcnow().isoformat(),
                "dry_run": False,
                "final_summary": root_final_summary
            }
            logger.info(f"Analysis completed successfully - ID: {analysis_id}")
            return final_result
            
        except Exception as e:
            logger.error(f"Error during crew execution: {str(e)}")
            return {
                "analysis_id": analysis_id,
                "status": "error",
                "error_message": f"Crew execution failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "review_analysis": {"error": "Analysis failed"},
                "company_analysis": {"error": "Analysis failed"},
                "final_grade": "N/A",
                "dry_run": False
            } 