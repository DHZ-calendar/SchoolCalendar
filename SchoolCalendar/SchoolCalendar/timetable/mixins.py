from django.contrib.auth.mixins import UserPassesTestMixin

from timetable import utils


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