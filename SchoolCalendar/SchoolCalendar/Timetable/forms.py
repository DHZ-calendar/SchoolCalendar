from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

from Timetable.models import School, MyUser, Teacher, AdminSchool


class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['name']


class TeacherForm(UserCreationForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'school', 'notes']
