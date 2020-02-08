from django.urls import path
from Timetable.views import SchoolCreate, TeacherCreate, AdminSchoolCreate, SchoolYearCreate, CourseCreate

urlpatterns = [
    path('school/add/', SchoolCreate.as_view(), name='school-add'),
    path('teacher/add/', TeacherCreate.as_view(), name='teacher-add'),
    path('admin_school/add/', AdminSchoolCreate.as_view(), name='adminschool-add'),
    path('school_year/add/', SchoolYearCreate.as_view(), name='school_year-add'),
    path('course/add/', CourseCreate.as_view(), name='course-add'),
    # path('author/<int:pk>/', AuthorUpdate.as_view(), name='author-update'),
    # path('author/<int:pk>/delete/', AuthorDelete.as_view(), name='author-delete'),
]