from django.contrib.auth.mixins import UserPassesTestMixin

from timetable.models import Teacher
from timetable import utils


class TeacherPermissionMixin(UserPassesTestMixin):
    """
    Only the logged teacher user can pass the test.
    """
    def test_func(self):
        return self.request.user and Teacher.objects.filter(id=self.request.user.id).exists()


class AdminSchoolPermissionMixin(UserPassesTestMixin):
    """
    Only the logged admin user can pass the test.
    """
    def test_func(self):
        return self.request.user and utils.is_adminschool(self.request.user)


class SuperUserPermissionMixin(UserPassesTestMixin):
    """
    Only logged super user can pass the test
    """
    def test_func(self):
        return self.request.user and self.request.user.is_superuser