import logging
from fastapi import FastAPI
from src.api.v1.endpoints import ratings, health
from src.api.middleware.exception_handler import global_exception_handler
from src.domain.exceptions.base_exceptions import BaseAPIException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ms_rate - EasyProFind",
    description="Microserviço de avaliações de profissionais",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add exception handlers
app.add_exception_handler(BaseAPIException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(ratings.router, tags=["Ratings"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up ms_rate service...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down ms_rate service...") 