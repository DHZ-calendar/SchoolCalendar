from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User

from rest_framework.viewsets import ModelViewSet

from Timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday,\
                             Stage, Subject, HoursPerTeacherInClass, Assignment

from Timetable.forms import SchoolForm, TeacherForm, AdminSchoolForm, SchoolYearForm, CourseForm, HourSlotForm, \
                            AbsenceBlockForm, HolidayForm, StageForm, SubjectForm, HoursPerTeacherInClassForm,\
                            AssignmentForm

from Timetable.serializers import UserSerializer


class SchoolCreate(CreateView):
    model = School
    form_class = SchoolForm
    template_name = 'Timetable/school_form.html'
    success_url = reverse_lazy('school-add')


class TeacherCreate(CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'Timetable/teacher_form.html'
    success_url = reverse_lazy('teacher-add')


class AdminSchoolCreate(CreateView):
    model = AdminSchool
    form_class = AdminSchoolForm
    template_name = 'Timetable/adminschool_form.html'
    success_url = reverse_lazy('adminschool-add')


class SchoolYearCreate(CreateView):
    model = SchoolYear
    form_class = SchoolYearForm
    template_name = 'Timetable/school_year_form.html'
    success_url = reverse_lazy('school_year-add')


class CourseCreate(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'Timetable/course_form.html'
    success_url = reverse_lazy('course-add')


class HourSlotCreate(CreateView):
    model = HourSlot
    form_class = HourSlotForm
    template_name = 'Timetable/hourslot_form.html'
    success_url = reverse_lazy('hourslot-add')


class AbsenceBlockCreate(CreateView):
    model = AbsenceBlock
    form_class = AbsenceBlockForm
    template_name = 'Timetable/absenceBlock_form.html'
    success_url = reverse_lazy('absenceblock-add')


class HolidayCreate(CreateView):
    model = Holiday
    form_class = HolidayForm
    template_name = 'Timetable/holiday_form.html'
    success_url = reverse_lazy('holiday-add')


class StageCreate(CreateView):
    model = Stage
    form_class = StageForm
    template_name = 'Timetable/stage_form.html'
    success_url = reverse_lazy('stage-add')


class SubjectCreate(CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'Timetable/subject_form.html'
    success_url = reverse_lazy('subject-add')


class HoursPerTeacherInClassCreate(CreateView):
    model = HoursPerTeacherInClass
    form_class = HoursPerTeacherInClassForm
    template_name = 'Timetable/hoursPerTeacherInClass_form.html'
    success_url = reverse_lazy('hours_per_teacher_in_class-add')


class AssignmentCreate(CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'Timetable/assignment_form.html'
    success_url = reverse_lazy('assignment-add')


class TimetableView(TemplateView):
    template_name = 'Timetable/timetable.html'


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
