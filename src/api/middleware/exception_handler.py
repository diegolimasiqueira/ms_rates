from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError
from typing import Union

from src.domain.exceptions.base_exceptions import BaseAPIException

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for the application
    """
    if isinstance(exc, BaseAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "details": exc.details
            }
        )
    
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Invalid request data",
                "details": [{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]
            }
        )
    
    if isinstance(exc, PyMongoError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An error occurred while accessing the database",
                "details": {"error": str(exc)}
            }
        )

    # Handle unexpected errors
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "An unexpected error occurred",
            "details": {"error": str(exc)} if request.app.debug else None
        }
    ) 