from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from Timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday,\
                             Stage, Subject, HoursPerTeacherInClass, Assignment

from Timetable.forms import SchoolForm, TeacherForm, AdminSchoolForm, SchoolYearForm, CourseForm

# Create your views here.


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
