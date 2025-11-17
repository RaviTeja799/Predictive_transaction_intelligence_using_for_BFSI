"""
Backend Server Startup Script
Run this file from the backend directory: python run.py
"""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting server from: {backend_dir}")
    print(f"Python path includes: {sys.path[0]}")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(backend_dir / "src")]
    )
