from django.urls import path
from Timetable.views import SchoolCreate, TeacherCreate, AdminSchoolCreate, SchoolYearCreate, CourseCreate,\
                            HourSlotCreate, AbsenceBlockCreate, HolidayCreate, StageCreate, SubjectCreate, \
                            HoursPerTeacherInClassCreate, AssignmentCreate, TimetableView

urlpatterns = [
    path('', TimetableView.as_view(), name='timetable-view'),

    path('school/add/', SchoolCreate.as_view(), name='school-add'),
    path('teacher/add/', TeacherCreate.as_view(), name='teacher-add'),
    path('admin_school/add/', AdminSchoolCreate.as_view(), name='adminschool-add'),
    path('school_year/add/', SchoolYearCreate.as_view(), name='school_year-add'),
    path('course/add/', CourseCreate.as_view(), name='course-add'),
    path('hour_slot/add/', HourSlotCreate.as_view(), name='hourslot-add'),
    path('absence_block/add/', AbsenceBlockCreate.as_view(), name='absenceblock-add'),
    path('holiday/add/', HolidayCreate.as_view(), name='holiday-add'),
    path('stage/add/', StageCreate.as_view(), name='stage-add'),
    path('subject/add/', SubjectCreate.as_view(), name='subject-add'),
    path('hours_per_teacher_in_class/add/', HoursPerTeacherInClassCreate.as_view(),
         name='hours_per_teacher_in_class-add'),
    path('assignment/add/', AssignmentCreate.as_view(), name='assignment-add'),

    # path('author/<int:pk>/', AuthorUpdate.as_view(), name='author-update'),
    # path('author/<int:pk>/delete/', AuthorDelete.as_view(), name='author-delete'),
]