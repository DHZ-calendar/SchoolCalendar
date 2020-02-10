from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, Serializer
from rest_framework.serializers import IntegerField, CharField, DateField, SerializerMethodField
import datetime

from Timetable.models import Teacher, Holiday


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


class HolidaySerializer(ModelSerializer):
    """
    Returns the holiday filtered in a given period.
    date_start and date_end are the actual extremes of the holiday interval
    start end are the extremes of the intersection among the holiday interval and the period filtered
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

    class Meta:
        model = Holiday
        fields = ['start', 'end', 'date_start', 'date_end', 'name', 'school', 'school_year']
