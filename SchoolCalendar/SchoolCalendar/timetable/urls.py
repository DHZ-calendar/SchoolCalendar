from django.urls import path, re_path, include
from timetable.views import SchoolCreate, TeacherCreate, AdminSchoolCreate, SchoolYearCreate, CourseCreate, \
    HourSlotCreate, AbsenceBlockCreate, HolidayCreate, StageCreate, SubjectCreate, \
    HoursPerTeacherInClassCreate, AssignmentCreate, TimetableView, TeacherViewSet, \
    CourseYearOnlyListViewSet, CourseSectionOnlyListViewSet, HolidayViewSet, StageViewSet, \
    HourSlotViewSet, HoursPerTeacherInClassViewSet, AssignmentViewSet, TeacherAssignmentsViewSet, \
    AbsenceBlocksPerTeacherViewSet, ReplicateAssignmentViewSet, CreateMultipleAssignmentsView, \
    TeacherSubstitutionViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'year_only_course', CourseYearOnlyListViewSet, basename='year_only_course')
router.register(r'section_only_course', CourseSectionOnlyListViewSet, basename='section_only_course')
router.register(r'holidays', HolidayViewSet, basename='holiday')
router.register(r'stages', StageViewSet, basename='stage')
router.register(r'hour_slots', HourSlotViewSet, basename='hour_slot')
router.register(r'hour_per_teacher_in_class/?(start_date=\d\d\d\d-\d\d-\d\d)?(end_date=\d\d\d\d-\d\d-\d\d)?', HoursPerTeacherInClassViewSet, basename='hour_per_teacher_in_class')
router.register(r'assignments', AssignmentViewSet, basename='assignments')
router.register(r'teacher_assignments/(?P<teacher_pk>[0-9]+)/(?P<school_year_pk>[0-9]+)', TeacherAssignmentsViewSet,
                basename='teacher_assignments')
router.register(r'teacher_absence_block/(?P<teacher_pk>[0-9]+)/(?P<school_year_pk>[0-9]+)',
                AbsenceBlocksPerTeacherViewSet, basename='teacher_absence_blocks')
router.register(
    r'replicated_assignment/(?P<assignment_pk>[0-9]+)/(?P<from>\d\d\d\d-\d\d-\d\d)/(?P<to>\d\d\d\d-\d\d-\d\d)',
    ReplicateAssignmentViewSet, basename='replicate_assignment')
router.register(r'teacher_can_substitute/(?P<assignment_pk>\d+)', TeacherSubstitutionViewSet,
                basename='teacher_substitution')
# router.register(r'absence_blocks', AbsenceBlockViewSet)


urlpatterns = [
    path('', TimetableView.as_view(), name='timetable-view'),
    re_path(r'^api-auth/', include('rest_framework.urls')),    # Django Rest Framework
    re_path(r'^api/', include(router.urls)),
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
    re_path(r'multiple_assignments/add/(?P<assignment_pk>[0-9]+)/(?P<from>\d\d\d\d-\d\d-\d\d)/(?P<to>\d\d\d\d-\d\d-\d\d)'
            , CreateMultipleAssignmentsView.as_view(), name='multiple_assignment-add')
    # path('author/<int:pk>/', AuthorUpdate.as_view(), name='author-update'),
    # path('author/<int:pk>/delete/', AuthorDelete.as_view(), name='author-delete'),
]