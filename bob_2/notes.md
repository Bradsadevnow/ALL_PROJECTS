# Steve Setup Notes

## Starting the Backend
The backend runs on FastAPI and uses a virtual environment to manage its dependencies (including the Gemini SDK, ChromaDB, and SQLAlchemy).

1. Open a terminal in the root project folder (`bob_2`).
2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
3. Start the FastAPI server on port 8000:
   ```bash
   uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```
*(Note: Adding `--reload` to the end of the uvicorn command will automatically restart the server when you edit Python files).*

## Starting the Frontend
The frontend is a React application built with Vite. It runs independently and connects to the backend via WebSockets.

1. Open a **second, separate terminal** in the root project folder (`bob_2`).
2. Navigate into the frontend directory:
   ```bash
   cd frontend
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open the localhost URL it provides (usually `http://localhost:5173`) in your browser.

## Running the Sleep Cycle (Offline Consolidation)
The Sleep Cycle is designed to run asynchronously in the background (e.g., via a cron job at 3 AM), but you can trigger it manually to convert Short-Term Memory (STM) into Long-Term Memory (LTM) and update Steve's Identity profiles.

1. Open a terminal and activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
2. Execute the sleep cycle script:
   ```bash
   python3 -m backend.agent.sleep_cycle
   ```
