from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from enum import Enum

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"

class ReviewAnalysis(BaseModel):
    average_rating: float
    total_reviews: int
    sentiment_summary: str
    key_positive_points: List[str]
    key_negative_points: List[str]
    reliability_score: float  # 0-1 scale

class CompanyAnalysis(BaseModel):
    company_name: str
    years_in_market: int
    safety_issues: List[str]
    lawsuits: List[str]
    reliability_score: float  # 0-1 scale
    market_position: str

class AnalysisRequest(BaseModel):
    product_url: str
    product_name: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: AnalysisStatus
    review_analysis: Dict[str, Any]
    company_analysis: Dict[str, Any]
    timestamp: str
    error_message: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str 