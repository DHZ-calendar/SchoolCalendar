from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, Serializer
from rest_framework.serializers import IntegerField, CharField, DateField, SerializerMethodField
import datetime

from timetable.models import Teacher, Holiday, Stage, AbsenceBlock, Assignment, HoursPerTeacherInClass, HourSlot
from timetable import utils


class TeacherSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['url', 'username', 'email', 'is_staff', 'school', 'notes']


class CourseYearOnlySerializer(Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    year = IntegerField()


class CourseSectionOnlySerializer(Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
    section = CharField()


class AbstractTimePeriodSerializer(ModelSerializer):
    """
    date_start and date_end are the actual extremes of the model interval
    start and end are the extremes of the intersection among the model interval and the period filtered

    For instance, if the model has a period from 4th January and 15th January, and the filtered period is 7-20th of
    January, then start and end are 7-15th of January.
    """
    start = SerializerMethodField()
    end = SerializerMethodField()

    def get_start(self, obj, *args, **kwargs):
        """
        :return: the maximum value among the beginning of the holiday, and the beginning of the filtered period
        """
        if self.context['request'].GET.get('from_date'):
            start = datetime.datetime.strptime(self.context['request'].GET.get('from_date'), '%Y-%m-%d').date()
        else:
            # No filter applied
            return obj.date_start
        start = start if start > obj.date_start else obj.date_start
        return start

    def get_end(self, obj, *args, **kwargs):
        """
        :return: the minimum value among the end of the holiday, and the end of the filtered period
        """
        if self.context['request'].GET.get('to_date'):
            end = datetime.datetime.strptime(self.context['request'].GET.get('to_date'), '%Y-%m-%d').date()
        else:
            # No filter applied
            return obj.date_end
        end = end if end < obj.date_end else obj.date_end
        return end


class HolidaySerializer(AbstractTimePeriodSerializer):
    """
    Returns the holiday filtered in a given period.
    """
    class Meta:
        model = Holiday
        fields = ['start', 'end', 'date_start', 'date_end', 'name', 'school', 'school_year']


class StageSerializer(AbstractTimePeriodSerializer):
    """
    Stage Serializer with period filter
    """
    class Meta:
        model = Stage
        fields = ['start', 'end', 'date_start', 'date_end', 'name', 'course', 'school', 'school_year']


class HourSlotSerializer(ModelSerializer):
    """
    Serializer for Hour Slots. No period filter is required
    """
    class Meta:
        model = HourSlot
        fields = ['id', 'hour_number', 'starts_at', 'ends_at', 'school', 'school_year', 'day_of_week', 'legal_duration']


class HoursPerTeacherInClassSerializer(ModelSerializer):
    """
    Serializer for teachers
    """
    missing_hours = SerializerMethodField()
    # missing_hours_bes = SerializerMethodField()

    class Meta:
        model = HoursPerTeacherInClass
        fields = ['teacher', 'course', 'subject', 'school_year', 'school', 'hours', 'hours_bes', 'missing_hours']

    def get_missing_hours(self, obj, *args, **kwargs):
        """
        Missing hours is computed over the hours the teacher needs to do for a given class,
        and the hours already planned in that class.
        :param obj:
        :param args:
        :param kwargs:
        :return:
        """
        pass
        assignments = Assignment.objects.filter(teacher=obj.teacher,
                                                course=obj.course,
                                                subject=obj.subject,
                                                school=obj.school,
                                                school_year=obj.school_year,
                                                bes=False).values('date__week_day', 'hour_start', 'hour_end')

        for el in assignments:
            el['date__week_day'] = utils.convert_weekday_into_0_6_format(el['date__week_day'])

        hours_slots = HourSlot.objects.filter(school=obj.school,
                                              school_year=obj.school_year).values("day_of_week", "starts_at",
                                                                                  "ends_at", "legal_duration")
        # Create a 3 dimensional map, indexed by day_of_week, starts_at, ends_at -> legal_duration
        map_hour_slots = {}
        for el in hours_slots:
            if el['day_of_week'] not in map_hour_slots:
                map_hour_slots[el['day_of_week']] = {}
            if el['starts_at'] not in map_hour_slots[el['day_of_week']]:
                map_hour_slots[el['day_of_week']][el['starts_at']] = {}
            if el['ends_at'] not in map_hour_slots[el['day_of_week']][el['starts_at']]:
                map_hour_slots[el['day_of_week']][el['starts_at']][el['ends_at']] = {}
            map_hour_slots[el['day_of_week']][el['starts_at']][el['ends_at']] = el['legal_duration']

        for el in assignments:
            if el["date__week_day"] in map_hour_slots and el['hour_start'] in map_hour_slots[el['date__week_day']] and \
                    el['hour_end'] in map_hour_slots[el['date__week_day']][el['hour_start']]:
                el['legal_duration'] = map_hour_slots[el['date__week_day']][el['hour_start']][el['hour_end']]
            else:
                el['legal_duration'] = el['hour_end'] - el['hour_start']

        total = datetime.timedelta(0)
        for el in assignments:
            total += el['legal_duration']

        return obj.hours - int(total.seconds/3600)
