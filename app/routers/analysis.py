from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
import json
import os

router = APIRouter(prefix="/analysis", tags=["analysis"])
templates = Jinja2Templates(directory="app/templates")

# Ensure analysis directory exists
os.makedirs("data/analysis", exist_ok=True)

@router.get("/", response_class=HTMLResponse)
async def list_analyses(request: Request):
    """List all analyses"""
    analyses = []
    for filename in os.listdir("data/analysis"):
        if filename.endswith(".json"):
            with open(f"data/analysis/{filename}", "r") as f:
                analyses.append(json.load(f))
    return templates.TemplateResponse(
        "analysis.html",
        {"request": request, "analyses": analyses}
    )

@router.post("/")
async def create_analysis(analysis: Dict[str, Any]):
    """Create a new analysis"""
    analysis_id = analysis.get("id")
    if not analysis_id:
        raise HTTPException(status_code=400, detail="Analysis ID is required")
    
    filepath = f"data/analysis/{analysis_id}.json"
    if os.path.exists(filepath):
        raise HTTPException(status_code=400, detail="Analysis already exists")
    
    with open(filepath, "w") as f:
        json.dump(analysis, f, indent=2)
    
    return {"status": "success", "message": "Analysis created successfully"}

@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get a specific analysis"""
    filepath = f"data/analysis/{analysis_id}.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    with open(filepath, "r") as f:
        return json.load(f)

@router.put("/{analysis_id}")
async def update_analysis(analysis_id: str, analysis: Dict[str, Any]):
    """Update an analysis"""
    filepath = f"data/analysis/{analysis_id}.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    with open(filepath, "w") as f:
        json.dump(analysis, f, indent=2)
    
    return {"status": "success", "message": "Analysis updated successfully"}

@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis"""
    filepath = f"data/analysis/{analysis_id}.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    os.remove(filepath)
    return {"status": "success", "message": "Analysis deleted successfully"} 