from django import forms
from django.db.models import Q
from django.forms import ModelForm, Form
from django.contrib.auth.forms import UserCreationForm
from durationwidget.widgets import TimeDurationWidget
from django.utils.translation import gettext_lazy as _

from timetable import models
from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday, \
    Stage, Subject, HoursPerTeacherInClass, Assignment, Room, TeachersYearlyLoad, CoursesYearlyLoad, HourSlotsGroup, \
    HourSlotsGroup
from timetable.utils import get_school_from_user, assign_html_style_to_visible_forms_fields, generate_random_password, \
    assign_translated_labels_to_form_fields


class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = ['name']


class BaseFormWithUser(ModelForm):
    """
    Base form class, which allows to retrieve only the correct schools, and perform clean on the school field
    """

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(BaseFormWithUser, self).__init__(*args, **kwargs)

        assign_translated_labels_to_form_fields(self)


class BaseFormWithSchoolCheck(BaseFormWithUser):
    """
    Base form class, which allows to retrieve only the correct schools, and perform clean on the school field
    """

    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithSchoolCheck, self).__init__(user, *args, **kwargs)

        # Populate with the correct schools
        self.fields['school'].queryset = School.objects.filter(id=get_school_from_user(user).id)

    def clean_school(self):
        if get_school_from_user(self.user) != self.cleaned_data['school']:
            self.add_error(None, forms.ValidationError(_('The school selected is not a valid choice.')))
        return self.cleaned_data['school']


class BaseFormWithTeacherCheck(BaseFormWithUser):
    """
    Base form class, which allows to retrieve only the correct teachers according to the school of the user logged
    """

    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithTeacherCheck, self).__init__(user, *args, **kwargs)

        # Populate the teacher picker with the correct teachers
        self.fields['teacher'].queryset = Teacher.objects.filter(school__id=get_school_from_user(user).id) \
            .order_by('last_name', 'first_name')
        self.fields['teacher'].label_from_instance = self.teacher_label

    @staticmethod
    def teacher_label(obj):
        """
        It is desirable that teachers' names are written as last_name first_name
        """
        return "{} {}".format(obj.last_name, obj.first_name)

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


class BaseFormWithHourSlotCheck(BaseFormWithUser):
    """
    Base form class, which checks if the hour_slot is correct for the user given
    """

    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithHourSlotCheck, self).__init__(user, *args, **kwargs)

        # Get the correct hours slots
        self.fields['hour_slot'].queryset = HourSlot.objects.filter(
            hour_slots_group__school__id=get_school_from_user(user).id) \
            .order_by('day_of_week', 'starts_at')

    def clean_hour_slot(self):
        """
        We need to check whether the hour_slot belongs to the correct school
        :return:
        """
        if self.cleaned_data['hour_slot'].school != get_school_from_user(self.user):
            self.add_error(None, forms.ValidationError(_('The current school has no such hour slot!')))
        return self.cleaned_data['hour_slot']


class BaseFormWithCourseCheck(BaseFormWithUser):
    """
    Base form class, which allows to retrieve only the correct course according to the school of the user logged
    """

    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithCourseCheck, self).__init__(user, *args, **kwargs)

        self.fields['course'].queryset = Course.objects.filter(hour_slots_group__school__id=get_school_from_user(user).id) \
            .order_by('hour_slots_group__school_year', 'year', 'section')

    def clean_course(self):
        """
        Check whether the course is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a course.
        :return:
        """
        if get_school_from_user(self.user) != self.cleaned_data['course'].hour_slots_group.school:
            self.add_error(None, forms.ValidationError(_('The course {} is not in the school ({}).'.format(
                self.cleaned_data['course'], self.cleaned_data['course'].hour_slots_group.school
            ))))
        return self.cleaned_data['course']


class BaseFormWithSubjectCheck(BaseFormWithUser):
    """
    Base form class, which allows to retrieve only the correct subject according to the school of the user logged.
    Moreover it inherits from BaseFormWithUser
    """

    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithSubjectCheck, self).__init__(user, *args, **kwargs)

        self.fields['subject'].queryset = Subject.objects.filter(school__id=get_school_from_user(user).id) \
            .order_by('name')

    def clean_subject(self):
        """
        Check whether the subject is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a subject.
        :return:
        """
        if get_school_from_user(self.user) != self.cleaned_data['subject'].school:
            self.add_error(None, forms.ValidationError(_('The subject {} is not taught in the school ({}).'.format(
                self.cleaned_data['subject'], self.cleaned_data['subject'].school
            ))))
        return self.cleaned_data['subject']


