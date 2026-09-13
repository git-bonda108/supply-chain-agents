#!/bin/bash
# Script to run Streamlit application

cd "$(dirname "$0")"
source .venv/bin/activate

echo "Starting Streamlit application..."
echo "Access the app at: http://localhost:8501"
echo ""

streamlit run streamlit_app.py



