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

        for visible in self.visible_fields():
            if 'class' not in visible.field.widget.attrs:
                visible.field.widget.attrs['class'] = 'form-control'


    def clean_school(self):
        if get_school_from_user(self.user) != self.cleaned_data['school']:
            self.add_error(None, forms.ValidationError(_('The school selected is not a valid choice.')))
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
            self.add_error(None, forms.ValidationError(_('The teacher {} is not in the school ({}).'.format(
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
            self.add_error(None, forms.ValidationError(_('The course {} is not in the school ({}).'.format(
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
            self.add_error(None, forms.ValidationError(_('The subject {} is not taught in the school ({}).'.format(
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
    date_start = forms.TimeField(
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker'
        }))

    class Meta:
        model = SchoolYear
        fields = ['year_start', 'date_start']

    def clean(self):
        """
        Of course, the date_start must be included in the year_start
        :return:
        """
        if self.cleaned_data['year_start'] != self.cleaned_data['date_start'].year:
            self.add_error(None, forms.ValidationError(_('The start date must belong to the start year!')))
        return self.cleaned_data


class CourseForm(BaseFormWithSchoolCheck):
    year = forms.IntegerField(help_text=_("This is the class number, for class IA for instance it is 1."))

    class Meta:
        model = Course
        fields = ['year', 'section', 'school_year', 'school']


class HourSlotForm(BaseFormWithSchoolCheck):
    starts_at = forms.TimeField(
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'class': 'form-control timepicker'
    }))
    ends_at = forms.TimeField(
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'class': 'form-control timepicker'
    }))
    legal_duration = forms.DurationField(widget=TimeDurationWidget(show_days=False,
                                                                   show_hours=True,
                                                                   show_minutes=True,
                                                                   show_seconds=False,
                                                                   attrs={}),  # We need to remove form-control.
                                         required=False)

    class Meta:
        model = HourSlot
        fields = ["hour_number", 'starts_at', 'ends_at', 'school', 'school_year', 'day_of_week', 'legal_duration']

    def clean(self):
        """
        Of course, the starts_at must be smaller than ends_at
        :return:
        """
        if self.cleaned_data['starts_at'] >= self.cleaned_data['ends_at']:
            self.add_error(None, forms.ValidationError(_('The start hour must be strictly smaller that the '
                                                         'end hour.')))
        return self.cleaned_data


class AbsenceBlockForm(BaseFormWithTeacherAndSchoolCheck):
    """
    It actually inherits the clean_school method, but doesn't have the school field. It shouldn't be a problem.
    """
    def __init__(self, user, *args, **kwargs):
        """
        Add hour_slot selection based on the current school, and ordered by week_day and starts_at
        :param user: the user logged, the school is retrieved by her.
        """
        super(AbsenceBlockForm, self).__init__(user, *args, **kwargs)
        self.fields['hour_slot'] = forms.ModelChoiceField(
            queryset=HourSlot.objects.filter(school__id=get_school_from_user(self.user).id).order_by('day_of_week',
                                                                                                     'starts_at'))

    class Meta:
        model = AbsenceBlock
        fields = ['teacher', 'hour_slot', 'school_year']

    def clean_hour_slot(self):
        """
        We need to check whether the hour_slot belongs to the correct school
        :return:
        """
        if self.cleaned_data['hour_slot'].school != get_school_from_user(self.user):
            self.add_error(None, forms.ValidationError(_('The current school has no such hour slot!')))
        return self.cleaned_data['hour_slot']


class HolidayForm(BaseFormWithSchoolCheck):

    date_start = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker'
        }))
    date_end = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker'
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
            self.add_error(None, forms.ValidationError(_('The date_start field can\'t be greater than the end date')))
        return self.cleaned_data


class StageForm(BaseFormWithCourseTeacherAndSchoolCheck):
    date_start = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker'
        }))
    date_end = forms.DateField(
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker'
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
            self.add_error(None, forms.ValidationError(_('The date_start field can\'t be greater than the end date')))

        return self.cleaned_data


class SubjectForm(BaseFormWithSchoolCheck):

    class Meta:
        model = Subject
        fields = ['name', 'school', 'school_year']


class HoursPerTeacherInClassForm(BaseFormWithSubjectCourseTeacherAndSchoolCheck):

    class Meta:
        model = HoursPerTeacherInClass
        fields = ['teacher', 'course', 'subject', 'school_year', 'school', 'hours', 'hours_bes']


class AssignmentForm(BaseFormWithSubjectCourseTeacherAndSchoolCheck):
    date = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
        'class': 'form-control datepicker'
    }))
    hour_start = forms.TimeField(widget=forms.TextInput(attrs={
        'class': 'form-control timepicker'
    }))
    hour_end = forms.TimeField(widget=forms.TextInput(attrs={
        'class': 'form-control timepicker'
    }))

    class Meta:
        model = Assignment
        fields = ['teacher', 'course', 'subject', 'school_year', 'school', 'date', 'hour_start', 'hour_end', 'bes',
                  'substitution', 'absent']

    def clean(self):
        """
        We need to check whether date_start <= date_end
        Moreover, we need to check whether there is a HoursPerTeacherInClass for a given course, teacher,
        school_year, school, subject, bes. Only if the hour is not a substitution class.
        :return:
        """
        if self.cleaned_data['hour_start'] > self.cleaned_data['hour_end']:
            self.add_error(None, forms.ValidationError(_('The start time field can\'t be greater than the end time')))

        if not self.cleaned_data['substitution']:
            # We need to check for the existence of a related HourPerTeacherInClass
            hours_teacher_in_class = HoursPerTeacherInClass.objects.filter(
                                                        teacher=self.cleaned_data['teacher'],
                                                        school_year=self.cleaned_data['school_year'],
                                                        school=self.cleaned_data['school'],
                                                        course=self.cleaned_data['course'],
                                                        subject=self.cleaned_data['subject'])
            if not hours_teacher_in_class:

                self.add_error(None, forms.ValidationError(_('There is not a related '
                                                             'teacher in class instance.')))
            elif self.cleaned_data['bes'] and hours_teacher_in_class.first().hours_bes == 0:
                self.add_error(None, forms.ValidationError(_('The teacher doesn\'t have bes hours '
                                                             'in this course.')))
            elif not self.cleaned_data['bes'] and hours_teacher_in_class.first().hours == 0:
                self.add_error(None, forms.ValidationError(_('The teacher has only bes hours '
                                                             'in this course.')))
        return self.cleaned_data
