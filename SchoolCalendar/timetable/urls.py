from django.conf.urls import url
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from timetable.views.CRUD_views import SchoolCreate, TeacherCreate, AdminSchoolCreate, SchoolYearCreate, CourseCreate, \
    HourSlotCreate, AbsenceBlockCreate, HolidayCreate, StageCreate, SubjectCreate, \
    HoursPerTeacherInClassCreate, AssignmentCreate, \
    SchoolList, TeacherList, AdminSchoolList, SchoolYearList, CourseList, HourSlotList, AbsenceBlockList, \
    HolidayList, StageList, SubjectList, HoursPerTeacherInClassList, \
    SchoolUpdate, TeacherUpdate, AdminSchoolUpdate, SchoolYearUpdate, CourseUpdate, HourSlotUpdate, AbsenceBlockUpdate, \
    HolidayUpdate, StageUpdate, SubjectUpdate, HoursPerTeacherInClassUpdate, \
    SchoolDelete, TeacherDelete, AdminSchoolDelete, SchoolYearDelete, CourseDelete, HourSlotDelete, AbsenceBlockDelete, \
    HolidayDelete, StageDelete, SubjectDelete, HoursPerTeacherInClassDelete, RoomCreate, RoomUpdate, RoomDelete, \
    RoomList, TeachersYearlyLoadCreate, TeachersYearlyLoadUpdate, TeachersYearlyLoadDelete, TeachersYearlyLoadList, \
    CoursesYearlyLoadCreate, CoursesYearlyLoadUpdate, CoursesYearlyLoadDelete, CoursesYearlyLoadList, \
    HourSlotsGroupCreate, HourSlotsGroupUpdate, HourSlotsGroupDelete, HourSlotsGroupList, \
    SecretaryCreate, SecretaryUpdate, SecretaryDelete, SecretaryList
from timetable.views.rest_framework_views import TeacherViewSet, \
    CourseYearOnlyListViewSet, CourseSectionOnlyListViewSet, HolidayViewSet, StageViewSet, \
    HourSlotViewSet, HoursPerTeacherInClassViewSet, AssignmentViewSet, TeacherAssignmentsViewSet, \
    AbsenceBlocksPerTeacherViewSet, TeacherTimetableViewSet, AbsenceBlockViewSet, \
    SubjectViewSet, RoomViewSet, TeacherSummaryViewSet, CourseSummaryViewSet, TeachersYearlyLoadViewSet, \
    CoursesYearlyLoadViewSet, RoomTimetableViewSet, HourSlotsGroupViewSet, SubstitutionAssignmentsViewSet
from timetable.views.other_views import TimetableView, SubstituteTeacherView, TeacherTimetableView, \
    LoggedUserRedirectView, TeacherSummaryView, SendInvitationTeacherEmailView, \
    SendInvitationAdminSchoolEmailView, CheckWeekReplicationView, ReplicateWeekAssignmentsView, \
    TeacherSubstitutionView, SubstituteTeacherApiView, TimetableReportView, \
    CourseSummaryView, RoomTimetableView, SubstitutionSummaryView, \
    SendTeacherSubstitutionEmailView, DownloadTeacherSubstitutionTicketView, SecretaryTimetableView
from timetable.views.csv_views import TimetableTeacherCSVReportViewSet, TimetableCourseCSVReportViewSet, \
                                      TimetableRoomCSVReportViewSet, TimetableGeneralCSVReportViewSet, \
                                      SubstitutionsCSVReportViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'year_only_course', CourseYearOnlyListViewSet, basename='year_only_course')
router.register(r'section_only_course', CourseSectionOnlyListViewSet, basename='section_only_course')
router.register(r'holidays', HolidayViewSet, basename='holiday')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'stages', StageViewSet, basename='stage')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'hour_slots', HourSlotViewSet, basename='hour_slot')
router.register(r'hour_slots_groups', HourSlotsGroupViewSet, basename='hour_slots_group')
router.register(r'hour_per_teacher_in_class/?(start_date=\d\d\d\d-\d\d-\d\d)?(end_date=\d\d\d\d-\d\d-\d\d)?',
                HoursPerTeacherInClassViewSet, basename='hour_per_teacher_in_class')
