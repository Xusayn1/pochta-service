import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, Union

from rest_framework.request import Request
from rest_framework.response import Response

from apps.shared.exceptions.translator import get_message_detail

logger = logging.getLogger(__name__)


@dataclass
class ResponseBody:
    """Standardized response structure with translation support"""
    message_key: str
    request: Optional[Request] = None
    context: Optional[Dict[str, Any]] = None

    def get_language(self) -> str:
        """
        Extract language from request headers.
        Supports Accept-Language header with quality values.

        Examples:
            'en-US,en;q=0.9' -> 'en-US'
            'uz' -> 'uz'
        """
        if self.request and hasattr(self.request, 'headers'):
            accept_lang = self.request.headers.get('Accept-Language', 'en')
            # Parse Accept-Language header (remove quality values)
            lang = accept_lang.split(';')[0].split(',')[0].strip()
            return lang
        return 'en'

    def to_dict(self, **kwargs) -> Dict[str, Any]:
        """
        Convert to response dictionary with translated message.

        Args:
            **kwargs: Additional fields to include in response

        Returns:
            Dictionary with message details and any additional fields
        """
        lang = self.get_language()
        message_detail = get_message_detail(
            message_key=self.message_key,
            lang=lang,
            context=self.context
        )

        response_body = {
            "id": message_detail["id"],
            "message": message_detail["message"],
            **kwargs
        }

        return response_body

    def get_status_code(self) -> int:
        """Get the HTTP status code for this message"""
        lang = self.get_language()
        message_detail = get_message_detail(
            message_key=self.message_key,
            lang=lang,
            context=self.context
        )
        return message_detail["status_code"]


class CustomResponse:
    """Handle responses with automatic message translation"""

    @staticmethod
    def success(
            message_key: str = "SUCCESS_MESSAGE",
            request: Request = None,
            data: Any = None,
            context: Dict[str, Any] = None,
            status_code: int = None,
            **kwargs
    ) -> Response:
        """
        Create a success response with translated message.

        Args:
            message_key: Key for message template (default: SUCCESS_MESSAGE)
            request: Django REST Framework request object
            data: Response data
            context: Variables for message template formatting
            status_code: Override status code from message template
            **kwargs: Additional fields to include in response

        Returns:
            DRF Response object

        Example:
            >>> CustomResponse.success(
            ...     message_key="USER_CREATED",
            ...     request=request,
            ...     data={"id": 1, "name": "John"},
            ...     context={"username": "john"}
            ... )
            :param message_key:
            :param request:
            :param data:
            :param context:
            :param status_code:
        """
        body_maker = ResponseBody(
            message_key=message_key,
            request=request,
            context=context
        )

        # Build response body
        body = body_maker.to_dict(data=data, **kwargs)

        # Use explicit status code or get from message template
        final_status = status_code or body_maker.get_status_code()
        body["success"] = True
        return Response(body, status=final_status)

    @staticmethod
    def error(
            message_key: str,
            request: Request = None,
            context: Dict[str, Any] = None,
            errors: Union[Dict[str, Any], str, Exception] = None,
            status_code: int = None,
            **kwargs
    ) -> Response:
        """
        Create an error response with translated message.

        Args:
            message_key: Key for error message template
            request: Django REST Framework request object
            context: Variables for message template formatting
            errors: Detailed error information (field errors, etc.)
            status_code: Override status code from message template
            **kwargs: Additional fields to include in response

        Returns:
            DRF Response object

        Example:
            >>> CustomResponse.error(
            ...     message_key="VALIDATION_ERROR",
            ...     request=request,
            ...     errors={"email": ["Invalid email format"]}
            ... )
            :param message_key:
            :param request:
            :param context:
            :param errors:
            :param status_code:
        """
        body_maker = ResponseBody(
            message_key=message_key,
            request=request,
            context=context
        )

        # Build response body with errors if provided
        response_data = {}
        if errors:
            response_data['errors'] = errors

        body = body_maker.to_dict(**response_data, **kwargs)

        # Use explicit status code or get from message template
        final_status = status_code or body_maker.get_status_code()

        # Log error for monitoring
        logger.warning(
            f"Error response: {message_key} (status: {final_status})",
            extra={'errors': errors, 'context': context}
        )
        body["success"] = False
        return Response(body, status=final_status)

    @staticmethod
    def validation_error(
            errors: Dict[str, Any],
            request: Request = None,
            message_key: str = "VALIDATION_ERROR",
            context: Dict[str, Any] = None,
            **kwargs
    ) -> Response:
        """
        Create a validation error response (400).

        Args:
            errors: Validation errors (typically from serializer.errors)
            request: Django REST Framework request object
            message_key: Key for error message (default: VALIDATION_ERROR)
            context: Variables for message template formatting
            **kwargs: Additional fields to include in response

        Returns:
            DRF Response object with status 400

        """
        return CustomResponse.error(
            message_key=message_key,
            request=request,
            context=context,
            errors=errors,
            status_code=400,
            **kwargs
        )

    @staticmethod
    def not_found(
            message_key: str = "NOT_FOUND",
            request: Request = None,
            context: Dict[str, Any] = None,
            **kwargs
    ) -> Response:
        """
        Create a not found error response (404).

        Args:
            message_key: Key for error message
            request: Django REST Framework request object
            context: Variables for message template formatting
            **kwargs: Additional fields to include in response

        Returns:
            DRF Response object with status 404
        """
        return CustomResponse.error(
            message_key=message_key,
            request=request,
            context=context,
            status_code=404,
            **kwargs
        )

    @staticmethod
    def unauthorized(
            message_key: str = "UNAUTHORIZED",
            request: Request = None,
            context: Dict[str, Any] = None,
            **kwargs
    ) -> Response:
        """
        Create an unauthorized error response (401).

        Args:
            message_key: Key for error message
            request: Django REST Framework request object
            context: Variables for message template formatting
            **kwargs: Additional fields to include in response

        Returns:
            DRF Response object with status 401
        """
        return CustomResponse.error(
            message_key=message_key,
            request=request,
            context=context,
            status_code=401,
            **kwargs
        )

    @staticmethod
    def forbidden(
            message_key: str = "PERMISSION_DENIED",
            request: Request = None,
            context: Dict[str, Any] = None,
            **kwargs
    ) -> Response:
        """
        Create a forbidden error response (403).

        Args:
            message_key: Key for error message
            request: Django REST Framework request object
            context: Variables for message template formatting
            **kwargs: Additional fields to include in response

        Returns:
            DRF Response object with status 403
        """
        return CustomResponse.error(
            message_key=message_key,
            request=request,
            context=context,
            status_code=403,
            **kwargs
        )