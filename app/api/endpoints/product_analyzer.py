from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from app.agents.orchestrator import OrchestratorAgent
from datetime import datetime
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Product Analysis API",
    description="API for analyzing products and their manufacturers",
    version="1.0.0"
)

# Create router
router = APIRouter(prefix="/api/v1", tags=["product-analysis"])
orchestrator = OrchestratorAgent()

# Response Models
class ReviewAnalysis(BaseModel):
    average_customer_rating: float = Field(..., description="Average rating from customer reviews (0-10)")
    total_reviews_analyzed: int = Field(..., description="Total number of reviews analyzed")
    customer_sentiment_summary: str = Field(..., description="Overall sentiment: positive, negative, or neutral")
    key_positive_points: list[str] = Field(..., description="List of key positive aspects from reviews")
    key_negative_points: list[str] = Field(..., description="List of key negative aspects from reviews")
    common_issues: list[str] = Field(..., description="List of common issues reported in reviews")
    overall_product_reliability_score: float = Field(..., description="Overall reliability score (0-10)")
    brand_name: str = Field(None, description="Name of the brand or company that makes the product")
    final_summary: str = Field(..., description="One-sentence summary of the review findings, max 50 words.")

class CompanyAnalysis(BaseModel):
    company_name: str = Field(..., description="Name of the company")
    years_in_market: str = Field(..., description="How long the company has been in business")
    safety_issues: str = Field(..., description="Any reported safety concerns at company level")
    legal_issues: str = Field(..., description="Any legal challenges or lawsuits")
    company_reliability_score: float = Field(..., description="Company reliability score (0-10)")
    market_position: str = Field(..., description="Company's position in the market")
    brand_name: str = Field(None, description="Name of the brand or company that makes the product")
    final_summary: str = Field(..., description="One-sentence summary of the company findings, max 50 words.")

class AnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="Unique identifier for the analysis")
    status: str = Field(..., description="Status of the analysis: completed or error")
    review_analysis: ReviewAnalysis = Field(..., description="Analysis of customer reviews")
    company_analysis: CompanyAnalysis = Field(..., description="Analysis of company information")
    final_grade: str = Field(..., description="Final grade based on combined scores: A+, A, B+, B, C, or D")
    timestamp: str = Field(..., description="ISO timestamp of when the analysis was completed")
    dry_run: bool = Field(..., description="Whether this was a dry run (no actual LLM calls)")
    brand_name: str = Field(None, description="Name of the brand or company that makes the product")
    final_summary: str = Field(..., description="One-sentence summary of the overall analysis, max 50 words.")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    details: dict = Field(..., description="Additional error details")
    timestamp: str = Field(..., description="ISO timestamp of when the error occurred")

# Request Models
class ProductAnalysisRequest(BaseModel):
    product_url: HttpUrl = Field(..., description="URL of the product to analyze")
    product_name: str = Field(..., description="Name of the product to analyze")
    brand_name: str = Field(None, description="Name of the brand or company that makes the product")
    dry_run: bool = Field(False, description="If true, returns mock data without calling LLM")

@router.post("/analyze-product", 
    response_model=AnalysisResponse,
    responses={
        200: {"description": "Analysis completed successfully"},
        500: {"model": ErrorResponse, "description": "Analysis failed"}
    }
)
async def analyze_product(request: ProductAnalysisRequest):
    """
    Analyze a product and its manufacturer.
    
    - **product_url**: URL of the product to analyze
    - **product_name**: Name of the product to analyze
    - **brand_name**: Name of the brand or company that makes the product
    - **dry_run**: If true, returns mock data without calling LLM
    
    Returns a comprehensive analysis including:
    - Customer review analysis
    - Company analysis
    - Final reliability grade
    """
    try:
        logger.info(f"Received analysis request for product: {request.product_name}, brand: {request.brand_name}")
        result = await orchestrator.analyze_product(
            product_url=str(request.product_url),
            product_name=request.product_name,
            brand_name=request.brand_name,
            dry_run=request.dry_run
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing product: {str(e)}")
        error_response = ErrorResponse(
            error="Analysis failed",
            details={"message": str(e)},
            timestamp=datetime.utcnow().isoformat()
        )
        raise HTTPException(status_code=500, detail=error_response.dict())

# Include router in app
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app.api.endpoints.product_analyzer:app", host="0.0.0.0", port=8000, reload=True) 