from rest_framework.filters import BaseFilterBackend

from django_filters import FilterSet, DateFilter, ChoiceFilter, NumberFilter, TimeFilter
from django.db.models import Q, Count

from datetime import datetime

from timetable import utils
from timetable.utils import get_school_from_user, convert_weekday_into_0_6_format
from timetable.models import Holiday, Stage, AbsenceBlock, Teacher, AdminSchool, HourSlot, HoursPerTeacherInClass, \
    Course, Assignment, Subject, Room


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
    school_year = NumberFilter(field_name='school_year', method='school_year_filter')

    def school_year_filter(self, queryset, name, value):
        return queryset.filter(course__school_year__id=value)

    class Meta:
        model = Stage
        fields = ['from_date', 'to_date', 'course', 'school_year']


class AbsenceBlockFilter(FilterSet):
    school_year = NumberFilter(field_name='school_year', method='school_year_filter')

    def school_year_filter(self, queryset, name, value):
        return queryset.filter(hour_slot__school_year__id=value)

    class Meta:
        model = AbsenceBlock
        fields = ['school_year', 'teacher']


class HourSlotFilter(FilterSet):
    class Meta:
        model = HourSlot
        fields = ['school_year', 'day_of_week']


class HoursPerTeacherInClassFilter(FilterSet):
    school_year = NumberFilter(field_name='school_year', method='school_year_filter')

    def school_year_filter(self, queryset, name, value):
        return queryset.filter(course__school_year__id=value)

    class Meta:
        model = HoursPerTeacherInClass
        fields = ['school_year', 'course', 'teacher']


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
    school_year = NumberFilter(field_name='school_year', method='school_year_filter')

    def school_year_filter(self, queryset, name, value):
        return queryset.filter(course__school_year__id=value)

    class Meta:
        model = Assignment
        fields = ['school_year', 'course', 'from_date', 'to_date']


class RoomFilter(FilterSet):
    def filter_queryset(self, queryset):
        """
        If the necessary parameters are given we return only the free rooms in the time period specified
        """
        school = self.request.GET.get('school')
        school_year = self.request.GET.get('school_year')
        hour_start = self.request.GET.get('hour_start')
        hour_end = self.request.GET.get('hour_end')
        date = self.request.GET.get('date')

        if date:
            date = datetime.strptime(date, '%Y-%m-%d')
        if hour_start and hour_end:
            hour_start = datetime.strptime(hour_start, '%H:%M')
            hour_end = datetime.strptime(hour_end, '%H:%M')

        if school and school_year and hour_start and hour_end and date:
            # Search assignments with an intersection in time
            used_rooms = Assignment.objects.filter(school=school,
                                                   course__school_year=school_year,
                                                   date=date,
                                                   room__isnull=False) \
                .filter(Q(hour_start__lte=hour_start, hour_end__gt=hour_start) |
                        Q(hour_start__lt=hour_end, hour_end__gte=hour_end)) \
                .values('room').annotate(total=Count('room'))
            rooms_id = []
            for room in used_rooms:
                if room['total'] >= Room.objects.get(id=room['room']).capacity:
                    rooms_id.append(room['room'])
            return queryset.exclude(id__in=rooms_id)
        return queryset

