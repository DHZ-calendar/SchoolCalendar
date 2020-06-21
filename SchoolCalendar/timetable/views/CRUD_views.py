from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from timetable.forms import SchoolForm, TeacherForm, AdminSchoolForm, SchoolYearForm, CourseForm, HourSlotForm, \
    AbsenceBlockForm, HolidayForm, StageForm, SubjectForm, HoursPerTeacherInClassForm, \
    AssignmentForm
from timetable.mixins import AdminSchoolPermissionMixin, SuperUserPermissionMixin, TeacherPermissionMixin
from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday, \
    Stage, Subject, HoursPerTeacherInClass, Assignment


class CreateViewWithUser(CreateView):
    def get_form_kwargs(self):
        kwargs = super(CreateViewWithUser, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class UpdateViewWithUser(CreateView):
    def get_form_kwargs(self):
        kwargs = super(UpdateViewWithUser, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # To fix loading of model data
    def get_initial(self):
        instance = self.get_object()
        initial = {}
        print(vars(instance))
        obj_dict = vars(instance)
        for key in obj_dict.keys():
            if key[-3:] == '_id':
                initial[key[:-3]] = obj_dict[key]
            else:
                initial[key] = obj_dict[key]
        return initial


# School CRUD
class SchoolCreate(SuperUserPermissionMixin, CreateView):
    model = School
    form_class = SchoolForm
    template_name = 'timetable/school_form.html'
    success_url = reverse_lazy('school-add')


class SchoolList(SuperUserPermissionMixin, ListView):
    model = School
    template_name = 'timetable/school_list.html'


# Teacher CRUD
class TeacherCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Teacher
    form_class = TeacherForm
    template_name = 'timetable/teacher_form.html'
    success_url = reverse_lazy('teacher-list')


class TeacherUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Teacher
    form_class = TeacherForm
    template_name = 'timetable/teacher_form.html'
    success_url = reverse_lazy('teacher-list')


class TeacherDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('teacher-list')


class TeacherList(AdminSchoolPermissionMixin, ListView):
    model = Teacher
    template_name = 'timetable/teacher_list.html'


# AdminSchool CRUD
class AdminSchoolCreate(SuperUserPermissionMixin, CreateViewWithUser):
    model = AdminSchool
    form_class = AdminSchoolForm
    template_name = 'timetable/adminschool_form.html'
    success_url = reverse_lazy('adminschool-list')


class AdminSchoolUpdate(SuperUserPermissionMixin, UpdateViewWithUser):
    model = AdminSchool
    form_class = AdminSchoolForm
    template_name = 'timetable/adminschool_form.html'
    success_url = reverse_lazy('adminschool-list')


class AdminSchoolDelete(SuperUserPermissionMixin, DeleteView):
    model = AdminSchool
    form_class = AdminSchoolForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('adminschool-list')


class AdminSchoolList(SuperUserPermissionMixin, ListView):
    model = AdminSchool
    template_name = 'timetable/adminschool_list.html'


# SchoolYear CRUD
class SchoolYearCreate(SuperUserPermissionMixin, CreateView):
    model = SchoolYear
    form_class = SchoolYearForm
    template_name = 'timetable/school_year_form.html'
    success_url = reverse_lazy('school_year-list')


class SchoolYearUpdate(SuperUserPermissionMixin, UpdateView):
    model = SchoolYear
    form_class = SchoolYearForm
    template_name = 'timetable/school_year_form.html'
    success_url = reverse_lazy('school_year-list')


class SchoolYearDelete(SuperUserPermissionMixin, DeleteView):
    model = SchoolYear
    form_class = SchoolYearForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('school_year-list')


class SchoolYearList(SuperUserPermissionMixin, ListView):
    model = SchoolYear
    template_name = 'timetable/school_year_list.html'


# Course CRUD
class CourseCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Course
    form_class = CourseForm
    template_name = 'timetable/course_form.html'
    success_url = reverse_lazy('course-list')


class CourseUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Course
    form_class = CourseForm
    template_name = 'timetable/course_form.html'
    success_url = reverse_lazy('course-list')


class CourseDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Course
    form_class = CourseForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('course-list')


class CourseList(AdminSchoolPermissionMixin, ListView):
    model = Course
    template_name = 'timetable/course_list.html'


# CRUD HourSlot
class HourSlotCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = HourSlot
    form_class = HourSlotForm
    template_name = 'timetable/hourslot_form.html'
    success_url = reverse_lazy('hourslot-list')


class HourSlotUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = HourSlot
    form_class = HourSlotForm
    template_name = 'timetable/hourslot_form.html'
    success_url = reverse_lazy('hourslot-list')


class HourSlotDelete(AdminSchoolPermissionMixin, DeleteView):
    model = HourSlot
    form_class = HourSlotForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('hourslot-list')


class HourSlotList(AdminSchoolPermissionMixin, ListView):
    model = HourSlot
    template_name = 'timetable/hourslot_list.html'


# CRUD AbsenceBlock
class AbsenceBlockCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = AbsenceBlock
    form_class = AbsenceBlockForm
    template_name = 'timetable/absenceBlock_form.html'
    success_url = reverse_lazy('absenceblock-add')


class AbsenceBlockUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = AbsenceBlock
    form_class = AbsenceBlockForm
    template_name = 'timetable/absenceBlock_form.html'
    success_url = reverse_lazy('absenceblock-list')


class AbsenceBlockDelete(AdminSchoolPermissionMixin, DeleteView):
    model = AbsenceBlock
    form_class = AbsenceBlockForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('absenceblock-list')


class AbsenceBlockList(AdminSchoolPermissionMixin, ListView):
    model = AbsenceBlock
    template_name = 'timetable/absenceBlock_list.html'


# CRUD Holiday
class HolidayCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Holiday
    form_class = HolidayForm
    template_name = 'timetable/holiday_form.html'
    success_url = reverse_lazy('holiday-list')


class HolidayUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Holiday
    form_class = HolidayForm
    template_name = 'timetable/holiday_form.html'
    success_url = reverse_lazy('holiday-list')


class HolidayDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Holiday
    form_class = HolidayForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('holiday-list')


class HolidayList(AdminSchoolPermissionMixin, ListView):
    model = Holiday
    template_name = 'timetable/holiday_list.html'


# CRUD Stage
class StageCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Stage
    form_class = StageForm
    template_name = 'timetable/stage_form.html'
    success_url = reverse_lazy('stage-list')


class StageUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Stage
    form_class = StageForm
    template_name = 'timetable/stage_form.html'
    success_url = reverse_lazy('stage-list')


class StageDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Stage
    form_class = StageForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('stage-list')


class StageList(AdminSchoolPermissionMixin, ListView):
    model = Stage
    template_name = 'timetable/stage_list.html'


# CRUD Subject
class SubjectCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Subject
    form_class = SubjectForm
    template_name = 'timetable/subject_form.html'
    success_url = reverse_lazy('subject-list')


class SubjectUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Subject
    form_class = SubjectForm
    template_name = 'timetable/subject_form.html'
    success_url = reverse_lazy('subject-list')


class SubjectDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Subject
    form_class = SubjectForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('subject-list')


class SubjectList(AdminSchoolPermissionMixin, ListView):
    model = Subject
    template_name = 'timetable/subject_list.html'


# CRUD HoursPerTeacherInClass
class HoursPerTeacherInClassCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = HoursPerTeacherInClass
    form_class = HoursPerTeacherInClassForm
    template_name = 'timetable/hoursPerTeacherInClass_form.html'
    success_url = reverse_lazy('hours_per_teacher_in_class-list')


class HoursPerTeacherInClassUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = HoursPerTeacherInClass
    form_class = HoursPerTeacherInClassForm
    template_name = 'timetable/hoursPerTeacherInClass_form.html'
    success_url = reverse_lazy('hours_per_teacher_in_class-list')


class HoursPerTeacherInClassDelete(AdminSchoolPermissionMixin, DeleteView):
    model = HoursPerTeacherInClass
    form_class = HoursPerTeacherInClassForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('hours_per_teacher_in_class-list')


class HoursPerTeacherInClassList(AdminSchoolPermissionMixin, ListView):
    model = HoursPerTeacherInClass
    template_name = 'timetable/hours_per_teacher_in_class_list.html'


class AssignmentCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'timetable/assignment_form.html'
    success_url = reverse_lazy('assignment-add')
