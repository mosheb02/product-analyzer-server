from fastapi import FastAPI, HTTPException
from app.models.schemas import AnalysisRequest, AnalysisResponse, ErrorResponse
from app.agents.orchestrator import OrchestratorAgent
from datetime import datetime
import uvicorn

app = FastAPI(title="Product Analysis API")
orchestrator = OrchestratorAgent()

@app.post("/analyze-product", response_model=AnalysisResponse)
async def analyze_product(request: AnalysisRequest):
    try:
        result = await orchestrator.analyze_product(request.product_url, request.product_name)
        return result
    except Exception as e:
        error_response = ErrorResponse(
            error="Analysis failed",
            details={"message": str(e)},
            timestamp=datetime.utcnow().isoformat()
        )
        raise HTTPException(status_code=500, detail=error_response.dict())

@app.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str):
    # In a real implementation, this would fetch from a database
    raise HTTPException(status_code=501, detail="Not implemented")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 