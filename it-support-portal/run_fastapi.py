#!/usr/bin/env python3

import subprocess
import sys
import os

def run_fastapi():
    print("Starting FastAPI IT Support Portal...")
    print("1. Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "fastapi_requirements.txt"])
    
    print("2. Initializing database...")
    subprocess.run([sys.executable, "fastapi_init_db.py"])
    
    print("3. Starting server...")
    print("Server will be available at: http://localhost:8000")
    print("Default credentials:")
    print("  Staff: staff / password123")
    print("  IT Admin: it / itadmin123")
    print("\nPress Ctrl+C to stop the server")
    
    subprocess.run([sys.executable, "-m", "uvicorn", "fastapi_main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    run_fastapi()