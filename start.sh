#!/bin/bash

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run app
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}