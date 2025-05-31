import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.routers import projects, agents, analysis
import os

# Create FastAPI app
app = FastAPI(title="Strategic Intelligence App")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(projects.router)
app.include_router(agents.router)
app.include_router(analysis.router)

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs("app/static", exist_ok=True)
    os.makedirs("app/templates", exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 