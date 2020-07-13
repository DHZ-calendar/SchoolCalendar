from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, Serializer, IntegerField, CharField, \
    DateField, SerializerMethodField, ValidationError, PrimaryKeyRelatedField, BooleanField

import datetime

from timetable.models import Teacher, Holiday, Stage, AbsenceBlock, Assignment, HoursPerTeacherInClass, HourSlot, \
    Course, Subject, Room
from timetable import utils


class CourseYearOnlySerializer(Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    year = IntegerField()


class CourseSectionOnlySerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'section', 'year']


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


class TeacherSerializer(ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'url', 'first_name', 'last_name', 'username', 'email', 'is_staff', 'school', 'notes']


class TeacherSummarySerializer(ModelSerializer):
    hours_done = SerializerMethodField()  # normal hours done in the given date period
    hours_bes_done = SerializerMethodField()  # bes hours done in the given date period
    total_hours = SerializerMethodField()  # total amount of hours to be done in the year
    total_hours_bes = SerializerMethodField()  # same but for bes hours
    hours_substitution_done = SerializerMethodField()  # substitution hours done in the given date period

    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'hours_done', 'hours_bes_done', 'total_hours', 'total_hours_bes',
                  'hours_substitution_done']

    def get_hours_done(self, obj, *args, **kwargs):
        # Get start_date and end_date parameters from url
        start_date = self.context.get('request').query_params.get('start_date')
        end_date = self.context.get('request').query_params.get('end_date')

        school_year = self.context.get('request').query_params.get('school_year')

        assignments = Assignment.objects.filter(teacher=obj.id,
                                                school=obj.school,
                                                school_year=school_year,
                                                substitution=False,
                                                bes=False).values('date__week_day', 'hour_start', 'hour_end')
        # Filter in a time interval
        if start_date:
            assignments = assignments.filter(date__gte=start_date)
        if end_date:
            assignments = assignments.filter(date__lte=end_date)

        for el in assignments:
            el['date__week_day'] = utils.convert_weekday_into_0_6_format(el['date__week_day'])

        hours_slots = HourSlot.objects.filter(school=obj.school,
                                              school_year=school_year).values("day_of_week", "starts_at",
                                                                              "ends_at", "legal_duration")
        total = utils.compute_total_hours_assignments(assignments, hours_slots)
        return total

    def get_hours_bes_done(self, obj, *args, **kwargs):
        # Get start_date and end_date parameters from url
        start_date = self.context.get('request').query_params.get('start_date')
        end_date = self.context.get('request').query_params.get('end_date')

        school_year = self.context.get('request').query_params.get('school_year')

        assignments = Assignment.objects.filter(teacher=obj.id,
                                                school=obj.school,
                                                school_year=school_year,
                                                bes=True).values('date__week_day', 'hour_start', 'hour_end')
        # Filter in a time interval
        if start_date:
            assignments = assignments.filter(date__gte=start_date)
        if end_date:
            assignments = assignments.filter(date__lte=end_date)

        for el in assignments:
            el['date__week_day'] = utils.convert_weekday_into_0_6_format(el['date__week_day'])

        hours_slots = HourSlot.objects.filter(school=obj.school,
                                              school_year=school_year).values("day_of_week", "starts_at",
                                                                              "ends_at", "legal_duration")
        total = utils.compute_total_hours_assignments(assignments, hours_slots)
        return total

    def get_hours_substitution_done(self, obj, *args, **kwargs):
        # Get start_date and end_date parameters from url
        start_date = self.context.get('request').query_params.get('start_date')
        end_date = self.context.get('request').query_params.get('end_date')

        school_year = self.context.get('request').query_params.get('school_year')

        assignments = Assignment.objects.filter(teacher=obj.id,
                                                school=obj.school,
                                                school_year=school_year,
                                                substitution=True).values('date__week_day', 'hour_start', 'hour_end')
        # Filter in a time interval
        if start_date:
            assignments = assignments.filter(date__gte=start_date)
        if end_date:
            assignments = assignments.filter(date__lte=end_date)

        for el in assignments:
            el['date__week_day'] = utils.convert_weekday_into_0_6_format(el['date__week_day'])

        hours_slots = HourSlot.objects.filter(school=obj.school,
                                              school_year=school_year).values("day_of_week", "starts_at",
                                                                              "ends_at", "legal_duration")
        total = utils.compute_total_hours_assignments(assignments, hours_slots)
        return total

    # TODO: complete the methods when the year load is done
    def get_total_hours(self, obj, *args, **kwargs):
        return 0

    def get_total_hours_bes(self, obj, *args, **kwargs):
        return 0


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'school', 'capacity']


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'year', 'school', 'school_year', 'section']


class SubjectSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'school']


class HolidaySerializer(AbstractTimePeriodSerializer):
    """
    Returns the holiday filtered in a given period.
    """

    class Meta:
        model = Holiday
        fields = ['id', 'start', 'end', 'date_start', 'date_end', 'name', 'school', 'school_year']


class StageSerializer(AbstractTimePeriodSerializer):
    """
    Stage Serializer with period filter
    """
    course = CourseSerializer()

    class Meta:
        model = Stage
        fields = ['id', 'start', 'end', 'date_start', 'date_end', 'name', 'course', 'school']


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
    missing_hours_bes = SerializerMethodField()
    teacher = TeacherSerializer()
    subject = SubjectSerializer()
    course = CourseSerializer()

    class Meta:
        model = HoursPerTeacherInClass
        fields = ['id', 'teacher', 'course', 'subject', 'school_year', 'school', 'hours', 'hours_bes', 'missing_hours',
                  'missing_hours_bes']

    def get_missing_hours(self, obj, *args, **kwargs):
        """
        Missing hours is computed over the hours the teacher needs to do for a given class,
        and the hours already planned in that class.
        :param obj:
        :param args:
        :param kwargs:
        :return:
        """
        # Get start_date and end_date parameters from url
        start_date = self.context.get('request').query_params.get('start_date')
        end_date = self.context.get('request').query_params.get('end_date')
        assignments = Assignment.objects.filter(teacher=obj.teacher,
                                                course=obj.course,
                                                subject=obj.subject,
                                                school=obj.school,
                                                school_year=obj.school_year,
                                                bes=False).values('date__week_day', 'hour_start', 'hour_end')
        # Filter in a time interval
        if start_date:
            assignments = assignments.filter(date__gte=start_date)
        if end_date:
            assignments = assignments.filter(date__lte=end_date)

        for el in assignments:
            el['date__week_day'] = utils.convert_weekday_into_0_6_format(el['date__week_day'])

        hours_slots = HourSlot.objects.filter(school=obj.school,
                                              school_year=obj.school_year).values("day_of_week", "starts_at",
                                                                                  "ends_at", "legal_duration")
        total = utils.compute_total_hours_assignments(assignments, hours_slots)
        return obj.hours - total

    def get_missing_hours_bes(self, obj, *args, **kwargs):
        """
            Missing hours is computed over the hours the teacher needs to do for a given class,
            and the hours already planned in that class.
            :param obj:
            :param args:
            :param kwargs:
            :return:
            """
        start_date = self.context.get('request').query_params.get('start_date')
        end_date = self.context.get('request').query_params.get('end_date')

        assignments = Assignment.objects.filter(teacher=obj.teacher,
                                                course=obj.course,
                                                subject=obj.subject,
                                                school=obj.school,
                                                school_year=obj.school_year,
                                                bes=True).values('date__week_day', 'hour_start', 'hour_end')

        # Filter in a time interval
        if start_date:
            assignments = assignments.filter(date__gte=start_date)
        if end_date:
            assignments = assignments.filter(date__lte=end_date)

        for el in assignments:
            el['date__week_day'] = utils.convert_weekday_into_0_6_format(el['date__week_day'])

        hours_slots = HourSlot.objects.filter(school=obj.school,
                                              school_year=obj.school_year).values("day_of_week", "starts_at",
                                                                                  "ends_at", "legal_duration")
        total = utils.compute_total_hours_assignments(assignments, hours_slots)

        return obj.hours_bes - total


