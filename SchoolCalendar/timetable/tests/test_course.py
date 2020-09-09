from django.test import TestCase
from django.forms.models import model_to_dict
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class CourseTestCase(BaseTestCase):
    def setUp(self):
        super(CourseTestCase, self).setUp()
        self.school_year_2020 = SchoolYear(year_start=2020, date_start=datetime(month=8, year=2020, day=31))
        self.school_year_2020.save()

        # Create HourSlotsGroup
        self.hsg1 = HourSlotsGroup(school=self.s1, school_year=self.school_year_2020, name='Default school 1')
        self.hsg1.save()

        self.form_data = {
            "year": 1,
            "section": 'A',
            "hour_slots_group": self.hsg1.id,
        }

    def test_course_correct_creation(self):

        """
        Test the creation of a Course, using the correct admin and school.
        :return:
        """

        f = CourseForm(user=self.a1, data=self.form_data)
        f.full_clean()
        self.assertTrue(f.is_valid())

    def test_course_wrong_admin_for_school_creation(self):
        """
        Test the creation of a Course, using the wrong school for the admin.
        :return:
        """
        # But admin of school 1
        f = CourseForm(user=self.a2, data=self.form_data)
        f.full_clean()
        self.assertTrue(f.has_error('hour_slots_group'))   # The form should have an error on the school field.
