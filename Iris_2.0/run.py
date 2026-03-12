import subprocess
import time
import sys
import os

def run():
    # 1. Start FastAPI Backend
    print("🚀 Starting Iris Backend (FastAPI)...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.api:app", "--host", "0.0.0.0", "--port", "8000"],
        # env=os.environ
    )

    # 2. Start Vite Frontend
    print("🎨 Starting Iris Frontend (Vite)...")
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd="frontend",
        # env=os.environ
    )

    try:
        while True:
            time.sleep(1)
            if backend.poll() is not None:
                print("❌ Backend crashed.")
                break
            if frontend.poll() is not None:
                print("❌ Frontend crashed.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Iris...")
    finally:
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    run()
