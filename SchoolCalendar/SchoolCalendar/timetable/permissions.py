from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework.permissions import BasePermission
from rest_framework import permissions

from timetable.models import Teacher, AdminSchool


class SchoolAdminCanWriteDelete(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            # Check permissions for read-only request
            # Every user can read
            return True
        else:
            # Check permissions for write request
            # Only if the logged in user is an admin.
            return AdminSchool.objects.filter(id=request.user.id).exists()


class TeacherCanView(BasePermission):
    """
    Permission to check that logged user is a teacher.
    """
    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS or not request.user:
            # A teacher can only see things, without creating, modifying or deleting anything
            # Some user need to be authenticated
            return False
        return Teacher.objects.filter(id=request.user.id).exists()
