from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/", response_model=Dict[str, str])
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"} 