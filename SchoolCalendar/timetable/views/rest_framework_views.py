from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.db.models import Q

import datetime

from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday, \
    Stage, Subject, HoursPerTeacherInClass, Assignment
from timetable.serializers import TeacherSerializer, CourseYearOnlySerializer, CourseSectionOnlySerializer, \
    HolidaySerializer, StageSerializer, HourSlotSerializer, HoursPerTeacherInClassSerializer, AssignmentSerializer, \
    AbsenceBlockSerializer, TeacherSubstitutionSerializer, SubjectSerializer, ReplicationConflictsSerializer
from timetable.permissions import SchoolAdminCanWriteDelete, TeacherCanView
from timetable.filters import TeacherFromSameSchoolFilterBackend, HolidayPeriodFilter, QuerysetFromSameSchool, \
    StageFilter, HourSlotFilter, HoursPerTeacherInClassFilter, CourseSectionOnlyFilter, CourseYearOnlyFilter, \
    AssignmentFilter, AbsenceBlockFilter
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from timetable import utils


class TeacherViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = [QuerysetFromSameSchool]


class AbsenceBlockViewSet(ListModelMixin, GenericViewSet):
    queryset = AbsenceBlock.objects.all()
    serializer_class = AbsenceBlockSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filterset_class = AbsenceBlockFilter
    filter_backends = [DjangoFilterBackend, TeacherFromSameSchoolFilterBackend]


class SubjectViewSet(ListModelMixin, GenericViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)


class CourseYearOnlyListViewSet(ListModelMixin, GenericViewSet):
    serializer_class = CourseYearOnlySerializer
    queryset = Course.objects.all()  # I think it gets overridden by get_queryset
    permission_classes = [IsAuthenticated]
    filterset_class = CourseYearOnlyFilter
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)

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
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)


class HolidayViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)
    filterset_class = HolidayPeriodFilter


class StageViewSet(ListModelMixin, GenericViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)
    filterset_class = StageFilter


class HourSlotViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    queryset = HourSlot.objects.all()
    serializer_class = HourSlotSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool,)
    filterset_class = HourSlotFilter


class HoursPerTeacherInClassViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin,
                                    GenericViewSet):
    """
    Can accept as parameter in the url (start_date, end_date) a period of time where to compute
    the total hour missing for a teacher.
    """
    queryset = HoursPerTeacherInClass.objects.all()
    serializer_class = HoursPerTeacherInClassSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool,)
    filterset_class = HoursPerTeacherInClassFilter


class AssignmentViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, CreateModelMixin,
                        GenericViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated, SchoolAdminCanWriteDelete]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool,)
    filterset_class = AssignmentFilter


class TeacherAssignmentsViewSet(UserPassesTestMixin, ListModelMixin, GenericViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool,)
    filterset_class = AssignmentFilter  # Here you should not specify any course
    lookup_url_kwarg = ['teacher_pk', 'school_year_pk']

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


class ReplicateAssignmentView(UserPassesTestMixin, View):
    def test_func(self):
        assignments = self.request.POST.getlist('assignments[]')

        for assign in assignments:
            if not (utils.is_adminschool(self.request.user) and Assignment.objects.filter(id=assign).exists() and
               Assignment.objects.get(id=assign).school == utils.get_school_from_user(self.request.user)):
                return False
        return True

    def post(self, request, *args, **kwargs):
        """
        Check conflicts with the assignments of a week if repeated in a specific date range
        """
        assignments = request.POST.getlist('assignments[]')
        try:
            from_date = datetime.datetime.strptime(kwargs.get('from'), '%Y-%m-%d').date()
            to_date = datetime.datetime.strptime(kwargs.get('to'), '%Y-%m-%d').date()
            course_conflicts = Assignment.objects.none()
            teacher_conflicts = Assignment.objects.none()
            for assign in assignments:
                a = Assignment.objects.get(pk=assign)
                # Return all assignments from the same course or teacher that would collide in the future.
                # excluding the assignment in the url.
                conflicts = Assignment.objects.filter(school_year=a.school_year,
                                                      # _week_day returns dates Sun-Sat (1,7), while weekday (Mon, Sun) (0,6)
                                                      date__week_day=(a.date.weekday() + 2) % 7,
                                                      hour_start=a.hour_start) \
                    .filter(date__gte=from_date, date__lte=to_date) \
                    .exclude(id=a.pk)
                course_conflicts |= conflicts.filter(course=a.course)
                teacher_conflicts |= conflicts.filter(teacher=a.teacher)

            data = dict(course_conflicts=course_conflicts, teacher_conflicts=teacher_conflicts)
            serializer = ReplicationConflictsSerializer(data=data, context={'request': request})
            serializer.is_valid()
            return JsonResponse(serializer.data)
        except ObjectDoesNotExist:
            return HttpResponse(_("One of the assignments specified doesn't exist"), 400)


