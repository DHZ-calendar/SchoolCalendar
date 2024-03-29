from django.contrib.auth.mixins import UserPassesTestMixin

from timetable import utils


class SecretaryPermissionMixin(UserPassesTestMixin):
    """
    Only the logged secretary user can pass the test.
    """
    def test_func(self):
        return self.request.user and utils.is_secretary(self.request.user)


class TeacherPermissionMixin(UserPassesTestMixin):
    """
    Only the logged teacher user can pass the test.
    """
    def test_func(self):
        return self.request.user and utils.is_teacher(self.request.user)


class AdminSchoolPermissionMixin(UserPassesTestMixin):
    """
    Only the logged admin school user can pass the test.
    """
    def test_func(self):
        return self.request.user and utils.is_adminschool(self.request.user)


class AdminSchoolOrSecretaryPermissionMixin(UserPassesTestMixin):
    """
    Only the logged admin school or secretary user can pass the test.
    """
    def test_func(self):
        return self.request.user and \
            (utils.is_adminschool(self.request.user) or utils.is_secretary(self.request.user))


class SuperUserPermissionMixin(UserPassesTestMixin):
    """
    Only logged super user can pass the test
    """
    def test_func(self):
        return self.request.user and self.request.user.is_superuser