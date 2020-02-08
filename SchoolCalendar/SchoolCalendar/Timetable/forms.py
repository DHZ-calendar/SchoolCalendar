from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

from Timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday,\
                             Stage, Subject, HoursPerTeacherInClass, Assignment


class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['name']


class TeacherForm(UserCreationForm):
    class Meta:
        model = Teacher
        fields = ['username', 'first_name', 'last_name', 'email', 'school', 'notes']


class AdminSchoolForm(UserCreationForm):
    class Meta:
        model = AdminSchool
        fields = ['username', 'first_name', 'last_name', 'email', 'school']


class SchoolYearForm(ModelForm):
    date_start = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker'
    }))

    class Meta:
        model = SchoolYear
        fields = ['year_start', 'date_start']


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['year', 'section', 'school_year', 'school']

