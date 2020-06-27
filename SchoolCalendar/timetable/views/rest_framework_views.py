from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist

from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday, \
    Stage, Subject, HoursPerTeacherInClass, Assignment, Room
from timetable.serializers import TeacherSerializer, CourseYearOnlySerializer, CourseSectionOnlySerializer, \
    HolidaySerializer, StageSerializer, HourSlotSerializer, HoursPerTeacherInClassSerializer, AssignmentSerializer, \
    AbsenceBlockSerializer, TeacherSubstitutionSerializer, SubjectSerializer, ReplicationConflictsSerializer, \
    RoomSerializer
from timetable.permissions import SchoolAdminCanWriteDelete, TeacherCanView
from timetable.filters import TeacherFromSameSchoolFilterBackend, HolidayPeriodFilter, QuerysetFromSameSchool, \
    StageFilter, HourSlotFilter, HoursPerTeacherInClassFilter, CourseSectionOnlyFilter, CourseYearOnlyFilter, \
    AssignmentFilter, AbsenceBlockFilter, RoomFilter
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from timetable import utils


class TeacherViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = [OrderingFilter, QuerysetFromSameSchool]
    ordering = ['last_name', 'first_name']


class AbsenceBlockViewSet(ListModelMixin, GenericViewSet):
    queryset = AbsenceBlock.objects.all()
    serializer_class = AbsenceBlockSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filterset_class = AbsenceBlockFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter, TeacherFromSameSchoolFilterBackend]
    ordering = ['teacher__last_name', 'teacher__first_name', 'hour_slot__day_of_week', 'hour_slot__starts_at']


class SubjectViewSet(ListModelMixin, GenericViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool)
    ordering = ['name']


class RoomViewSet(ListModelMixin, GenericViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filterset_class = RoomFilter
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool)
    ordering = ['name']


class CourseYearOnlyListViewSet(ListModelMixin, GenericViewSet):
    serializer_class = CourseYearOnlySerializer
    queryset = Course.objects.all()  # I think it gets overridden by get_queryset
    permission_classes = [IsAuthenticated]
    filterset_class = CourseYearOnlyFilter
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool)
    ordering = ['year']

    def get_queryset(self):
        """
        :return: only the years of courses of the user logged's school
        """
        school = utils.get_school_from_user(self.request.user)
        if school:
            return Course.objects.filter(school=school).values('year').distinct()


class CourseSectionOnlyListViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin,
                                   GenericViewSet):
    serializer_class = CourseSectionOnlySerializer
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filterset_class = CourseSectionOnlyFilter
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool)
    ordering = ['year', 'section']


class HolidayViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool)
    filterset_class = HolidayPeriodFilter
    ordering = ['date_start', 'name']


class StageViewSet(ListModelMixin, GenericViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool)
    filterset_class = StageFilter
    ordering = ['date_start', 'name']


class HourSlotViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    queryset = HourSlot.objects.all()
    serializer_class = HourSlotSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool,)
    filterset_class = HourSlotFilter
    ordering = ['day_of_week', 'starts_at']


class HoursPerTeacherInClassViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin,
                                    GenericViewSet):
    """
    Can accept as parameter in the url (start_date, end_date) a period of time where to compute
    the total hour missing for a teacher.
    """
    queryset = HoursPerTeacherInClass.objects.all()
    serializer_class = HoursPerTeacherInClassSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool,)
    filterset_class = HoursPerTeacherInClassFilter
    ordering = ['teacher__last_name', 'teacher__first_name', 'course__year', 'course__section', 'subject__name']


class AssignmentViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, CreateModelMixin,
                        GenericViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool,)
    filterset_class = AssignmentFilter
    ordering = ['teacher__last_name', 'teacher__first_name', 'course__year', 'course__section', 'hour_start']


