from rest_framework.filters import BaseFilterBackend

from django_filters import FilterSet, DateFilter

from Timetable.utils import get_school_from_user
from Timetable.models import Holiday


class TeacherFromSameSchoolFilterBackend(BaseFilterBackend):
    """
    Get all teachers in the school of the user logged
    """
    def filter_queryset(self, request, queryset, view):
        school = get_school_from_user(request.user)
        return queryset.filter(school=school.id)


class HolidayPeriodFilter(FilterSet):
    to_date = DateFilter(field_name='date_start', lookup_expr='lte')
    from_date = DateFilter(field_name='date_end', lookup_expr='gte')

    class Meta:
        model = Holiday
        fields = ['from_date', 'to_date']
