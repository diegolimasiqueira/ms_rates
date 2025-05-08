import pytest
from src.domain.exceptions.base_exceptions import (
    BaseAPIException,
    NotFoundException,
    ValidationException,
    DatabaseException,
    AuthenticationException
)

def test_base_api_exception():
    # Teste com detalhes
    details = {"field": "test", "error": "invalid"}
    exception = BaseAPIException(
        status_code=400,
        message="Test error",
        error_code="TEST_ERROR",
        details=details
    )
    assert exception.status_code == 400
    assert exception.message == "Test error"
    assert exception.error_code == "TEST_ERROR"
    assert exception.details == details
    assert str(exception) == "Test error"

    # Teste sem detalhes
    exception = BaseAPIException(
        status_code=400,
        message="Test error",
        error_code="TEST_ERROR"
    )
    assert exception.details == {}

def test_not_found_exception():
    # Teste com mensagem padrão
    exception = NotFoundException()
    assert exception.status_code == 404
    assert exception.message == "Resource not found"
    assert exception.error_code == "NOT_FOUND"
    assert exception.details == {}

    # Teste com mensagem e detalhes personalizados
    details = {"resource_id": "123", "resource_type": "user"}
    exception = NotFoundException(
        message="User not found",
        details=details
    )
    assert exception.status_code == 404
    assert exception.message == "User not found"
    assert exception.error_code == "NOT_FOUND"
    assert exception.details == details

def test_validation_exception():
    # Teste com mensagem padrão
    exception = ValidationException()
    assert exception.status_code == 400
    assert exception.message == "Validation error"
    assert exception.error_code == "VALIDATION_ERROR"
    assert exception.details == {}

    # Teste com mensagem e detalhes personalizados
    details = {"field": "email", "error": "invalid format"}
    exception = ValidationException(
        message="Invalid email format",
        details=details
    )
    assert exception.status_code == 400
    assert exception.message == "Invalid email format"
    assert exception.error_code == "VALIDATION_ERROR"
    assert exception.details == details

def test_database_exception():
    # Teste com mensagem padrão
    exception = DatabaseException()
    assert exception.status_code == 500
    assert exception.message == "Database error"
    assert exception.error_code == "DATABASE_ERROR"
    assert exception.details == {}

    # Teste com mensagem e detalhes personalizados
    details = {"operation": "insert", "error": "duplicate key"}
    exception = DatabaseException(
        message="Failed to insert record",
        details=details
    )
    assert exception.status_code == 500
    assert exception.message == "Failed to insert record"
    assert exception.error_code == "DATABASE_ERROR"
    assert exception.details == details

def test_authentication_exception():
    # Teste com mensagem padrão
    exception = AuthenticationException()
    assert exception.status_code == 401
    assert exception.message == "Authentication failed"
    assert exception.error_code == "AUTHENTICATION_ERROR"
    assert exception.details == {}

    # Teste com mensagem e detalhes personalizados
    details = {"reason": "token expired"}
    exception = AuthenticationException(
        message="Token expired",
        details=details
    )
    assert exception.status_code == 401
    assert exception.message == "Token expired"
    assert exception.error_code == "AUTHENTICATION_ERROR"
    assert exception.details == details 