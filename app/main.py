import logging
from fastapi import FastAPI
from app.handlers.upload import router as upload_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application")

app.include_router(upload_router, prefix="/api")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Data Upload Service"}