router.register(r'assignments', AssignmentViewSet, basename='assignments')
router.register(r'substitutions', SubstitutionAssignmentsViewSet, basename='substitutions')
router.register(r'teacher_assignments/(?P<teacher_pk>[0-9]+)/(?P<school_year_pk>[0-9]+)', TeacherAssignmentsViewSet,
                basename='teacher_assignments')
router.register(r'teacher_absence_block/(?P<teacher_pk>[0-9]+)/(?P<school_year_pk>[0-9]+)',
                AbsenceBlocksPerTeacherViewSet, basename='teacher_absence_blocks')
router.register(r'teacher_timetable', TeacherTimetableViewSet, basename='teacher_timetable')
router.register(r'room_timetable/(?P<room_pk>[0-9]+)', RoomTimetableViewSet, basename='room_timetable')
router.register(r'absence_blocks', AbsenceBlockViewSet, basename='absence_block')
router.register(r'teachers_summary/?(school_year=[0-9]+)?(start_date=\d\d\d\d-\d\d-\d\d)?(end_date=\d\d\d\d-\d\d-\d\d)?',
                TeacherSummaryViewSet, basename='teacher_summary')
router.register(r'courses_summary/?(school_year=[0-9]+)?(start_date=\d\d\d\d-\d\d-\d\d)?(end_date=\d\d\d\d-\d\d-\d\d)?',
                CourseSummaryViewSet, basename='course_summary')
router.register(r'teachers_yearly_loads', TeachersYearlyLoadViewSet, basename='teachers_yearly_load')
router.register(r'courses_yearly_loads', CoursesYearlyLoadViewSet, basename='courses_yearly_load')