class BaseFormWithRoomCheck(BaseFormWithUser):
    """
    Base form class, which allows to retrieve only the correct rooms according to the school of the user logged.
    Moreover it inherits from BaseFormWithUser
    """

    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithRoomCheck, self).__init__(user, *args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(school__id=get_school_from_user(user).id) \
            .order_by('name')

    def clean_room(self):
        """
        Check whether the room is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a room.
        :return:
        """
        if 'room' in self.cleaned_data and \
                self.cleaned_data['room'] is not None and \
                get_school_from_user(self.user) != self.cleaned_data['room'].school:
            self.add_error(None, forms.ValidationError(_('The room {} does not exist in the school ({}).'.format(
                self.cleaned_data['room'], self.cleaned_data['subject'].school
            ))))
        return self.cleaned_data['room']


class BaseFormWithHourSlotsGroupCheck(BaseFormWithUser):
    """
    Base form class, which allows to retrieve only the correct hour_slots_groups according to the school of the user logged.
    Moreover it inherits from BaseFormWithUser
    """

    def __init__(self, user, *args, **kwargs):
        super(BaseFormWithHourSlotsGroupCheck, self).__init__(user, *args, **kwargs)
        self.fields['hour_slots_group'].queryset = HourSlotsGroup.objects. \
            filter(school__id=get_school_from_user(user).id).order_by('name')

    def clean_hour_slots_group(self):
        """
        Check whether the hour_slots_group is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a subject.
        :return:
        """
        if get_school_from_user(self.user) != self.cleaned_data['hour_slots_group'].school:
            self.add_error(None, forms.ValidationError(_('The HourSlotsGroup {} is not present in the school ({}).'.
                format(self.cleaned_data['hour_slots_group'], self.cleaned_data['hour_slots_group'].school)
            )))
        return self.cleaned_data['hour_slots_group']


class UserCreationFormWithoutPassword(UserCreationForm):
    """
    A UserCreationForm without password inputs.
    """

    def __init__(self, *args, **kwargs):
        super(UserCreationFormWithoutPassword, self).__init__(*args, **kwargs)
        self.fields.pop('password1')
        self.fields.pop('password2')

    def clean(self):
        if self.instance.pk is None:  # Creating a new user
            self.cleaned_data['password1'] = generate_random_password()
            self.cleaned_data['password2'] = self.cleaned_data['password1']
        return super().clean()


class TeacherForm(BaseFormWithSchoolCheck):
    in_activity = forms.BooleanField(help_text=_("Set it to False if you do not want to "
                                                               "see this professor in the list of teachers "
                                                               "in the column on the right "
                                                               "of the timetable page."))
    def __init__(self, user, *args, **kwargs):
        super(TeacherForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = Teacher
        fields = ['username', 'first_name', 'last_name', 'email', 'school', 'in_activity', 'notes']


class TeacherCreationForm(UserCreationFormWithoutPassword, BaseFormWithSchoolCheck):
    """
    Form for creating a Teacher entity without asking passwords
    """

    def __init__(self, user, *args, **kwargs):
        super(TeacherCreationForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = Teacher
        fields = ['username', 'first_name', 'last_name', 'email', 'school', 'notes']


class AdminSchoolForm(ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(AdminSchoolForm, self).__init__(*args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = AdminSchool
        fields = ['username', 'first_name', 'last_name', 'email', 'school']


class AdminSchoolCreationForm(UserCreationFormWithoutPassword):
    """
    Form for creating a AdminSchool entity without asking passwords
    """

    def __init__(self, user, *args, **kwargs):
        super(AdminSchoolCreationForm, self).__init__(*args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = AdminSchool
        fields = ['username', 'first_name', 'last_name', 'email', 'school']


class SchoolYearForm(ModelForm):
    date_start = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'form-control datepicker-input datepicker'
            })
    )

    def __init__(self, *args, **kwargs):
        super(SchoolYearForm, self).__init__(*args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

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


class RoomForm(BaseFormWithSchoolCheck):
    capacity = forms.IntegerField(help_text=_("This is the number of classes that can be held concurrently, "
                                              "not the amount of students that can fit in."))

    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    def clean_capacity(self):
        """
        The capacity of the room, if specified, must be a strictly positive integer!
        :return:
        """
        if self.cleaned_data['capacity'] < 1:
            self.add_error(None, forms.ValidationError(_('The capacity must be a strictly positive number!')))
        return self.cleaned_data['capacity']

    class Meta:
        model = Room
        fields = ['name', 'capacity', 'school']


class CourseForm(BaseFormWithHourSlotsGroupCheck):
    def __init__(self, user, *args, **kwargs):
        super(CourseForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = Course
        fields = ['year', 'section', 'hour_slots_group']


class HourSlotsGroupForm(BaseFormWithSchoolCheck):
    school_year = forms.ModelChoiceField(queryset=SchoolYear.objects.all().order_by('-year_start'))

    def __init__(self, *args, **kwargs):
        super(HourSlotsGroupForm, self).__init__(*args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = HourSlotsGroup
        fields = ['name', 'school', 'school_year']


class HourSlotForm(BaseFormWithHourSlotsGroupCheck):
    starts_at = forms.TimeField(
        input_formats=['%H:%M'],
        widget=forms.TextInput(attrs={
            'class': 'form-control timepicker'
        }))
    ends_at = forms.TimeField(
        input_formats=['%H:%M'],
        widget=forms.TextInput(attrs={
            'class': 'form-control timepicker'
        }))
    legal_duration = forms.DurationField(
        widget=TimeDurationWidget(show_days=False,
                                  show_hours=True,
                                  show_minutes=True,
                                  show_seconds=False,
                                  attrs={'class': 'form-control duration-input'}),
        required=False)

    def __init__(self, user, *args, **kwargs):
        super(HourSlotForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = HourSlot
        fields = ['hour_number', 'starts_at', 'ends_at', 'hour_slots_group', 'day_of_week', 'legal_duration']

    def check_conflict_on_day(self, day_of_week):
        # Check if there is already the n-th hour of the day:
        conflicting_hour_number = HourSlot.objects.filter(
            hour_slots_group=self.cleaned_data['hour_slots_group'],
            day_of_week=day_of_week,
            hour_number=self.cleaned_data['hour_number']
        )
        if conflicting_hour_number.exists():
            if self.instance is not None and conflicting_hour_number.first().pk != self.instance.id:
                self.add_error(None, forms.ValidationError(
                    _("There is already the {}{} hour of the day "
                      "for this school, day of week and school_year!".format(
                        self.cleaned_data['hour_number'],
                        _("th") if self.cleaned_data['hour_number'] % 10 > 3 else
                        _("st") if self.cleaned_data['hour_number'] % 10 == 1 else
                        _("nd") if self.cleaned_data['hour_number'] % 10 == 2 else
                        _("rd")))))

        # TODO: add tests for this check!
        conflicting_time_interval = HourSlot.objects.filter(
            hour_slots_group=self.cleaned_data['hour_slots_group'],
            day_of_week=day_of_week
        ).filter(
            # Conflicting interval is when the start of the new interval is above the end of an existing one,
            # and the end is before the start of the existing one.
            Q(starts_at__lt=self.cleaned_data['ends_at']) & Q(ends_at__gt=self.cleaned_data['starts_at'])
        )
        if conflicting_time_interval.exists():
            if self.instance is None:
                # We are creating the hour slot, and we already have one in the same time interval.
                self.add_error(None, forms.ValidationError(
                    "You cannot create an hour slot in this time interval,"
                    " since there is already one on {} from {} to {}".format(
                        models.DAYS_OF_WEEK[conflicting_time_interval.first().day_of_week][1],
                        conflicting_time_interval.first().starts_at,
                        conflicting_time_interval.first().ends_at
                    )))
            elif conflicting_time_interval.count() > 1 or \
                    conflicting_time_interval.first().pk != self.instance.pk:
                # We are editing an existing hour slot, but there is an hour slot which is not the current one
                # in the same time interval.
                self.add_error(None, forms.ValidationError(
                    "You cannot create an hour slot in this time interval,"
                    " since there is already one on {} from {} to {}".format(
                        models.DAYS_OF_WEEK[conflicting_time_interval.first().day_of_week][1],
                        conflicting_time_interval.first().starts_at,
                        conflicting_time_interval.first().ends_at
                    )))

    def clean(self):
        """
        Of course, the starts_at must be smaller than ends_at.
        Moreover, we cannot have another hour-slot with the same hour_number in the same day, school and school_year.
        Lastly, no hour slot can be held in the same interval of another existing one, the same day.
        :return:
        """
        if self.cleaned_data['starts_at'] >= self.cleaned_data['ends_at']:
            self.add_error(None, forms.ValidationError(_('The start hour must be strictly smaller that the '
                                                         'end hour.')))

        if 'hour_slots_group' in self.cleaned_data:
            # If hour_slots_group is not a key, clean_hour_slots_group has already failed.
            self.check_conflict_on_day(self.cleaned_data['day_of_week'])

        return self.cleaned_data


class HourSlotCreateForm(HourSlotForm, Form):
    hour_number = forms.IntegerField(help_text=_('This is the order of the hour during the day. '
                                                 'For instance, if hour from 9 to 10 is the second hour of the morning,'
                                                 ' hour_number field must be 2.'))
    replicate_on_days = forms.MultipleChoiceField(
        choices=models.DAYS_OF_WEEK,
        help_text=_("Do you want to replicate the hour slot in multiple days?"
                    " Use shift key and the mouse click to select multiple days."),
        label=_("Replicate on days")
    )

    def __init__(self, user, *args, **kwargs):
        super(HourSlotForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = HourSlot
        fields = ['hour_number', 'starts_at', 'ends_at', 'hour_slots_group', 'legal_duration']

    def clean(self):
        """
        Of course, the starts_at must be smaller than ends_at.
        Moreover, we cannot have another hour-slot with the same hour_number in the same day, school and school_year.
        Lastly, no hour slot can be held in the same interval of another existing one, the same day.
        :return:
        """

        if 'hour_slots_group' in self.cleaned_data:
            # If hour_slots_group is not a key, clean_hour_slots_group has already failed.
            # Replicate the checks for all the day_of_week required.
            for day_of_week in self.cleaned_data['replicate_on_days']:
                self.check_conflict_on_day(day_of_week)

    def save(self, commit=True):
        """
        Create one hour slot for every day_of_week required.
        :param commit:
        :return:
        """
        for day_of_week in self.cleaned_data['replicate_on_days']:
            # Create an hour slot for every day_of_week required.
            hs = HourSlot(
                hour_number=self.cleaned_data['hour_number'],
                starts_at=self.cleaned_data['starts_at'],
                ends_at=self.cleaned_data['ends_at'],
                hour_slots_group=self.cleaned_data['hour_slots_group'],
                day_of_week=day_of_week,
                legal_duration=self.cleaned_data['legal_duration']
            )
            hs.save()
        self.cleaned_data.pop('replicate_on_days')

        return hs


class AbsenceBlockForm(BaseFormWithHourSlotCheck, BaseFormWithTeacherCheck):
    """
    It actually inherits the clean_school method, but doesn't have the school field. It shouldn't be a problem.
    """

    def __init__(self, user, *args, **kwargs):
        """
        Add hour_slot selection based on the current school, and ordered by week_day and starts_at
        :param user: the user logged, the school is retrieved by her.
        """
        super(AbsenceBlockForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = AbsenceBlock
        fields = ['teacher', 'hour_slot']


class AbsenceBlockCreateForm(BaseFormWithTeacherCheck, Form):
    """
    It allows to create more absence blocks specifying more than one hour slots.
    """

    def __init__(self, user, *args, **kwargs):
        """
        Add hour_slot selection based on the current school, and ordered by week_day and starts_at
        :param user: the user logged, the school is retrieved by her.
        """
        super(AbsenceBlockCreateForm, self).__init__(user, *args, **kwargs)

        # Get the correct hours slots in the MultipleChoiceField
        self.fields['hour_slots'] = forms.ModelMultipleChoiceField(
            queryset=HourSlot.objects.filter(school=get_school_from_user(self.user).id).order_by(
                'hour_slots_group__name', 'day_of_week', 'starts_at'),
            help_text=_("Do you want to assign multiple absence blocks?"
                        " Use shift key and the mouse click to select multiple hour slots."),
            label=_('Hour slots')
        )
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = AbsenceBlock
        fields = ['teacher']

    def save(self, commit=True):
        """
        Create one absence block for every hour_slot selected.
        :param commit:
        :return:
        """

        for hour_slot in self.cleaned_data['hour_slots']:
            # Create an absence block for every hour_slot.
            ab = AbsenceBlock(
                teacher=self.cleaned_data['teacher'],
                hour_slot=hour_slot
            )
            ab.save()
        self.cleaned_data.pop('hour_slots')

        return ab


class HolidayForm(BaseFormWithSchoolCheck):
    school_year = forms.ModelChoiceField(queryset=SchoolYear.objects.all().order_by('-year_start'))
    date_start = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'form-control datepicker-input datepicker'
            })
    )
    date_end = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'form-control datepicker-input datepicker',
            })
    )

    def __init__(self, user, *args, **kwargs):
        super(HolidayForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

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
        courses_conflict = Assignment.objects.filter(school=self.cleaned_data['school'],
                                                     school_year=self.cleaned_data['school_year'],
                                                     date__lte=self.cleaned_data['date_end'],
                                                     date__gte=self.cleaned_data['date_start'])\
            .values_list('course').distinct()
        return self.cleaned_data

    def save(self, *args, **kwargs):
        m = super(HolidayForm, self).save(commit=False)
        assignments_to_delete = Assignment.objects.filter(school=self.cleaned_data['school'],
                                                          school_year=self.cleaned_data['school_year'],
                                                          date__lte=self.cleaned_data['date_end'],
                                                          date__gte=self.cleaned_data['date_start'])
        assignments_to_delete.delete()
        m.save()
        return m


class StageForm(BaseFormWithCourseCheck):
    date_start = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'form-control datepicker-input datepicker'
            })
    )
    date_end = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'form-control datepicker-input datepicker',
            })
    )

    def __init__(self, user, *args, **kwargs):
        super(StageForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = Stage
        fields = ['date_start', 'date_end', 'course', 'name']

    def clean(self):
        """
        We need to check whether date_start <= date_end
        :return:
        """
        if self.cleaned_data['date_start'] > self.cleaned_data['date_end']:
            self.add_error(None, forms.ValidationError(_('The date_start field can\'t be greater than the end date')))

        # TODO: Add check for schoolyear!
        return self.cleaned_data


class SubjectForm(BaseFormWithSchoolCheck):
    def __init__(self, user, *args, **kwargs):
        super(SubjectForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = Subject
        fields = ['name', 'school', 'color']


class TeachersYearlyLoadForm(BaseFormWithTeacherCheck):
    school_year = forms.ModelChoiceField(queryset=SchoolYear.objects.all().order_by('-year_start'))

    def __init__(self, user, *args, **kwargs):
        super(TeachersYearlyLoadForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = TeachersYearlyLoad
        fields = ['teacher', 'school_year', 'yearly_load', 'yearly_load_bes', 'yearly_load_co_teaching']


class CoursesYearlyLoadForm(BaseFormWithCourseCheck):
    def __init__(self, user, *args, **kwargs):
        super(CoursesYearlyLoadForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = CoursesYearlyLoad
        fields = ['course', 'yearly_load', 'yearly_load_bes']


class HoursPerTeacherInClassForm(BaseFormWithSubjectCheck, BaseFormWithCourseCheck, BaseFormWithTeacherCheck):
    def __init__(self, user, *args, **kwargs):
        super(HoursPerTeacherInClassForm, self).__init__(user, *args, **kwargs)
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = HoursPerTeacherInClass
        fields = ['course', 'subject', 'teacher', 'hours', 'hours_bes', 'hours_co_teaching']


class AssignmentForm(BaseFormWithSubjectCheck, BaseFormWithCourseCheck, BaseFormWithTeacherCheck,
                     BaseFormWithRoomCheck):
    date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': 'form-control datepicker-input datepicker'
            })
    )
    hour_start = forms.TimeField(
        input_formats=['%H:%M'],
        widget=forms.TextInput(attrs={
            'class': 'form-control timepicker'
        }))
    hour_end = forms.TimeField(
        input_formats=['%H:%M'],
        widget=forms.TextInput(attrs={
            'class': 'form-control timepicker'
        }))

    def __init__(self, user, *args, **kwargs):
        super(AssignmentForm, self).__init__(user, *args, **kwargs)
        self.fields['room'].required = False
        assign_html_style_to_visible_forms_fields(self)

    class Meta:
        model = Assignment
        fields = ['teacher', 'course', 'subject', 'date', 'hour_start', 'hour_end', 'bes',
                  'substitution', 'co_teaching', 'absent', 'room']

    def clean(self):
        """
        We need to check whether date_start <= date_end
        Moreover, we need to check whether there is a HoursPerTeacherInClass for a given course, teacher,
        school_year, school, subject, bes or co_teaching. Only if the hour is not a substitution class.
        In addition we do not want to have conflicts for the teacher, course or room.
        Lastly, we cannot have an assignment which is both BES and co-teaching.
        :return:
        """
        if not self.errors:
            # If there are already some errors, there is no need to check again!
            if self.cleaned_data['hour_start'] > self.cleaned_data['hour_end']:
                self.add_error(None,
                               forms.ValidationError(_('The start time field can\'t be greater than the end time')))
            if not self.cleaned_data['substitution']:
                # We need to check for the existence of a related HourPerTeacherInClass
                hours_teacher_in_class = HoursPerTeacherInClass.objects.filter(
                    teacher=self.cleaned_data['teacher'],
                    course__school_year=self.cleaned_data['course'].school_year,
                    course=self.cleaned_data['course'],
                    subject=self.cleaned_data['subject'])
                if not hours_teacher_in_class:
                    # If there is not an hours per teacher in class
                    self.add_error(None, forms.ValidationError(_('There is not a related '
                                                                 'teacher in class instance.')))
                elif self.cleaned_data['bes'] and hours_teacher_in_class.first().hours_bes == 0:
                    # If the hour is bes, but there are no bes hours for the teacher in class.
                    self.add_error(None, forms.ValidationError(_('The teacher doesn\'t have bes hours '
                                                                 'in this course.')))
                elif self.cleaned_data['co_teaching'] and hours_teacher_in_class.first().co_teaching == 0:
                    # If the hour is co-teaching, but there are no co-teaching for the teacher in class.
                    self.add_error(None, forms.ValidationError(_('The teacher doesn\'t have co-teaching hours '
                                                                 'in this course.')))
                elif (not self.cleaned_data['bes'] and
                      not self.cleaned_data['co_teaching']) and hours_teacher_in_class.first().hours == 0:
                    # If the hour is "normal", but the teacher has no normal hours in the class.
                    self.add_error(None, forms.ValidationError(_('The teacher has only bes or co-teaching hours '
                                                                 'in this course.')))

            conflicts_teacher = Assignment.objects.filter(
                teacher=self.cleaned_data['teacher'],
                course__school_year=self.cleaned_data['course'].school_year,
                hour_start=self.cleaned_data['hour_start'],
                hour_end=self.cleaned_data['hour_end'],
                date=self.cleaned_data['date']) \
                .exclude(
                id=self.instance.id if self.instance is not None else None
            )

            if conflicts_teacher:
                self.add_error(None, forms.ValidationError(_("The teacher is already in another class {}.".format(
                    str([c.course for c in conflicts_teacher])  # TODO: Fix visualization of this error.
                ))))
            if self.cleaned_data['room'] is not None:
                conflict_room = Assignment.objects.filter(
                    room=self.cleaned_data['room'],
                    course__school_year=self.cleaned_data['course'].school_year,
                    hour_start=self.cleaned_data['hour_start'],
                    hour_end=self.cleaned_data['hour_end'],
                    date=self.cleaned_data['date']) \
                    .exclude(
                    id=self.instance.id if self.instance is not None else None
                )
                if conflict_room.count() >= self.cleaned_data['room'].capacity:
                    self.add_error(None, forms.ValidationError(
                        _("The room {} has already reached its maximum capacity").format(
                            self.cleaned_data['room'].name)))

        # Check that only one in bes and co_teaching is set to true.
        if self.cleaned_data['bes'] and self.cleaned_data['co_teaching']:
            # They cannot be both true.
            self.add_error(None, forms.ValidationError(
                _("An assignment can only be BES or co-teaching, but not both.")
            ))
        return self.cleaned_data
