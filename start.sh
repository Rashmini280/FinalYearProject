#!/bin/bash

# Move to backend folder
cd backend

# Install dependencies (optional, Railway also auto-installs)
pip install --no-cache-dir -r requirements.txt

# Start FastAPI with uvicorn
# $PORT is the environment variable Railway provides
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}