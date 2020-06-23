from django.test import TestCase
from datetime import datetime

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class SchoolTestCase(BaseTestCase):
    def setUp(self):
        super(SchoolTestCase, self).setUp()

    def test_teacher_correct_creation(self):
        """
        Test the creation of a teacher, using the correct admin and school.
        :return:
        """
        form_data = {
            'first_name': 'Paolino',
            'last_name': 'Paperino',
            'username': 'paolino_paperino',
            'email': 'p.p@fake.com',
            'school': self.s1,
            'password1': 'password_demo',
            'password2': 'password_demo',
        }
        tf = TeacherForm(user=self.a1, data=form_data)
        tf.full_clean()
        self.assertTrue(tf.is_valid())

    def test_teacher_wrong_admin_for_school_creation(self):
        """
        Test the creation of a teacher, using the wrong school for the admin.
        :return:
        """
        form_data = {
            'first_name': 'Paolino',
            'last_name': 'Paperino',
            'username': 'paolino_paperino',
            'email': 'p.p@fake.com',
            'school': self.s2,    # School 2
            'password1': 'password_demo',
            'password2': 'password_demo',
        }
        # But admin of school 1
        tf = TeacherForm(user=self.a1, data=form_data)
        tf.full_clean()
        self.assertTrue(tf.has_error('school'))   # The form should have an error on the school field.
