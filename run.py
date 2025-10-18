"""
Launch script for the Multimodal RAG application.
Starts both the FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting FastAPI backend on http://localhost:8000...")
    log_file = open("logs/backend.log", "w")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=Path(__file__).parent,
        stdout=log_file,
        stderr=log_file
    )
    return backend_process

def start_frontend():
    """Start the Streamlit frontend."""
    print("🎨 Starting Streamlit frontend on http://localhost:8501...")
    log_file = open("logs/frontend.log", "w")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"],
        cwd=Path(__file__).parent,
        stdout=log_file,
        stderr=log_file
    )
    return frontend_process

def main():
    """Main entry point for launching the application."""
    print("=" * 60)
    print("🚀 Multimodal RAG Application")
    print("=" * 60)
    
    try:
        # Start backend
        backend = start_backend()
        time.sleep(3)  # Give backend time to start
        
        # Start frontend
        frontend = start_frontend()
        time.sleep(2)
        
        # Open browser
        print("\n✅ Application is running!")
        print("   Backend API: http://localhost:8000")
        print("   Frontend UI: http://localhost:8501")
        print("   API Docs: http://localhost:8000/docs")
        print("\n📝 Press Ctrl+C to stop both servers\n")
        
        webbrowser.open("http://localhost:8501")
        
        # Wait for processes
        backend.wait()
        frontend.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend.terminate()
        frontend.terminate()
        print("✅ Shutdown complete")
        sys.exit(0)

if __name__ == "__main__":
    main()
