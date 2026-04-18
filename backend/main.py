"""
AI Python Code Visualizer & Debug Mentor - Backend
FastAPI application entry point
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

from routes.analyze import router as analyze_router

app = FastAPI(
    title="AI Python Visualizer",
    description="Web-based tool to explain, improve, and visualize Python code execution",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/api/v1", tags=["analysis"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AI Python Visualizer",
        "version": "1.0.0",
        "description": "Explain, improve, and visualize Python code"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)