class TeacherAssignmentsViewSet(UserPassesTestMixin, ListModelMixin, GenericViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool,)
    filterset_class = AssignmentFilter  # Here you should not specify any course
    lookup_url_kwarg = ['teacher_pk', 'school_year_pk']
    ordering = ['hour_start']

    def test_func(self):
        """
        :return: the teacher must be in the same school as the user in the request.
        """
        teacher = Teacher.objects.filter(id=self.kwargs['teacher_pk']).first()
        return teacher and teacher.school == utils.get_school_from_user(self.request.user)

    def get_queryset(self, *args, **kwargs):
        """
        Get all assignments for the given teacher, in the given time period.
        :param args:
        :param kwargs:
        :return:
        """
        teacher_pk = self.kwargs.get(self.lookup_url_kwarg[0])
        school_year_pk = self.kwargs.get(self.lookup_url_kwarg[1])
        try:
            teacher = Teacher.objects.get(id=teacher_pk)  # Used to retrieve other absences and assignments
            school_year = SchoolYear.objects.get(id=school_year_pk)

        except ObjectDoesNotExist:
            # If trying to retrieve an invalid object:
            return Assignment.objects.none()

        return Assignment.objects.filter(teacher=teacher,
                                         absent=False,
                                         school_year=school_year)


class AbsenceBlocksPerTeacherViewSet(UserPassesTestMixin, ListModelMixin, GenericViewSet):
    queryset = AbsenceBlock.objects.all()
    serializer_class = AbsenceBlockSerializer
    filter_backends = (DjangoFilterBackend,)
    lookup_url_kwarg = ['teacher_pk', 'school_year_pk']

    def test_func(self):
        """
        The teacher requested is in the same school as the user doing the request.
        Actually when the teacher doesn't exist it should return 404, now instead it returns 403.
        :return:
        """
        teacher_pk = self.kwargs.get('teacher_pk')
        return Teacher.objects.filter(id=teacher_pk).exists() and \
               Teacher.objects.get(id=teacher_pk).school == utils.get_school_from_user(self.request.user)

    def get_queryset(self, *args, **kwargs):
        """
        Get all absence blocks for the given teacher, in the given time period.
        :param args:
        :param kwargs:
        :return:
        """
        teacher_pk = self.kwargs.get('teacher_pk')
        school_year_pk = self.kwargs.get('school_year_pk')
        try:
            #  Return the teacher, but only among the ones in the school of the currently logged in user
            teacher = Teacher.objects.get(id=teacher_pk, school=utils.get_school_from_user(self.request.user))
            school_year = SchoolYear.objects.get(id=school_year_pk)

        except ObjectDoesNotExist:
            # If trying to retrieve an invalid object:
            return Assignment.objects.none()

        return AbsenceBlock.objects.filter(teacher=teacher,
                                           school_year=school_year)


class TeacherSubstitutionViewSet(ListModelMixin, GenericViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSubstitutionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)
    lookup_url_kwarg = 'assignment_pk'

    def dispatch(self, request, *args, **kwargs):
        request.assignment_pk = kwargs.get('assignment_pk')
        return super(TeacherSubstitutionViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return all teachers for a certain school.
        # May need to add only teachers for which there is at least one hour_per_teacher_in_class instance in
        # the given school_year
        if not Assignment.objects.filter(id=self.kwargs.get('assignment_pk'),
                                         school=utils.get_school_from_user(self.request.user).id).exists():
            return Teacher.objects.none()
        a = Assignment.objects.get(id=self.kwargs.get('assignment_pk'),
                                   school=utils.get_school_from_user(self.request.user).id)

        teachers_list = Teacher.objects.filter(school=utils.get_school_from_user(self.request.user)) \
            .exclude(id=a.teacher.id) \
            .filter(hoursperteacherinclass__school_year=a.school_year).distinct()

        # Remove all teachers who already have assignments in that hour
        teachers_list = teachers_list.exclude(assignment__date=a.date,
                                              assignment__hour_start=a.hour_start,
                                              assignment__hour_end=a.hour_end).distinct()

        # Remove all teachers who have an absence block there.
        hour_slot = HourSlot.objects.filter(school=a.school,
                                            school_year=a.school_year,
                                            starts_at=a.hour_start,
                                            ends_at=a.hour_end).first()
        if hour_slot:
            # If there is the hour_slot, then exclude all teachers that have an absence block in that period.
            # TODO: do some tests with absence blocks!!
            teachers_list = teachers_list.exclude(absenceblock__hour_slot=hour_slot)

        return teachers_list


class TeacherTimetableViewSet(ListModelMixin, GenericViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated, TeacherCanView]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)
    filterset_class = AssignmentFilter

    def get_queryset(self):
        # Return all assignments for a teacher in a given time period
        assignments = Assignment.objects.filter(teacher_id=self.request.user.id)
        return assignments
