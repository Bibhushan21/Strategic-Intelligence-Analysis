from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
from app.agents.best_practices_agent import BestPracticesAgent
from app.agents.scenario_planning_agent import ScenarioPlanningAgent
from app.agents.horizon_scan_agent import HorizonScanAgent
from app.agents.synthesis_agent import SynthesisAgent
import json
import os

router = APIRouter(prefix="/agents", tags=["agents"])
templates = Jinja2Templates(directory="app/templates")

# Initialize agents
agents = {
    "best_practices": BestPracticesAgent(),
    "scenario_planning": ScenarioPlanningAgent(),
    "horizon_scan": HorizonScanAgent(),
    "synthesis": SynthesisAgent()
}

@router.get("/", response_class=HTMLResponse)
async def list_agents(request: Request):
    """List all available agents"""
    return templates.TemplateResponse(
        "agents.html",
        {"request": request, "agents": list(agents.keys())}
    )

@router.post("/{agent_name}/process")
async def process_agent(agent_name: str, input_data: Dict[str, Any]):
    """Process input data with a specific agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        result = await agents[agent_name].process(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get the status of a specific agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "status": "active",
        "agent_name": agent_name,
        "capabilities": agents[agent_name].get_system_prompt()
    } 