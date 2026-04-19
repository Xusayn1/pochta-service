import logging
import re

from django.apps import apps
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger('permissions')


def get_endpoint_model():
    try:
        return apps.get_model("users", "Endpoint")
    except LookupError:
        return None


class EndpointPermissionMiddleware(MiddlewareMixin):
    """
    Middleware to check endpoint permissions from database
    Uses endpoint access_type to determine access control
    """

    # Endpoints that should skip database lookup entirely
    SKIP_PREFIXES = [
        '/admin/',
        '/static/',
        '/media/',
        '/schema/',
        '/api/v1/docs/',
        '/api/v1/redoc/',
        '/api/v1/users/login/'
    ]

    def process_request(self, request):
        # Skip for non-API endpoints
        if not request.path.startswith('/api/'):
            return None

        # Skip for admin, static, media, schema, docs
        for prefix in self.SKIP_PREFIXES:
            if request.path.startswith(prefix):
                return None

        # Try to authenticate user
        jwt_authenticator = JWTAuthentication()
        try:
            auth_result = jwt_authenticator.authenticate(request)
            if auth_result is not None:
                request.user, request.auth = auth_result
        except Exception as e:
            logger.debug(f"Authentication failed: {e}")
            return None
        if auth_result is None:
            logger.debug(f"Authentication failed")
            return None
        # Normalize the path (replace IDs with {id})
        normalized_path = self.normalize_path(request.path)
        endpoint_model = get_endpoint_model()

        # If the endpoint-permission model is not installed in this project,
        # fail open and let the normal view/auth permission flow handle access.
        if endpoint_model is None:
            logger.debug("Endpoint model is not installed; skipping endpoint permission middleware.")
            return None

        # Check access from database (this now handles all access types)
        has_access = endpoint_model.check_access(
            user=request.user if hasattr(request, 'user') else None,
            path=normalized_path,
            method=request.method
        )

        if not has_access:
            # Get endpoint to show better error message
            endpoint = endpoint_model.objects.filter(
                path=normalized_path,
                method=request.method.upper(),
                is_active=True
            ).first()

            if endpoint:
                if endpoint.access_type == 'public':
                    error_detail = f'This endpoint is temporarily unavailable'
                elif endpoint.access_type == 'authenticated':
                    error_detail = f'Authentication required to access {request.method} {request.path}'
                else:  # permission
                    error_detail = f'You do not have permission to access {request.method} {request.path}'
            else:
                error_detail = f'Endpoint not found or not configured: {request.method} {request.path}'

            logger.warning(
                f"Access denied: {getattr(request.user, 'username', 'Anonymous')} "
                f"tried to access {request.method} {request.path}"
            )

            return JsonResponse(
                {
                    'error': 'Access denied',
                    'detail': error_detail
                },
                status=403 if hasattr(request, 'user') and request.user.is_authenticated else 401
            )

        return None

    @staticmethod
    def normalize_path(path):
        """
        Normalize paths with clear slug detection
        """
        STATIC_SEGMENTS = {'api', 'v1', 'v2', 'user-profiles', 'order-items'}

        parts = path.split('/')
        normalized_parts = []

        for part in parts:
            # Empty parts or known static segments
            if not part or part in STATIC_SEGMENTS:
                normalized_parts.append(part)
            # Dynamic segments (IDs/slugs)
            elif (part.isdigit() or
                  part.startswith('slug-') or
                  re.match(r'^[0-9a-f-]{32,}$', part)):  # UUID-like
                normalized_parts.append('{id}')
            # Everything else stays as-is
            else:
                normalized_parts.append(part)

        return '/'.join(normalized_parts)
