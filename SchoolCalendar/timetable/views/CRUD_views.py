from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from timetable.forms import SchoolForm, TeacherForm, AdminSchoolForm, SchoolYearForm, CourseForm, HourSlotForm, \
    AbsenceBlockForm, HolidayForm, StageForm, SubjectForm, HoursPerTeacherInClassForm, \
    AssignmentForm, TeacherCreationForm, AdminSchoolCreationForm, RoomForm, HourSlotCreateForm, TeachersYearlyLoadForm
from timetable.mixins import AdminSchoolPermissionMixin, SuperUserPermissionMixin, TeacherPermissionMixin
from timetable.models import School, MyUser, Teacher, AdminSchool, SchoolYear, Course, HourSlot, AbsenceBlock, Holiday, \
    Stage, Subject, HoursPerTeacherInClass, Assignment, Room, TeachersYearlyLoad


class CreateViewWithUser(CreateView):
    def get_form_kwargs(self):
        kwargs = super(CreateViewWithUser, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class UpdateViewWithUser(UpdateView):
    def get_form_kwargs(self):
        kwargs = super(UpdateViewWithUser, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TemplateViewWithSchoolYears(TemplateView):
    def get_context_data(selfListView, **kwargs):
        context = super().get_context_data(**kwargs)

        context['school_years'] = SchoolYear.objects.all().order_by('-year_start')
        return context


# School CRUD
class SchoolCreate(SuperUserPermissionMixin, CreateView):
    model = School
    form_class = SchoolForm
    template_name = 'timetable/school_form.html'
    success_url = reverse_lazy('school-add')


class SchoolUpdate(SuperUserPermissionMixin, UpdateView):
    model = School
    form_class = SchoolForm
    template_name = 'timetable/school_form.html'
    success_url = reverse_lazy('school-listview')


class SchoolDelete(SuperUserPermissionMixin, DeleteView):
    model = School
    form_class = SchoolForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('school-listview')


class SchoolList(SuperUserPermissionMixin, ListView):
    template_name = 'timetable/school_list.html'
    model = School


# Teacher CRUD
class TeacherCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Teacher
    form_class = TeacherCreationForm
    template_name = 'timetable/teacher_form.html'
    success_url = reverse_lazy('teacher-listview')


class TeacherUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Teacher
    form_class = TeacherForm
    template_name = 'timetable/teacher_form.html'
    success_url = reverse_lazy('teacher-listview')


class TeacherDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('teacher-listview')


class TeacherList(AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/teacher_list.html'


# AdminSchool CRUD
class AdminSchoolCreate(SuperUserPermissionMixin, CreateViewWithUser):
    model = AdminSchool
    form_class = AdminSchoolCreationForm
    template_name = 'timetable/adminschool_form.html'
    success_url = reverse_lazy('adminschool-listview')


class AdminSchoolUpdate(SuperUserPermissionMixin, UpdateViewWithUser):
    model = AdminSchool
    form_class = AdminSchoolForm
    template_name = 'timetable/adminschool_form.html'
    success_url = reverse_lazy('adminschool-listview')


class AdminSchoolDelete(SuperUserPermissionMixin, DeleteView):
    model = AdminSchool
    form_class = AdminSchoolForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('adminschool-listview')


class AdminSchoolList(SuperUserPermissionMixin, ListView):
    model = AdminSchool
    template_name = 'timetable/adminschool_list.html'


# SchoolYear CRUD
class SchoolYearCreate(SuperUserPermissionMixin, CreateView):
    model = SchoolYear
    form_class = SchoolYearForm
    template_name = 'timetable/school_year_form.html'
    success_url = reverse_lazy('school_year-listview')


class SchoolYearUpdate(SuperUserPermissionMixin, UpdateView):
    model = SchoolYear
    form_class = SchoolYearForm
    template_name = 'timetable/school_year_form.html'
    success_url = reverse_lazy('school_year-listview')


class SchoolYearDelete(SuperUserPermissionMixin, DeleteView):
    model = SchoolYear
    form_class = SchoolYearForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('school_year-listview')


class SchoolYearList(SuperUserPermissionMixin, ListView):
    model = SchoolYear
    template_name = 'timetable/school_year_list.html'


# CRUD Room
class RoomCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Room
    form_class = RoomForm
    template_name = 'timetable/room_form.html'
    success_url = reverse_lazy('room-listview')


class RoomUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Room
    form_class = RoomForm
    template_name = 'timetable/room_form.html'
    success_url = reverse_lazy('room-listview')


class RoomDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Room
    form_class = RoomForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('room-listview')


class RoomList(AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/room_list.html'


# Course CRUD
class CourseCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Course
    form_class = CourseForm
    template_name = 'timetable/course_form.html'
    success_url = reverse_lazy('course-listview')


class CourseUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Course
    form_class = CourseForm
    template_name = 'timetable/course_form.html'
    success_url = reverse_lazy('course-listview')


class CourseDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Course
    form_class = CourseForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('course-listview')


class CourseList(AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/course_list.html'


# TeachersYearlyLoad CRUD
class TeachersYearlyLoadCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = TeachersYearlyLoad
    form_class = TeachersYearlyLoadForm
    template_name = 'timetable/teachersyearlyload_form.html'
    success_url = reverse_lazy('teachers_yearly_load-add')


class TeachersYearlyLoadUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = TeachersYearlyLoad
    form_class = TeachersYearlyLoadForm
    template_name = 'timetable/teachersyearlyload_form.html'
    success_url = reverse_lazy('teachers_yearly_load-listview')


class TeachersYearlyLoadDelete(AdminSchoolPermissionMixin, DeleteView):
    model = TeachersYearlyLoad
    form_class = TeachersYearlyLoadForm
    template_name = 'timetable/teachersyearlyload_form.html'
    success_url = reverse_lazy('teachers_yearly_load-listview')


class TeachersYearlyLoadList(AdminSchoolPermissionMixin, ListView):
    template_name = 'timetable/teachersyearlyload.html'
    model = TeachersYearlyLoad


# CRUD HourSlot
class HourSlotCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = HourSlot
    form_class = HourSlotCreateForm
    template_name = 'timetable/hourslot_form.html'
    success_url = reverse_lazy('hourslot-listview')


class HourSlotUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = HourSlot
    form_class = HourSlotForm
    template_name = 'timetable/hourslot_form.html'
    success_url = reverse_lazy('hourslot-listview')


class HourSlotDelete(AdminSchoolPermissionMixin, DeleteView):
    model = HourSlot
    form_class = HourSlotForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('hourslot-listview')


class HourSlotList(AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/hourslot_list.html'


# CRUD AbsenceBlock
class AbsenceBlockCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = AbsenceBlock
    form_class = AbsenceBlockForm
    template_name = 'timetable/absenceBlock_form.html'
    success_url = reverse_lazy('absenceblock-listview')


class AbsenceBlockUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = AbsenceBlock
    form_class = AbsenceBlockForm
    template_name = 'timetable/absenceBlock_form.html'
    success_url = reverse_lazy('absenceblock-listview')


class AbsenceBlockDelete(AdminSchoolPermissionMixin, DeleteView):
    model = AbsenceBlock
    form_class = AbsenceBlockForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('absenceblock-listview')


class AbsenceBlockList(AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/absenceBlock_list.html'


# CRUD Holiday
class HolidayCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Holiday
    form_class = HolidayForm
    template_name = 'timetable/holiday_form.html'
    success_url = reverse_lazy('holiday-listview')


class HolidayUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Holiday
    form_class = HolidayForm
    template_name = 'timetable/holiday_form.html'
    success_url = reverse_lazy('holiday-listview')


class HolidayDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Holiday
    form_class = HolidayForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('holiday-listview')


class HolidayList(AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/holiday_list.html'


# CRUD Stage
class StageCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Stage
    form_class = StageForm
    template_name = 'timetable/stage_form.html'
    success_url = reverse_lazy('stage-listview')


class StageUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Stage
    form_class = StageForm
    template_name = 'timetable/stage_form.html'
    success_url = reverse_lazy('stage-listview')


class StageDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Stage
    form_class = StageForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('stage-listview')


class StageList(AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/stage_list.html'


# CRUD Subject
class SubjectCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Subject
    form_class = SubjectForm
    template_name = 'timetable/subject_form.html'
    success_url = reverse_lazy('subject-listview')


class SubjectUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = Subject
    form_class = SubjectForm
    template_name = 'timetable/subject_form.html'
    success_url = reverse_lazy('subject-listview')


class SubjectDelete(AdminSchoolPermissionMixin, DeleteView):
    model = Subject
    form_class = SubjectForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('subject-listview')


class SubjectList(AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/subject_list.html'


# CRUD HoursPerTeacherInClass
class HoursPerTeacherInClassCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = HoursPerTeacherInClass
    form_class = HoursPerTeacherInClassForm
    template_name = 'timetable/hoursPerTeacherInClass_form.html'
    success_url = reverse_lazy('hours_per_teacher_in_class-listview')


class HoursPerTeacherInClassUpdate(AdminSchoolPermissionMixin, UpdateViewWithUser):
    model = HoursPerTeacherInClass
    form_class = HoursPerTeacherInClassForm
    template_name = 'timetable/hoursPerTeacherInClass_form.html'
    success_url = reverse_lazy('hours_per_teacher_in_class-listview')


class HoursPerTeacherInClassDelete(AdminSchoolPermissionMixin, DeleteView):
    model = HoursPerTeacherInClass
    form_class = HoursPerTeacherInClassForm
    template_name = 'timetable/delete_form.html'
    success_url = reverse_lazy('hours_per_teacher_in_class-listview')


class HoursPerTeacherInClassList(AdminSchoolPermissionMixin, TemplateViewWithSchoolYears):
    template_name = 'timetable/hours_per_teacher_in_class_list.html'


class AssignmentCreate(AdminSchoolPermissionMixin, CreateViewWithUser):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'timetable/assignment_form.html'
    success_url = reverse_lazy('assignment-add')
