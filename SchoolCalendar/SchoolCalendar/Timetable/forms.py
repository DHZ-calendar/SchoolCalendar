from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from durationwidget.widgets import TimeDurationWidget
from django.utils.translation import gettext as _

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


class AbsenceBlockForm(ModelForm):

    class Meta:
        model = AbsenceBlock
        fields = ['teacher', 'hour_slot', 'school_year']


class HolidayForm(ModelForm):

    date_start = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker'
    }))
    date_end = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker'
    }))

    class Meta:
        model = Holiday
        fields = ['date_start', 'date_end', 'name', 'school', 'school_year']

    def clean(self):
        """
        We need to check whether date_start <= date_end
        :return:
        """
        if self.cleaned_data['date_start'] > self.cleaned_data['date_end']:
            self.add_error(None, forms.ValidationError(_('The date_start field can\'t be later than the end date')))

        return self.cleaned_data


class StageForm(ModelForm):

    date_start = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker'
    }))
    date_end = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker'
    }))

    class Meta:
        model = Stage
        fields = ['date_start', 'date_end', 'course', 'school', 'school_year']

    def clean(self):
        """
        We need to check whether date_start <= date_end
        :return:
        """
        if self.cleaned_data['date_start'] > self.cleaned_data['date_end']:
            self.add_error(None, forms.ValidationError(_('The date_start field can\'t be later than the end date')))

        return self.cleaned_data


class SubjectForm(ModelForm):

    class Meta:
        model = Subject
        fields = ['name', 'school', 'school_year']


class HoursPerTeacherInClassForm(ModelForm):

    class Meta:
        model = HoursPerTeacherInClass
        fields = ['teacher', 'course', 'subject', 'school_year', 'school', 'hours', 'hours_bes']


class AssignmentForm(ModelForm):
    date = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker'
    }))
    hour_start = forms.TimeField(widget=forms.TextInput(attrs={
        'class': 'timepicker'
    }))
    hour_end = forms.TimeField(widget=forms.TextInput(attrs={
        'class': 'timepicker'
    }))

    class Meta:
        model = Assignment
        fields = ['teacher', 'course', 'subject', 'school_year', 'school', 'date', 'hour_start', 'hour_end', 'bes',
                  'substitution', 'absent']

    def clean(self):
        """
        We need to check whether date_start <= date_end
        :return:
        """
        if self.cleaned_data['hour_start'] > self.cleaned_data['hour_end']:
            self.add_error(None, forms.ValidationError(_('The start time field can\'t be later than the end time')))

        return self.cleaned_data
