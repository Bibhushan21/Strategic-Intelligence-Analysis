#!/bin/bash

# Make sure we're in the right directory
cd /opt/render/project/src

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Initialize database tables
echo "Initializing database tables..."
python init_cloud_database.py

# Start the application with gunicorn
echo "Starting FastAPI application..."
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT 