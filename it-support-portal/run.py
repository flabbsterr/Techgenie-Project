import subprocess
import sys

def run():
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("Initializing database...")
    subprocess.run([sys.executable, "init_db.py"])
    
    print("Starting server at http://localhost:8000")
    print("Credentials: staff/password123 or it/itadmin123")
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    run()