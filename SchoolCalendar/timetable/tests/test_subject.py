from django.test import TestCase
from datetime import datetime

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class SubjectTestCase(BaseTestCase):
    def setUp(self):
        super(SubjectTestCase, self).setUp()

    def test_subject_correct_creation(self):
        """
        Test the creation of a subject, using the correct admin and school.
        :return:
        """
        form_data = {
            'name': 'Mathematics',
            'school': self.s1,

        }
        f = SubjectForm(user=self.a1, data=form_data)
        f.full_clean()
        self.assertTrue(f.is_valid())

    def test_subject_wrong_admin_for_school_creation(self):
        """
        Test the creation of a subject, using the wrong school for the admin.
        :return:
        """
        form_data = {
            'name': 'Mathematics',
            'school': self.s1,

        }
        # But admin of school 1
        f = SubjectForm(user=self.a2, data=form_data)
        f.full_clean()
        self.assertTrue(f.has_error('school'))   # The form should have an error on the school field.