class AssignmentSerializer(ModelSerializer):
    """
    Serializer for teachers
    """
    teacher = TeacherSerializer(read_only=True)
    teacher_id = PrimaryKeyRelatedField(write_only=True, queryset=Teacher.objects.all(), source='teacher')
    subject = SubjectSerializer(read_only=True)
    subject_id = PrimaryKeyRelatedField(write_only=True, queryset=Subject.objects.all(), source='subject')
    hour_slot = SerializerMethodField(read_only=True)
    course_id = PrimaryKeyRelatedField(write_only=True, queryset=Course.objects.all(), source='course')
    course = CourseSerializer(read_only=True)
    room_id = PrimaryKeyRelatedField(write_only=True, required=False, queryset=Room.objects.all(), source='room')
    room = RoomSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        super(AssignmentSerializer, self).__init__(*args, **kwargs)
        self.user = self.context['request'].user

    def get_hour_slot(self, obj, *args, **kwargs):
        """
        OLDTODO: should better add the hour slot as as a FK in the Assignment model
        RESP: No, otherwise we could not support lecture extra from the standard hour_slots
        Per each Assignment, it returns the corresponding HourSlot (if it exists), otherwise None
        The problem is that it makes a query for each instance of assignment!
        :param obj: the assignment instance
        :return:
        """
        el = HourSlot.objects.filter(
            day_of_week=obj.date.weekday(),
            starts_at=obj.hour_start,
            ends_at=obj.hour_end,
            school=obj.school,
            school_year=obj.school_year
        )
        if el:
            return el[0].id
        return None

    def validate(self, attrs):
        """
        Check whether the hour_start is <= hour_end
        :param attrs: the values to validate
        :return: attrs or raises ValidationError
        """
        if attrs['hour_start'] > attrs['hour_end']:
            raise ValidationError(_('The start hour field can\'t be greater than the end hour'))
        return attrs

    def validate_subject_id(self, value):
        """
        Check whether the course is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a course.
        :return:
        """
        if utils.get_school_from_user(self.user) != value.school:
            raise ValidationError(_("The subject {} is not taught in this School ({}).").format(
                value, utils.get_school_from_user(self.user)
            ))
        return value

    def validate_course(self, value):
        """
        Check whether the course is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a course.
        :return:
        """
        if utils.get_school_from_user(self.user) != value.school:
            raise ValidationError(_('The course {} is not taught in this School ({}).').format(
                value, utils.get_school_from_user(self.user)
            ))
        return value

    def validate_school(self, value):
        """
        Check whether the school is the correct one for the admin user logged.
        :param value:
        :return:
        """
        if utils.get_school_from_user(self.user) != value:
            raise ValidationError(_('The school {} is not a valid choice.').format(
                value
            ))
        return value

    def validate_teacher(self, value):
        """
        Check whether the teacher is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a teacher.
        :return:
        """
        if utils.get_school_from_user(self.user) != value.school:
            raise ValidationError(_('The teacher {} does not teach in this School ({}).'.format(
                value, value.school
            )))
        return value

    def validate_room(self, value):
        """
        Check whether the room is in the school of the user logged.
        Somewhere else we should check that the user logged has enough permissions to do anything with a room.
        :return:
        """
        if utils.get_school_from_user(self.user) != value.school:
            raise ValidationError(_('The room {} cannot be used in this school ({}).'.format(
                value, value.school
            )))
        return value

    class Meta:
        model = Assignment
        fields = '__all__'


class AbsenceBlockSerializer(ModelSerializer):
    teacher = TeacherSerializer()
    hour_slot_text = SerializerMethodField(read_only=True)

    def get_hour_slot_text(self, obj, *args, **kwargs):
        return str(obj.hour_slot)

    class Meta:
        model = AbsenceBlock
        fields = ['teacher', 'hour_slot', 'hour_slot_text', 'id']


