from rest_framework.filters import BaseFilterBackend

from Timetable.utils import get_school_from_user


class TeacherFromSameSchoolFilterBackend(BaseFilterBackend):
    """
    Get all teachers in the school of the user logged
    """
    def filter_queryset(self, request, queryset, view):
        school = get_school_from_user(request.user)
        return queryset.filter(school=school.id)