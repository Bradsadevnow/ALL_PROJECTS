from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
import logging
import os
from backend.core.config import settings

# Setup standard logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)

# Ensure runtime directories exist
os.makedirs(settings.steve_runtime_dir, exist_ok=True)
os.makedirs(settings.steve_continuity_dir, exist_ok=True)

app = FastAPI(title="Steve Agent API")

# Setup CORS for future React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "Active", "agent": "Steve API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