class TeacherSubstitutionSerializer(ModelSerializer):
    has_hour_before = SerializerMethodField()
    has_hour_after = SerializerMethodField()
    substitutions_made_so_far = SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(TeacherSubstitutionSerializer, self).__init__(*args, **kwargs)
        self.user = self.context['request'].user
        # We have already checked in view .get_queryset whether the Assignment exists.
        self.assignment_to_substitute = Assignment.objects.get(id=self.context['request'].assignment_pk)

    class Meta:
        model = Teacher
        fields = ['school', 'notes', 'has_hour_before', 'has_hour_after', 'substitutions_made_so_far', 'first_name',
                  'last_name', 'id']

    def get_substitutions_made_so_far(self, obj, *args, **kwargs):
        return Assignment.objects.filter(teacher=obj.id,
                                         school=obj.school,
                                         school_year=self.assignment_to_substitute.school_year,
                                         substitution=True).count()

    def get_has_hour_after(self, obj, *args, **kwargs):
        related_hour_slot = HourSlot.objects.filter(starts_at=self.assignment_to_substitute.hour_start,
                                                    ends_at=self.assignment_to_substitute.hour_end,
                                                    day_of_week=self.assignment_to_substitute.date.weekday(),
                                                    school=obj.school,
                                                    school_year=self.assignment_to_substitute.school_year).first()
        if not related_hour_slot:
            # If there is not a related hour slot, then we are talking about a non standard assignment.
            # We return False by default
            return False
        if related_hour_slot.hour_number == max(HourSlot.objects.filter(
                day_of_week=self.assignment_to_substitute.date.weekday(),
                school=obj.school,
                school_year=self.assignment_to_substitute.school_year)
                                                        .values_list('hour_number')[0]):
            # It is the last hour of the day, the teacher can't be at school after.
            return False
        later_hour_slot = HourSlot.objects.filter(school=obj.school,
                                                  school_year=self.assignment_to_substitute.school_year,
                                                  hour_number=related_hour_slot.hour_number + 1,
                                                  day_of_week=self.assignment_to_substitute.date.weekday()).first()
        if not later_hour_slot:
            # There is no later hour slot, therefore we can't say.
            return False

        return Assignment.objects.filter(teacher=obj,
                                         date=self.assignment_to_substitute.date,
                                         school=obj.school,
                                         school_year=self.assignment_to_substitute.school_year,
                                         hour_start=later_hour_slot.starts_at,
                                         hour_end=later_hour_slot.ends_at).exists()

    def get_has_hour_before(self, obj, *args, **kwargs):
        related_hour_slot = HourSlot.objects.filter(starts_at=self.assignment_to_substitute.hour_start,
                                                    ends_at=self.assignment_to_substitute.hour_end,
                                                    day_of_week=self.assignment_to_substitute.date.weekday(),
                                                    school=obj.school,
                                                    school_year=self.assignment_to_substitute.school_year).first()
        if not related_hour_slot:
            # If there is not a related hour slot, then we are talking about a non standard assignment.
            # We return False by default
            return False
        if related_hour_slot.hour_number == 1:
            # It is the first hour of the day, the teacher can't be at school before.
            return False
        previous_hour_slot = HourSlot.objects.filter(school=obj.school,
                                                     school_year=self.assignment_to_substitute.school_year,
                                                     hour_number=related_hour_slot.hour_number - 1,
                                                     day_of_week=self.assignment_to_substitute.date.weekday()).first()
        if not previous_hour_slot:
            # There is no previous hour slot, therefore we can't say.
            return False

        return Assignment.objects.filter(teacher=obj,
                                         date=self.assignment_to_substitute.date,
                                         school=obj.school,
                                         school_year=self.assignment_to_substitute.school_year,
                                         hour_start=previous_hour_slot.starts_at,
                                         hour_end=previous_hour_slot.ends_at).exists()


class ReplicationConflictsSerializer(Serializer):
    teacher_conflicts = SerializerMethodField('get_teacher_conflicts')
    course_conflicts = SerializerMethodField('get_course_conflicts')
    room_conflicts = SerializerMethodField('get_room_conflicts')

    def get_teacher_conflicts(self, obj):
        serializer_context = {'request': self.context.get('request')}
        serializer = AssignmentSerializer(self.initial_data['teacher_conflicts'], many=True, context=serializer_context)
        return serializer.data

    def get_course_conflicts(self, obj):
        serializer_context = {'request': self.context.get('request')}
        serializer = AssignmentSerializer(self.initial_data['course_conflicts'], many=True, context=serializer_context)
        return serializer.data

    def get_room_conflicts(self, obj):
        serializer_context = {'request': self.context.get('request')}
        serializer = AssignmentSerializer(self.initial_data['room_conflicts'], many=True, context=serializer_context)
        return serializer.data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SubstitutionSerializer(Serializer):
    available_teachers = SerializerMethodField('get_available_teachers')
    other_teachers = SerializerMethodField('get_other_teachers')

    def get_available_teachers(self, obj):
        serializer_context = {'request': self.context.get('request')}
        serializer = TeacherSubstitutionSerializer(self.initial_data['available_teachers'], many=True,
                                                   context=serializer_context)
        return serializer.data

    def get_other_teachers(self, obj):
        serializer_context = {'request': self.context.get('request')}
        serializer = TeacherSubstitutionSerializer(self.initial_data['other_teachers'], many=True,
                                                   context=serializer_context)
        return serializer.data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
