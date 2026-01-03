"""
Centralized error handling middleware
"""
import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with consistent JSON format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_exception"
            },
            "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with consistent JSON format"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "type": "validation_error",
                "details": exc.errors()
            },
            "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with consistent JSON format"""
    # Log the full traceback
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "internal_error"
            },
            "request_id": request.state.request_id if hasattr(request.state, "request_id") else None
        }
    )
