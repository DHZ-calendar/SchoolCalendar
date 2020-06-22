from rest_framework.filters import BaseFilterBackend

from django_filters import FilterSet, DateFilter, ChoiceFilter

import datetime

from timetable import utils
from timetable.utils import get_school_from_user, convert_weekday_into_0_6_format
from timetable.models import Holiday, Stage, AbsenceBlock, Teacher, AdminSchool, HourSlot, HoursPerTeacherInClass, \
    Course, Assignment, Subject


class TeacherFromSameSchoolFilterBackend(BaseFilterBackend):
    """
    Get all teachers in the school of the user logged
    """
    def filter_queryset(self, request, queryset, view):
        school = get_school_from_user(request.user)
        return queryset.filter(teacher__school=school.id)


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


class StageFilter(FilterSet):
    to_date = DateFilter(field_name='date_start', lookup_expr='lte')
    from_date = DateFilter(field_name='date_end', lookup_expr='gte')

    class Meta:
        model = Stage
        fields = ['from_date', 'to_date', 'school_year', 'course']


class SubjectFilter(FilterSet):
    class Meta:
        model = Subject
        fields = ['school_year']


class AbsenceBlockFilter(FilterSet):
    class Meta:
        model = AbsenceBlock
        fields = ['school_year']


class HourSlotFilter(FilterSet):
    class Meta:
        model = HourSlot
        fields = ['school_year']


class HoursPerTeacherInClassFilter(FilterSet):
    class Meta:
        model = HoursPerTeacherInClass
        fields = ['school_year', 'course']


class CourseSectionOnlyFilter(FilterSet):
    class Meta:
        model = Course
        fields = ['school_year', 'year']


class CourseYearOnlyFilter(FilterSet):
    class Meta:
        model = Course
        fields = ['school_year']


class AssignmentFilter(FilterSet):
    to_date = DateFilter(field_name='date', lookup_expr='lte')
    from_date = DateFilter(field_name='date', lookup_expr='gte')

    class Meta:
        model = Assignment
        fields = ['school_year', 'course', 'from_date', 'to_date']
