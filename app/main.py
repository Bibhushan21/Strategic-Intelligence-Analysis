from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from typing import List, Optional
from app.agents.orchestrator_agent import OrchestratorAgent
import uvicorn

app = FastAPI(title="Strategic Intelligence App")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Request models
class AnalysisRequest(BaseModel):
    strategic_question: str
    scope: List[str]
    time_frame: str
    region: str
    prompt: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    try:
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Process the analysis
        result = await orchestrator.process(request.dict())
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 