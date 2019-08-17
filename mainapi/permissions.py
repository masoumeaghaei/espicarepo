#permissions.py

from rest_framework import permissions
from .models import DeviceToken


class CustomPermission(permissions.BasePermission):
    """
    Allows access only to authenticated devices.
    """
    def has_permission(self, request, view):
        message = 'Request not allowed.'
        if DeviceToken.objects.filter(token = request.data.get('token')).exists():
            return True
        return False