urlpatterns = [
    # Excel reports
    url(r'timetable_room_csv_report_view/(?P<school_year_pk>[0-9]+)/(?P<room_pk>\d+)/'
        r'(?P<monday_date>\d\d\d\d-\d\d-\d\d)', TimetableRoomCSVReportViewSet.as_view(),
        name='timetable_room_csv_report'),
    url(r'timetable_course_csv_report_view/(?P<school_year_pk>[0-9]+)/(?P<course_pk>\d+)/'
        r'(?P<monday_date>\d\d\d\d-\d\d-\d\d)', TimetableCourseCSVReportViewSet.as_view(),
        name='timetable_course_csv_report'),
    url(r'timetable_teacher_csv_report_view/(?P<school_year_pk>[0-9]+)/(?P<teacher_pk>\d+)/'
        r'(?P<monday_date>\d\d\d\d-\d\d-\d\d)', TimetableTeacherCSVReportViewSet.as_view(),
        name='timetable_teacher_csv_report'),
    url(r'timetable_general_csv_report_view/(?P<school_year_pk>[0-9]+)'
        r'(?P<monday_date>\d\d\d\d-\d\d-\d\d)', TimetableGeneralCSVReportViewSet.as_view(),
        name='timetable_general_csv_report'),
    url(r'substitutions_csv_report_view/(?P<school_year_pk>[0-9]+)', SubstitutionsCSVReportViewSet.as_view(),
        name='substitutions_csv_report'),

    path('', LoggedUserRedirectView.as_view(), name='user_redirect-view'),
    path('user_guide', TemplateView.as_view(template_name='timetable/user_guide.html'), name='user_guide'),
    path('admin_school', TimetableView.as_view(), name='timetable-view'),
    path('substitute_teacher', SubstituteTeacherView.as_view(), name='substitute_teacher-view'),
    path('teacher_view', TeacherTimetableView.as_view(), name='teacher_timetable-view'),
    path('secretary_view', SecretaryTimetableView.as_view(), name='secretary_timetable-view'),
    path('room_view', RoomTimetableView.as_view(), name='room_timetable-view'),
    path('teacher_summary_view', TeacherSummaryView.as_view(), name='teacher_summary-view'),
    path('course_summary_view', CourseSummaryView.as_view(), name='course_summary-view'),
    path('substitution_summary_view', SubstitutionSummaryView.as_view(), name='substitution_summary-view'),
    path('timetable_report_view', TimetableReportView.as_view(), name='timetable_report-view'),
    path('substitution_pdf_ticket/<assign_pk>', DownloadTeacherSubstitutionTicketView.as_view(),
         name='substitution_pdf_ticket-view'),
    path('substitution_teacher_email/<assign_pk>', SendTeacherSubstitutionEmailView.as_view(),
         name='substitution_teacher_email-view'),
    path('invite_teacher/<user_pk>', SendInvitationTeacherEmailView.as_view(), name='teacher_invitation-view'),
    path('invite_adminschool/<user_pk>', SendInvitationAdminSchoolEmailView.as_view(),
         name='adminschool_invitation-view'),
    re_path(r'^api-auth/', include('rest_framework.urls')),  # Django Rest Framework
    re_path(r'^api/', include(router.urls)),
    path('school/add/', SchoolCreate.as_view(), name='school-add'),
    path('school/<pk>/edit/', SchoolUpdate.as_view(), name='school-edit'),
    path('school/<pk>/delete/', SchoolDelete.as_view(), name='school-delete'),
    path('school/', SchoolList.as_view(), name='school-listview'),
    path('room/add/', RoomCreate.as_view(), name='room-add'),
    path('room/<pk>/edit/', RoomUpdate.as_view(), name='room-edit'),
    path('room/<pk>/delete/', RoomDelete.as_view(), name='room-delete'),
    path('room/', RoomList.as_view(), name='room-listview'),
    path('teacher/add/', TeacherCreate.as_view(), name='teacher-add'),
    path('teacher/<pk>/edit/', TeacherUpdate.as_view(), name='teacher-edit'),
    path('teacher/<pk>/delete/', TeacherDelete.as_view(), name='teacher-delete'),
    path('teacher/', TeacherList.as_view(), name='teacher-listview'),
    path('admin_school/add/', AdminSchoolCreate.as_view(), name='adminschool-add'),
    path('admin_school/<pk>/edit/', AdminSchoolUpdate.as_view(), name='adminschool-edit'),
    path('admin_school/<pk>/delete/', AdminSchoolDelete.as_view(), name='adminschool-delete'),
    path('admin_school/', AdminSchoolList.as_view(), name='adminschool-listview'),
    path('secretary/add/', SecretaryCreate.as_view(), name='secretary-add'),
    path('secretary/<pk>/edit/', SecretaryUpdate.as_view(), name='secretary-edit'),
    path('secretary/<pk>/delete/', SecretaryDelete.as_view(), name='secretary-delete'),
    path('secretary/', SecretaryList.as_view(), name='secretary-listview'),
    path('school_year/add/', SchoolYearCreate.as_view(), name='school_year-add'),
    path('school_year/<pk>/edit/', SchoolYearUpdate.as_view(), name='school_year-edit'),
    path('school_year/<pk>/delete/', SchoolYearDelete.as_view(), name='school_year-delete'),
    path('school_year/', SchoolYearList.as_view(), name='school_year-listview'),
    path('course/add/', CourseCreate.as_view(), name='course-add'),
    path('course/<pk>/edit/', CourseUpdate.as_view(), name='course-edit'),
    path('course/<pk>/delete/', CourseDelete.as_view(), name='course-delete'),
    path('course/', CourseList.as_view(), name='course-listview'),
    path('hour_slots_group/add/', HourSlotsGroupCreate.as_view(), name='hourslotsgroup-add'),
    path('hour_slots_group/<pk>/edit/', HourSlotsGroupUpdate.as_view(), name='hourslotsgroup-edit'),
    path('hour_slots_group/<pk>/delete/', HourSlotsGroupDelete.as_view(), name='hourslotsgroup-delete'),
    path('hour_slots_group/', HourSlotsGroupList.as_view(), name='hourslotsgroup-listview'),
    path('hour_slot/add/', HourSlotCreate.as_view(), name='hourslot-add'),
    path('hour_slot/<pk>/edit/', HourSlotUpdate.as_view(), name='hourslot-edit'),
    path('hour_slot/<pk>/delete/', HourSlotDelete.as_view(), name='hourslot-delete'),
    path('hour_slot/', HourSlotList.as_view(), name='hourslot-listview'),
    path('absence_block/add/', AbsenceBlockCreate.as_view(), name='absenceblock-add'),
    path('absence_block/<pk>/edit/', AbsenceBlockUpdate.as_view(), name='absenceblock-edit'),
    path('absence_block/<pk>/delete/', AbsenceBlockDelete.as_view(), name='absenceblock-delete'),
    path('absence_block/', AbsenceBlockList.as_view(), name='absenceblock-listview'),
    path('holiday/add/', HolidayCreate.as_view(), name='holiday-add'),
    path('holiday/<pk>/edit/', HolidayUpdate.as_view(), name='holiday-edit'),
    path('holiday/<pk>/delete/', HolidayDelete.as_view(), name='holiday-delete'),
    path('holiday/', HolidayList.as_view(), name='holiday-listview'),
    path('stage/add/', StageCreate.as_view(), name='stage-add'),
    path('stage/<pk>/edit/', StageUpdate.as_view(), name='stage-edit'),
    path('stage/<pk>/delete/', StageDelete.as_view(), name='stage-delete'),
    path('stage/', StageList.as_view(), name='stage-listview'),
    path('subject/add/', SubjectCreate.as_view(), name='subject-add'),
    path('subject/<pk>/edit/', SubjectUpdate.as_view(), name='subject-edit'),
    path('subject/<pk>/delete/', SubjectDelete.as_view(), name='subject-delete'),
    path('subject/', SubjectList.as_view(), name='subject-listview'),
    path('teachers_yearly_load/add/', TeachersYearlyLoadCreate.as_view(), name='teachers_yearly_load-add'),
    path('teachers_yearly_load/<pk>/edit/', TeachersYearlyLoadUpdate.as_view(), name='teachers_yearly_load-edit'),
    path('teachers_yearly_load/<pk>/delete/', TeachersYearlyLoadDelete.as_view(), name='teachers_yearly_load-delete'),
    path('teachers_yearly_load/', TeachersYearlyLoadList.as_view(), name='teachers_yearly_load-listview'),
    path('courses_yearly_load/add/', CoursesYearlyLoadCreate.as_view(), name='courses_yearly_load-add'),
    path('courses_yearly_load/<pk>/edit/', CoursesYearlyLoadUpdate.as_view(), name='courses_yearly_load-edit'),
    path('courses_yearly_load/<pk>/delete/', CoursesYearlyLoadDelete.as_view(), name='courses_yearly_load-delete'),
    path('courses_yearly_load/', CoursesYearlyLoadList.as_view(), name='courses_yearly_load-listview'),
    path('hours_per_teacher_in_class/add/', HoursPerTeacherInClassCreate.as_view(),
         name='hours_per_teacher_in_class-add'),
    path('hours_per_teacher_in_class/<pk>/edit/', HoursPerTeacherInClassUpdate.as_view(),
         name='hours_per_teacher_in_class-edit'),
    path('hours_per_teacher_in_class/<pk>/delete/', HoursPerTeacherInClassDelete.as_view(),
         name='hours_per_teacher_in_class-delete'),
    path('hours_per_teacher_in_class/', HoursPerTeacherInClassList.as_view(),
         name='hours_per_teacher_in_class-listview'),
    path('assignment/add/', AssignmentCreate.as_view(), name='assignment-add'),
    re_path(r'replicate_week/add/(?P<school_year_pk>[0-9]+)/(?P<course_pk>[0-9]+)/(?P<from>\d\d\d\d-\d\d-\d\d)/'
            r'(?P<to>\d\d\d\d-\d\d-\d\d)',
            ReplicateWeekAssignmentsView.as_view(), name='replicate_week-view'),
    re_path(r'check_week_replication/(?P<from>\d\d\d\d-\d\d-\d\d)/(?P<to>\d\d\d\d-\d\d-\d\d)',
            CheckWeekReplicationView.as_view(), name='check_week_replication-view'),
    re_path(r'teacher_can_substitute/(?P<assignment_pk>\d+)', TeacherSubstitutionView.as_view(),
            name='teacher_substitution-view'),
    re_path(r'substitute_teacher_api/(?P<assignment_pk>\d+)/(?P<teacher_pk>\d+)', SubstituteTeacherApiView.as_view(),
            name='substitute_teacher_api-view')
]
