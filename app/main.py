from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.agents.orchestrator_agent import OrchestratorAgent
import uvicorn
import json
import asyncio
from pathlib import Path

app = FastAPI(title="Strategic Intelligence App")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Request models
class AnalysisRequest(BaseModel):
    strategic_question: str
    time_frame: str
    region: str
    prompt: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("analysis.html", {"request": request})

async def stream_agent_outputs(orchestrator: OrchestratorAgent, input_data: Dict[str, Any]):
    """Stream agent outputs as they become available."""
    try:
        # Process each agent sequentially
        for agent_name, agent in orchestrator.agents.items():
            # Process the agent
            result = await agent.process(input_data)
            
            # Yield the result
            yield json.dumps({agent_name: result}) + "\n"
            
            # Update input data with the current agent's output
            input_data[agent_name.lower().replace(" ", "_")] = result
            
    except Exception as e:
        yield json.dumps({"error": str(e)}) + "\n"

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    try:
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Convert request to dict
        input_data = request.dict()
        
        # Return streaming response
        return StreamingResponse(
            stream_agent_outputs(orchestrator, input_data),
            media_type="application/x-ndjson"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 