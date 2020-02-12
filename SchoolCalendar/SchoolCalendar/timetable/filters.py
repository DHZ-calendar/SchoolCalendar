from rest_framework.filters import BaseFilterBackend

from django_filters import FilterSet, DateFilter, ChoiceFilter

from timetable.utils import get_school_from_user
from timetable.models import Holiday, Stage, AbsenceBlock, Teacher, AdminSchool, HourSlot, HoursPerTeacherInClass, Course


class TeacherFromSameSchoolFilterBackend(BaseFilterBackend):
    """
    Get all teachers in the school of the user logged
    """
    def filter_queryset(self, request, queryset, view):
        school = get_school_from_user(request.user)
        return queryset.filter(school=school.id)


class QuerysetFromSameSchool(BaseFilterBackend):
    """
    Generic filter that filters any queryset by school
    """
    def filter_queryset(self, request, queryset, view):
        school = get_school_from_user(request.user)
        return queryset.filter(school=school.id)


class HolidayPeriodFilter(FilterSet):
    to_date = DateFilter(field_name='date_start', lookup_expr='lte')
    from_date = DateFilter(field_name='date_end', lookup_expr='gte')

    class Meta:
        model = Holiday
        fields = ['from_date', 'to_date', 'school_year']


class StagePeriodFilter(FilterSet):
    to_date = DateFilter(field_name='date_start', lookup_expr='lte')
    from_date = DateFilter(field_name='date_end', lookup_expr='gte')

    class Meta:
        model = Stage
        fields = ['from_date', 'to_date', 'school_year']


class HourSlotFilter(FilterSet):
    class Meta:
        model = HourSlot
        fields = ['school_year']


class HoursPerTeacherInClassFilter(FilterSet):
    class Meta:
        model = HoursPerTeacherInClass
        fields = ['school_year', 'course']


class CoursesFilter(FilterSet):
    class Meta:
        model = Course
        fields = ['school_year']
