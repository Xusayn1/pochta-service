from functools import wraps
from django.shortcuts import redirect
from rest_framework import permissions


class IsCourier(permissions.BasePermission):
    """Check if user has courier role"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_courier


class IsManager(permissions.BasePermission):
    """Check if user has manager role"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager


class IsOwnerOrAdmin(permissions.BasePermission):
    """Check if user is owner of object or manager"""
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            (obj.sender == request.user or request.user.is_manager)
        )


def role_required(required_role):
    """
    Decorator to restrict view access by user role.
    
    Usage:
        @role_required('courier')
        def my_view(request):
            ...
    
    Args:
        required_role: 'courier', 'customer', or 'manager'
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login-page')
            
            user_role = getattr(request.user, 'role', None)
            
            # Map role names
            if required_role == 'courier' and request.user.is_courier:
                return view_func(request, *args, **kwargs)
            elif required_role == 'customer' and request.user.is_customer:
                return view_func(request, *args, **kwargs)
            elif required_role == 'manager' and request.user.is_manager:
                return view_func(request, *args, **kwargs)
            
            # Redirect to appropriate dashboard
            if request.user.is_courier:
                return redirect('courier_dashboard')
            elif request.user.is_customer:
                return redirect('customer_dashboard')
            else:
                return redirect('app')
        
        return wrapper
    return decorator