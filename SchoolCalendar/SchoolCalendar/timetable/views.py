from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User

from rest_framework.viewsets import ModelViewSet, ViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday,\
                             Stage, Subject, HoursPerTeacherInClass, Assignment

from timetable.forms import SchoolForm, TeacherForm, AdminSchoolForm, SchoolYearForm, CourseForm, HourSlotForm, \
                            AbsenceBlockForm, HolidayForm, StageForm, SubjectForm, HoursPerTeacherInClassForm,\
                            AssignmentForm

from timetable.serializers import TeacherSerializer, CourseYearOnlySerializer, CourseSectionOnlySerializer

from timetable.filters import TeacherFromSameSchoolFilterBackend, HolidayPeriodFilter, QuerysetFromSameSchool, \
    StagePeriodFilter, HourSlotFilter, HoursPerTeacherInClassFilter, CourseSectionOnlyFilter, CourseYearOnlyFilter
from timetable import utils
from timetable.serializers import HolidaySerializer, StageSerializer, HourSlotSerializer, \
    HoursPerTeacherInClassSerializer


class CreateViewWithUser(CreateView):
    def get_form_kwargs(self):
        kwargs = super(CreateViewWithUser, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SchoolCreate(CreateView):
    model = School
    form_class = SchoolForm
    template_name = 'timetable/school_form.html'
    success_url = reverse_lazy('school-add')


class TeacherCreate(CreateViewWithUser):
    model = Teacher
    form_class = TeacherForm
    template_name = 'timetable/teacher_form.html'
    success_url = reverse_lazy('teacher-add')


class AdminSchoolCreate(CreateView):
    model = AdminSchool
    form_class = AdminSchoolForm
    template_name = 'timetable/adminschool_form.html'
    success_url = reverse_lazy('adminschool-add')


class SchoolYearCreate(CreateView):
    model = SchoolYear
    form_class = SchoolYearForm
    template_name = 'timetable/school_year_form.html'
    success_url = reverse_lazy('school_year-add')


class CourseCreate(CreateViewWithUser):
    model = Course
    form_class = CourseForm
    template_name = 'timetable/course_form.html'
    success_url = reverse_lazy('course-add')


class HourSlotCreate(CreateViewWithUser):
    model = HourSlot
    form_class = HourSlotForm
    template_name = 'timetable/hourslot_form.html'
    success_url = reverse_lazy('hourslot-add')


class AbsenceBlockCreate(CreateViewWithUser):
    model = AbsenceBlock
    form_class = AbsenceBlockForm
    template_name = 'timetable/absenceBlock_form.html'
    success_url = reverse_lazy('absenceblock-add')


class HolidayCreate(CreateViewWithUser):
    model = Holiday
    form_class = HolidayForm
    template_name = 'timetable/holiday_form.html'
    success_url = reverse_lazy('holiday-add')


class StageCreate(CreateViewWithUser):
    model = Stage
    form_class = StageForm
    template_name = 'timetable/stage_form.html'
    success_url = reverse_lazy('stage-add')


class SubjectCreate(CreateViewWithUser):
    model = Subject
    form_class = SubjectForm
    template_name = 'timetable/subject_form.html'
    success_url = reverse_lazy('subject-add')


class HoursPerTeacherInClassCreate(CreateViewWithUser):
    model = HoursPerTeacherInClass
    form_class = HoursPerTeacherInClassForm
    template_name = 'timetable/hoursPerTeacherInClass_form.html'
    success_url = reverse_lazy('hours_per_teacher_in_class-add')


class AssignmentCreate(CreateViewWithUser):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'timetable/assignment_form.html'
    success_url = reverse_lazy('assignment-add')


class TimetableView(TemplateView):
    template_name = 'timetable/timetable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['school_years'] = SchoolYear.objects.all()
        return context


class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [TeacherFromSameSchoolFilterBackend]


class CourseYearOnlyListViewSet(ListModelMixin, GenericViewSet):

    serializer_class = CourseYearOnlySerializer
    queryset = Course.objects.all()   # I think it gets overridden by get_queryset
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


class CourseSectionOnlyListViewSet(ListModelMixin, GenericViewSet):

    serializer_class = CourseSectionOnlySerializer
    queryset = Course.objects.all()   # I think it gets overridden by get_queryset
    permission_classes = [IsAuthenticated]
    filterset_class = CourseSectionOnlyFilter
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)

    def get_queryset(self):
        """
        :return: only the years of courses of the user logged's school
        """
        school = utils.get_school_from_user(self.request.user)
        if school:
            return Course.objects.filter(school=school).values('section').distinct()


class HolidayViewSet(ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)
    filterset_class = HolidayPeriodFilter


class StageViewSet(ModelViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool)
    filterset_class = StagePeriodFilter


class HourSlotViewSet(ModelViewSet):
    queryset = HourSlot.objects.all()
    serializer_class = HourSlotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool,)
    filterset_class = HourSlotFilter


class HoursPerTeacherInClassViewSet(ModelViewSet):
    queryset = HoursPerTeacherInClass.objects.all()
    serializer_class = HoursPerTeacherInClassSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, QuerysetFromSameSchool,)
    filterset_class = HoursPerTeacherInClassFilter
