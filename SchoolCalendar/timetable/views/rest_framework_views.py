from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist

from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday, \
    Stage, Subject, HoursPerTeacherInClass, Assignment, Room, TeachersYearlyLoad, CoursesYearlyLoad, HourSlotsGroup
from timetable.serializers import TeacherSerializer, CourseYearOnlySerializer, CourseSectionOnlySerializer, \
    HolidaySerializer, StageSerializer, HourSlotSerializer, HoursPerTeacherInClassSerializer, AssignmentSerializer, \
    AbsenceBlockSerializer, TeacherSubstitutionSerializer, SubjectSerializer, ReplicationConflictsSerializer, \
    RoomSerializer, TeacherSummarySerializer, CourseSummarySerializer, TeachersYearlyLoadSerializer, \
    CoursesYearlyLoadSerializer, HourSlotsGroupSerializer
from timetable.permissions import SchoolAdminCanWriteDelete, TeacherCanView
from timetable.filters import TeacherFromSameSchoolFilterBackend, HolidayPeriodFilter, QuerysetFromSameSchool, \
    StageFilter, HourSlotFilter, HoursPerTeacherInClassFilter, CourseSectionOnlyFilter, CourseYearOnlyFilter, \
    AssignmentFilter, AbsenceBlockFilter, RoomFilter, TeachersYearlyLoadFilter, CoursesYearlyLoadFilter, \
    CourseFromSameSchoolFilterBackend, HourSlotsGroupFromSameSchoolFilterBackend, HourSlotsGroupFilter
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from timetable import utils


class TeacherViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = [OrderingFilter, QuerysetFromSameSchool]
    ordering = ['last_name', 'first_name']


class TeacherSummaryViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = TeacherSummarySerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = [OrderingFilter, QuerysetFromSameSchool]
    ordering = ['last_name', 'first_name']

    def get_queryset(self):
        """
        :return: only the teachers of the passed year, if given
        """
        teachers_teaching_in_the_year = HoursPerTeacherInClass.objects.none()
        school_year = self.request.query_params.get('school_year')
        if school_year:
            teachers_teaching_in_the_year = HoursPerTeacherInClass.objects.filter(school_year=school_year).values('teacher')
        return Teacher.objects.filter(id__in=teachers_teaching_in_the_year)


class TeachersYearlyLoadViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = TeachersYearlyLoad.objects.all()
    serializer_class = TeachersYearlyLoadSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filterset_class = TeachersYearlyLoadFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter, TeacherFromSameSchoolFilterBackend]
    ordering = ['teacher__last_name', 'teacher__first_name']


class CoursesYearlyLoadViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = CoursesYearlyLoad.objects.all()
    serializer_class = CoursesYearlyLoadSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filterset_class = CoursesYearlyLoadFilter
    filter_backends = [DjangoFilterBackend, OrderingFilter, CourseFromSameSchoolFilterBackend]
    ordering = ['course__year', 'course__section']


class CourseSummaryViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = CourseSummarySerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = [OrderingFilter, QuerysetFromSameSchool]
    ordering = ['year', 'section']

    def get_queryset(self):
        """
        :return: only the courses of the desired year, if given
        """
        school_year = self.request.query_params.get('school_year')
        if school_year:
            return Course.objects.filter(school_year=school_year)
        return Course.objects.all()


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
    filter_backends = (DjangoFilterBackend, OrderingFilter, HourSlotsGroupFromSameSchoolFilterBackend)
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
    filter_backends = (DjangoFilterBackend, OrderingFilter, HourSlotsGroupFromSameSchoolFilterBackend)
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


class HourSlotsGroupViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    queryset = HourSlotsGroup.objects.all()
    serializer_class = HourSlotsGroupSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, OrderingFilter, QuerysetFromSameSchool)
    filterset_class = HourSlotsGroupFilter
    ordering = ['school_year', 'name']


class HourSlotViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    queryset = HourSlot.objects.all()
    serializer_class = HourSlotSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, OrderingFilter, HourSlotsGroupFromSameSchoolFilterBackend)
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

    def destroy(self, request, *args, **kwargs):
        """
        If the assignment that we are deleting is a substitution, then we need to mark the substituted assignments
        as not absent anymore (which means that they still need to be substituted using the Substitute Teacher
        feature).
        It applies only if there are no other substitutions in such time slot, for the given course.
        For instance, if we have 2 substitution assignments and we are deleting one, then we can still consider the
        substituted assignments as properly handled.
        Actually, there should be no need for handling multiple substitutions,
        since we can have at most one at the moment, but for future possible improvements we will be more general.
        """
        instance = self.get_object()
        if instance.substitution or instance.free_substitution:
            # If we are deleting a substitution
            assignments_same_hour = Assignment.objects.filter(
                course=instance.course,
                date=instance.date,
                hour_start=instance.hour_start,
                hour_end=instance.hour_end).exclude(id=instance.id)
            if not assignments_same_hour.filter(
                    substitution=True, free_substitution=True).exists():
                # If we have no other substitution in the same hour slot
                for a in assignments_same_hour.exclude(
                        substitution=True, free_substitution=True):
                    # Set the absent to False for all other assignments.
                    a.absent = False
                    a.save()
        return super(AssignmentViewSet, self).destroy(request, *args, **kwargs)


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


class RoomTimetableViewSet(ListModelMixin, GenericViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)
    filterset_class = AssignmentFilter
    lookup_url_kwarg = ['room_pk']

    def get_queryset(self):
        # Return all assignments for a room in a given time period
        room_pk = self.kwargs.get('room_pk')
        assignments = Assignment.objects.filter(room_id=room_pk)
        return assignments