class CreateMultipleAssignmentsView(UserPassesTestMixin, View):

    def test_func(self):
        """
        Returns True only when the user logged is an admin, and it is replicating an assignment that
        is in the correct school
        :return:
        """
        assignment_pk = self.kwargs.get('assignment_pk')
        return utils.is_adminschool(self.request.user) and Assignment.objects.filter(id=assignment_pk).exists() and \
               Assignment.objects.get(id=assignment_pk).school == utils.get_school_from_user(self.request.user)

    def post(self, request, *args, **kwargs):
        """
        Create multiple instances of one assignments in a given time period

        :param request:
        :return:
        """
        assignment_pk = kwargs.get('assignment_pk')
        try:
            from_date = datetime.datetime.strptime(kwargs.get('from'), '%Y-%m-%d').date()
            to_date = datetime.datetime.strptime(kwargs.get('to'), '%Y-%m-%d').date()

        except ValueError:
            # Wrong format of date: yyyy-mm-dd
            return HttpResponse(_('Wrong format of date: yyyy-mm-dd'), 400)

        if from_date > to_date:
            # From date should be smaller than to_date
            return HttpResponse(_('The beginning of the period is greater then the end of the period'), 400)
        try:
            a = Assignment.objects.get(id=assignment_pk)
        except ObjectDoesNotExist:
            return HttpResponse(_("The Assignment Specified doesn't exist"), 404)
        # Repeat the assignment every week:
        d = from_date
        assignments_list = []
        # There can't be conflicts among the newly created assignments and the teaching hours of the same teacher!
        # The same is not true for conflicts of the same class.
        conflicts = Assignment.objects.filter(school=a.school,
                                              teacher=a.teacher,
                                              school_year=a.school_year,
                                              hour_start=a.hour_start,
                                              hour_end=a.hour_end,
                                              date__week_day=((a.date.weekday() + 2) % 7),
                                              date__gte=from_date,
                                              date__lte=to_date). \
            exclude(id=a.id)
        if conflicts:
            # There are conflicts!
            return JsonResponse(
                AssignmentSerializer(conflicts, context={'request': request}, many=True).data,
                safe=False,
                status=400)

        while d <= to_date:
            if d != a.date and d.weekday() == a.date.weekday() and not \
                    Holiday.objects.filter(school=a.school,
                                           school_year=a.school_year,
                                           date_end__gte=d,
                                           date_start__lte=d).exists() and not \
                    Stage.objects.filter(school=a.school,
                                         school_year=a.school_year,
                                         date_start__lte=d,
                                         date_end__gte=d,
                                         course=a.course):
                # Found the correct day of the week when to duplicate the assignment
                new_a = Assignment(
                    teacher=a.teacher,
                    course=a.course,
                    subject=a.subject,
                    school_year=a.school_year,
                    school=a.school,
                    hour_start=a.hour_start,
                    hour_end=a.hour_end,
                    bes=a.bes,
                    substitution=a.substitution,
                    absent=a.absent,
                    date=d
                )
                assignments_list.append(new_a)
            d += datetime.timedelta(days=1)

        # Create with one single query.
        Assignment.objects.bulk_create(assignments_list)
        return HttpResponse(status=201)


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
