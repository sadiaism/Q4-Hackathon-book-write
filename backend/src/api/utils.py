import logging
from typing import Any, Dict
from fastapi import HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class APIResponseUtils:
    """
    Utility class for standardizing API responses
    """

    @staticmethod
    def success_response(data: Any, message: str = "Success", status_code: int = 200) -> Dict[str, Any]:
        """
        Create a standardized success response.

        Args:
            data: The response data
            message: Success message
            status_code: HTTP status code

        Returns:
            Dictionary with standardized success response format
        """
        return {
            "success": True,
            "message": message,
            "data": data,
            "status_code": status_code
        }

    @staticmethod
    def error_response(error: str, message: str = "Error occurred", status_code: int = 400) -> Dict[str, Any]:
        """
        Create a standardized error response.

        Args:
            error: Error code or type
            message: Error message
            status_code: HTTP status code

        Returns:
            Dictionary with standardized error response format
        """
        return {
            "success": False,
            "error": error,
            "message": message,
            "status_code": status_code
        }

    @staticmethod
    def create_http_exception(status_code: int, detail: str) -> HTTPException:
        """
        Create an HTTPException with standardized format.

        Args:
            status_code: HTTP status code
            detail: Error detail

        Returns:
            HTTPException instance
        """
        logger.error(f"HTTP Exception: status_code={status_code}, detail={detail}")
        return HTTPException(status_code=status_code, detail=detail)

    @staticmethod
    def format_response_object(response_obj) -> Dict[str, Any]:
        """
        Format a response object to a dictionary.

        Args:
            response_obj: Response object to format

        Returns:
            Dictionary representation of the response object
        """
        try:
            return response_obj.dict()
        except AttributeError:
            # If the object doesn't have a dict() method, try other approaches
            if hasattr(response_obj, '__dict__'):
                return response_obj.__dict__
            else:
                # If all else fails, return the object as is
                return response_obj