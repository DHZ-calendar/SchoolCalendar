from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, Serializer
from rest_framework.serializers import IntegerField

from Timetable.models import Teacher


class TeacherSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['url', 'username', 'email', 'is_staff', 'school', 'notes']


class CourseYearOnlySerializer(Serializer):
    year = IntegerField()
