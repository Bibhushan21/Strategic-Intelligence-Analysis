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
    return templates.TemplateResponse("index.html", {"request": request})

async def stream_agent_outputs_realtime(orchestrator: OrchestratorAgent, input_data: Dict[str, Any]):
    """Stream agent outputs in real-time with database integration."""
    try:
        # Create database session at start
        orchestrator._create_analysis_session(input_data)
        
        # Cumulative input data for subsequent agents
        cumulative_input_data = input_data.copy()
        
        # Agent names mapping
        agent_names_map = {
            "Problem Explorer": "problem_explorer",
            "Best Practices": "best_practices", 
            "Horizon Scanning": "horizon_scanning",
            "Scenario Planning": "scenario_planning",
            "Research Synthesis": "research_synthesis",
            "Strategic Action": "strategic_action",
            "High Impact": "high_impact",
            "Backcasting": "backcasting"
        }
        
        # Helper function to process agent and return result
        async def process_agent(agent_name: str, current_input_data: Dict[str, Any]):
            agent_instance = orchestrator.agents[agent_name]
            result = await orchestrator.rate_limited_process(agent_instance, current_input_data.copy(), agent_name)
            return result
        
        # Stage 1: Problem Explorer
        result = await process_agent("Problem Explorer", cumulative_input_data)
        cumulative_input_data[agent_names_map["Problem Explorer"]] = result
        yield json.dumps({"Problem Explorer": result}) + "\n"
        
        # Stage 2: Parallel agents (Best Practices, Horizon Scanning, Scenario Planning)
        parallel_agents = ["Best Practices", "Horizon Scanning", "Scenario Planning"]
        
        # Create tasks with proper mapping
        agent_tasks = {}
        for agent_name in parallel_agents:
            task = asyncio.create_task(process_agent(agent_name, cumulative_input_data))
            agent_tasks[agent_name] = task
        
        # Process parallel agents and yield results as they complete
        remaining_agents = set(parallel_agents)
        
        while remaining_agents:
            # Wait for any task to complete
            completed_tasks, pending_tasks = await asyncio.wait(
                [agent_tasks[agent_name] for agent_name in remaining_agents],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Process completed tasks
            for completed_task in completed_tasks:
                # Find which agent this task belongs to
                completed_agent = None
                for agent_name in remaining_agents:
                    if agent_tasks[agent_name] == completed_task:
                        completed_agent = agent_name
                        break
                
                if completed_agent:
                    try:
                        result = await completed_task
                        
                        # Update cumulative data
                        agent_key = agent_names_map[completed_agent]
                        cumulative_input_data[agent_key] = result
                        
                        # Yield result with correct agent name
                        yield json.dumps({completed_agent: result}) + "\n"
                        
                        # Remove from remaining agents
                        remaining_agents.remove(completed_agent)
                        
                    except Exception as task_error:
                        # Handle individual task errors
                        yield json.dumps({completed_agent: f"Error: {str(task_error)}"}) + "\n"
                        remaining_agents.remove(completed_agent)
        
        # Stage 3: Research Synthesis
        result = await process_agent("Research Synthesis", cumulative_input_data)
        cumulative_input_data[agent_names_map["Research Synthesis"]] = result
        yield json.dumps({"Research Synthesis": result}) + "\n"
        
        # Stage 4: Strategic Action
        result = await process_agent("Strategic Action", cumulative_input_data)
        cumulative_input_data[agent_names_map["Strategic Action"]] = result
        yield json.dumps({"Strategic Action": result}) + "\n"
        
        # Stage 5: High Impact
        result = await process_agent("High Impact", cumulative_input_data)
        cumulative_input_data[agent_names_map["High Impact"]] = result
        yield json.dumps({"High Impact": result}) + "\n"
        
        # Stage 6: Backcasting
        result = await process_agent("Backcasting", cumulative_input_data)
        cumulative_input_data[agent_names_map["Backcasting"]] = result
        yield json.dumps({"Backcasting": result}) + "\n"
        
        # Update session completion status
        orchestrator._update_session_completion("completed")
        
        # Yield session info
        if orchestrator.current_session_id:
            yield json.dumps({
                "session_info": {
                    "session_id": orchestrator.current_session_id,
                    "status": "completed"
                }
            }) + "\n"
            
    except Exception as e:
        # Update session as failed
        orchestrator._update_session_completion("failed")
        yield json.dumps({"error": str(e)}) + "\n"

@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    try:
        # Initialize orchestrator
        orchestrator = OrchestratorAgent()
        
        # Convert request to dict
        input_data = request.dict()
        
        # Return real-time streaming response
        return StreamingResponse(
            stream_agent_outputs_realtime(orchestrator, input_data),
            media_type="application/x-ndjson"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 