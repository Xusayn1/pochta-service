"""
Django REST Framework class-based exception handler with Telegram alerting.

Provides structured exception handling with beautiful Telegram notifications
for critical errors while preventing spam from common exceptions.
"""

import logging
import traceback
from typing import Dict, Any, Optional

from django.http import Http404
from rest_framework.exceptions import (
    PermissionDenied,
    NotAuthenticated,
    ValidationError,
    AuthenticationFailed,
    NotFound,
    MethodNotAllowed,
    NotAcceptable,
    UnsupportedMediaType,
    Throttled
)
from rest_framework.response import Response

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.shared.utils.custom_current_host import get_client_ip
from apps.shared.utils.custom_response import CustomResponse
from apps.shared.utils.telegram_alerts import alert_to_telegram

logger = logging.getLogger(__name__)


class DRFExceptionHandler:
    """
    Class-based Django REST Framework exception handler.

    Provides structured exception handling with Telegram alerting for critical
    errors while preventing spam from common/expected exceptions.
    """

    # Exception types that should NOT trigger Telegram alerts (to prevent spam)
    SKIP_TELEGRAM_EXCEPTIONS = (
        ValidationError,
        Http404,
        PermissionDenied,
        NotAuthenticated,
        AuthenticationFailed,
        NotFound,
        MethodNotAllowed,
        NotAcceptable,
        UnsupportedMediaType,
        Throttled,
        CustomException  # Custom exceptions are handled gracefully
    )

    # Mapping of exception types to standardized error codes
    EXCEPTION_MAPPING = {
        ValidationError: "VALIDATION_ERROR",
        Http404: "NOT_FOUND",
        PermissionDenied: "PERMISSION_DENIED",
        NotAuthenticated: "AUTHENTICATION_FAILED",
        AuthenticationFailed: "AUTHENTICATION_FAILED",
        NotFound: "NOT_FOUND",
        MethodNotAllowed: "METHOD_NOT_ALLOWED",
        NotAcceptable: "NOT_ACCEPTABLE",
        UnsupportedMediaType: "UNSUPPORTED_MEDIA_TYPE",
        Throttled: "THROTTLED"
    }

    def handle_exception(self, exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
        """
        Main exception handling entry point.

        Args:
            exc: The exception instance
            context: Exception context containing request and view information

        Returns:
            Custom error response
        """
        request = context.get("request")

        # Handle CustomException with special context handling
        if isinstance(exc, CustomException):
            return self._handle_custom_exception(exc, request)

        # Handle known/mapped exceptions
        response = self._handle_known_exception(exc, context, request)
        if response:
            return response

        # Handle unknown/critical exceptions with Telegram alerting
        return self._handle_unknown_exception(exc, context, request)

    @staticmethod
    def _handle_custom_exception(exc: CustomException, request) -> Response:
        """
        Handle CustomException with special context handling.

        Args:
            exc: CustomException instance
            request: Django request object

        Returns:
            Custom error response with exception context
        """
        return CustomResponse.error(
            message_key=exc.message_key,
            request=request,
            context=exc.context
        )

    def _handle_known_exception(self, exc: Exception, context: Dict[str, Any], request) -> Optional[Response]:
        """
        Handle known exception types with appropriate custom responses.

        Args:
            exc: Exception instance
            context: Exception context
            request: Django request object

        Returns:
            CustomResponse for known exceptions, None for unknown exceptions
        """
        # Check if this is a known exception type
        for exc_type, error_code in self.EXCEPTION_MAPPING.items():
            if isinstance(exc, exc_type):
                return CustomResponse.error(
                    message_key=error_code,
                    request=request,
                    context=context,
                    exc=str(exc)
                )

        # Unknown exception - will be handled by _handle_unknown_exception
        return None

    def _handle_unknown_exception(self, exc: Exception, context: Dict[str, Any], request) -> Response:
        """
        Handle unknown/critical exceptions with Telegram alerting.

        Args:
            exc: Exception instance
            context: Exception context
            request: Django request object

        Returns:
            Generic error response for unknown exceptions
        """
        try:
            # Extract error details for Telegram alert
            error_details = self._extract_error_details(request, exc)

            # Send structured alert details to Telegram helper.
            alert_to_telegram(
                traceback_text=error_details["traceback"],
                message=error_details["message"],
                request=request,
                ip=error_details["client_ip"],
                port=error_details["port"],
            )

        except Exception as alert_error:
            # Log if Telegram alerting fails (avoid infinite recursion)
            logger.error(
                f"Failed to send Telegram alert for exception: {alert_error}",
                exc_info=True
            )

        # Return generic error response
        return CustomResponse.error(
            message_key="UNKNOWN_ERROR",
            request=request,
            context=context
        )

    def _should_skip_telegram_alert(self, exception: Exception) -> bool:
        """
        Determine if we should skip Telegram alert for this exception.

        Args:
            exception: Exception instance to check

        Returns:
            True if alert should be skipped, False if alert should be sent
        """
        return isinstance(exception, self.SKIP_TELEGRAM_EXCEPTIONS)

    @staticmethod
    def _extract_error_details(request, exception: Exception) -> Dict[str, Any]:
        """
        Extract comprehensive error details from request and exception.

        Args:
            request: Django HttpRequest object
            exception: Exception instance

        Returns:
            Dictionary containing error details for alerting
        """
        # Get full stack trace with length limit for Telegram
        current_traceback = traceback.format_exc()
        safe_traceback = (
            current_traceback[-2000:] if current_traceback
                                         and current_traceback.strip() != "NoneType: None"
            else "No traceback available"
        )

        # Extract client information safely
        client_ip = get_client_ip(request) if request else 'unknown'
        port = request.META.get('REMOTE_PORT', 'unknown') if request else 'unknown'

        # Additional context for debugging
        request_path = getattr(request, 'path', 'unknown') if request else 'unknown'
        request_method = getattr(request, 'method', 'unknown') if request else 'unknown'

        # Create comprehensive error message
        error_message = (
            f"{exception.__class__.__name__}: {str(exception)}\n"
            f"Path: {request_method} {request_path}"
        )

        return {
            'traceback': safe_traceback,
            'message': error_message,
            'client_ip': client_ip or 'unknown',
            'port': port,
            'request_path': request_path,
            'request_method': request_method
        }

# Create handler instance
exception_handler_instance = DRFExceptionHandler()


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """
    Function wrapper for the class-based exception handler.

    DRF expects a function, so this acts as a bridge to the class-based handler.

    Args:
        exc: Exception instance
        context: Exception context

    Returns:
        Custom error response
    """
    return exception_handler_instance.handle_exception(exc, context)