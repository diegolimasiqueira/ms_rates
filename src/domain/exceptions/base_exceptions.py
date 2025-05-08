from typing import Any, Dict, Optional

class BaseAPIException(Exception):
    """Base exception for all API errors"""
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class NotFoundException(BaseAPIException):
    """Exception for resource not found"""
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=404,
            message=message,
            error_code="NOT_FOUND",
            details=details
        )

class ValidationException(BaseAPIException):
    """Exception for validation errors"""
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=400,
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )

class DatabaseException(BaseAPIException):
    """Exception for database errors"""
    def __init__(self, message: str = "Database error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            message=message,
            error_code="DATABASE_ERROR",
            details=details
        )

class AuthenticationException(BaseAPIException):
    """Exception for authentication errors"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=401,
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        ) 