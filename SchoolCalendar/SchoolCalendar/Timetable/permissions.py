from rest_framework.permissions import BasePermission

from Timetable.models import Teacher, AdminSchool

#
# class IsUserInSchool(BasePermission):
#     """
#     Custom permission to only allow owners of an object to edit it.
#     """
#     def has_permission(self, request, view):
#         return True
