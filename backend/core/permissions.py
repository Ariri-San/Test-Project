from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class DeviceUserPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.user == user or user.is_staff
    
    def has_permission(self, request, view):
        if request.method == "POST":
            if  request.user.is_staff:
                return True
            return False
        return True
