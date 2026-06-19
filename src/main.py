import os
import logging
import json
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(json.dumps({"event": "startup", "message": f"Warden is running on port {os.getenv('PORT', 8000)}"}))
    yield

app = FastAPI(title="Warden Service", version="1.0.0", lifespan=lifespan)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify that the service is running.
    """
    logger.info(json.dumps({"event": "health_check", "status": "success"}))
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)