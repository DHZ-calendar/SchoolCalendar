from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from durationwidget.widgets import TimeDurationWidget
from django.utils.translation import gettext as _

from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday,\
                             Stage, Subject, HoursPerTeacherInClass, Assignment
from timetable.utils import get_school_from_user


class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['name']


class BaseFormWithSchoolCheck(ModelForm):
    """
    Base form class, which allows to retrieve only the correct schools, and perform clean on the school field
    """
    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithSchoolCheck, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['school'] = forms.ModelChoiceField(
            queryset=School.objects.filter(id=get_school_from_user(self.user).id))

    def clean_school(self):
        if get_school_from_user(self.user) != self.cleaned_data['school']:
            self.add_error(None, forms.ValidationError(_('The school is not a valid choice.')))
        return self.cleaned_data['school']


class BaseFormWithTeacherAndSchoolCheck(BaseFormWithSchoolCheck):
    """
    Base form class, which allows to retrieve only the correct teachers according to the school of the user logged
    """
    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithTeacherAndSchoolCheck, self).__init__(user, *args, **kwargs)
        self.fields['teacher'] = forms.ModelChoiceField(
            queryset=Teacher.objects.filter(school__id=get_school_from_user(self.user).id))

    def clean_teacher(self):
        """
        Check whether the teacher is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a teacher.
        :return:
        """
        if get_school_from_user(self.user) != self.cleaned_data['teacher'].school:
            self.add_error(None, forms.ValidationError(_('The teacher {} is not in the School ({}).'.format(
                self.cleaned_data['teacher'], self.cleaned_data['teacher'].school
            ))))
        return self.cleaned_data['teacher']


class BaseFormWithCourseTeacherAndSchoolCheck(BaseFormWithTeacherAndSchoolCheck):
    """
    Base form class, which allows to retrieve only the correct course according to the school of the user logged
    """
    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithCourseTeacherAndSchoolCheck, self).__init__(user, *args, **kwargs)
        self.fields['course'] = forms.ModelChoiceField(
            queryset=Course.objects.filter(school__id=get_school_from_user(self.user).id))

    def clean_course(self):
        """
        Check whether the course is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a course.
        :return:
        """
        if get_school_from_user(self.user) != self.cleaned_data['course'].school:
            self.add_error(None, forms.ValidationError(_('The course {} is not in the School ({}).'.format(
                self.cleaned_data['course'], self.cleaned_data['course'].school
            ))))
        return self.cleaned_data['course']


class BaseFormWithSubjectCourseTeacherAndSchoolCheck(BaseFormWithCourseTeacherAndSchoolCheck):
    """
    Base form class, which allows to retrieve only the correct subject according to the school of the user logged.
    Moreover it inherits from BaseFormWithCourseTeacherAndSchoolCheck
    """
    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithSubjectCourseTeacherAndSchoolCheck, self).__init__(user, *args, **kwargs)
        self.fields['subject'] = forms.ModelChoiceField(
            queryset=Subject.objects.filter(school__id=get_school_from_user(self.user).id))

    def clean_subject(self):
        """
        Check whether the course is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a course.
        :return:
        """
        if get_school_from_user(self.user) != self.cleaned_data['subject'].school:
            self.add_error(None, forms.ValidationError(_('The subject {} is not taught in the School ({}).'.format(
                self.cleaned_data['subject'], self.cleaned_data['subject'].school
            ))))
        return self.cleaned_data['subject']


class TeacherForm(UserCreationForm, BaseFormWithSchoolCheck):
    class Meta:
        model = Teacher
        fields = ['username', 'first_name', 'last_name', 'email', 'school', 'notes']


class AdminSchoolForm(UserCreationForm, BaseFormWithSchoolCheck):
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


class CourseForm(BaseFormWithSchoolCheck):
    year = forms.IntegerField(help_text="This is the class number, for class IA for instance it is 1.")

    class Meta:
        model = Course
        fields = ['year', 'section', 'school_year', 'school']


class HourSlotForm(BaseFormWithSchoolCheck):
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


class AbsenceBlockForm(BaseFormWithTeacherAndSchoolCheck):
    """
    It actually inherits the clean_school method, but doesn't have the school field. It shouldn't be a problem.
    """
    class Meta:
        model = AbsenceBlock
        fields = ['teacher', 'hour_slot', 'school_year']


class HolidayForm(BaseFormWithSchoolCheck):

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


class StageForm(BaseFormWithCourseTeacherAndSchoolCheck):
    date_start = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker'
    }))
    date_end = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker'
    }))

    class Meta:
        model = Stage
        fields = ['date_start', 'date_end', 'course', 'name', 'school', 'school_year']

    def __init__(self, user, *args, **kwargs):
        """
        A bit dirty here:
        We have no teacher here, but we have it among the fields, as we inherit from
        BaseFormWithCourseTeacherAndSchoolCheck.
        Therefore, we need to remove after having populated fields with super.
        :param user:
        :param args:
        :param kwargs:
        """
        super(StageForm, self).__init__(user, *args, **kwargs)
        self.fields.pop('teacher')

    def clean(self):
        """
        We need to check whether date_start <= date_end
        :return:
        """
        if self.cleaned_data['date_start'] > self.cleaned_data['date_end']:
            self.add_error(None, forms.ValidationError(_('The date_start field can\'t be later than the end date')))

        return self.cleaned_data


class SubjectForm(BaseFormWithSchoolCheck):

    class Meta:
        model = Subject
        fields = ['name', 'school', 'school_year']


class HoursPerTeacherInClassForm(BaseFormWithSubjectCourseTeacherAndSchoolCheck):

    class Meta:
        model = HoursPerTeacherInClass
        fields = ['teacher', 'course', 'subject', 'school_year', 'school', 'hours', 'hours_bes']


class AssignmentForm(BaseFormWithSchoolCheck):
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
