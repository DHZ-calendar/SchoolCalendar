from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from durationwidget.widgets import TimeDurationWidget

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
    year = forms.IntegerField(help_text="This is the class number, for class IA for instance it is 1.")

    class Meta:
        model = Course
        fields = ['year', 'section', 'school_year', 'school']


class HourSlotForm(ModelForm):
    starts_at = forms.TimeField(widget=forms.TextInput(attrs={
        'class': 'datepicker'
    }))
    ends_at = forms.TimeField(widget=forms.TextInput(attrs={
        'class': 'datepicker'
    }))
    legal_duration = forms.DurationField(widget=TimeDurationWidget(show_days=False, show_hours=True, show_minutes=True,
                                                                   show_seconds=False),
                                         required=False)

    class Meta:
        model = HourSlot
        fields = ["hour_number", 'starts_at', 'ends_at', 'school', 'school_year', 'day_of_week', 'legal_duration']
