#!/usr/bin/env python3
"""
Render entry point - redirects to backend app
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the backend app
from app import app

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check if service is running"""
    return {
        "message": "Backend is running",
        "working_directory": os.getcwd(),
        "python_path": sys.path[:3],  # Show first 3 paths
        "port": os.environ.get("PORT", "not set"),
        "backend_path": os.path.join(os.path.dirname(__file__), 'backend'),
        "backend_exists": os.path.exists(os.path.join(os.path.dirname(__file__), 'backend'))
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)