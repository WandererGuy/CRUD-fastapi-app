from typing import Annotated
from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class ServiceException(Exception):
    """Base exception for service layer errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

class ValidationException(ServiceException):
    """Exception for validation errors."""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        exception_details = details or {}
        if field:
            exception_details["field"] = field

        super().__init__(message, exception_details, status_code=status.HTTP_400_BAD_REQUEST)

from sqlalchemy.exc import IntegrityError
def to_http_exception(exc: ServiceException) -> HTTPException:
    """
    Convert a ServiceException to HTTPException.

    Args:
        exc: ServiceException to convert

    Returns:
        HTTPException: Converted exception
    """
    return HTTPException(status_code=exc.status_code, detail={"message": exc.message, "details": exc.details})
