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