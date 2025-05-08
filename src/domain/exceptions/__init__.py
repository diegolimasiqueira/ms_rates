"""
Package for domain exceptions
"""
from .base_exceptions import (
    BaseAPIException,
    NotFoundException,
    ValidationException,
    DatabaseException,
    AuthenticationException
)

__all__ = [
    'BaseAPIException',
    'NotFoundException',
    'ValidationException',
    'DatabaseException',
    'AuthenticationException'
] 