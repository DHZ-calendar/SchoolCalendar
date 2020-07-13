from django.test import TestCase
from django.forms.models import model_to_dict
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class StageTestCase(BaseTestCase):
    def setUp(self):
        super(StageTestCase, self).setUp()
        self.school_year_2020 = SchoolYear(year_start=2020, date_start=datetime(month=8, year=2020, day=31))
        self.school_year_2020.save()
        # Create a course for the school s1
        self.course1 = Course(year=1, section='A', school_year=self.school_year_2020, school=self.s1)
        self.course2 = Course(year=1, section='A', school_year=self.school_year_2020, school=self.s2)
        self.course1.save()
        self.course2.save()

        self.form_data = {
            "date_start": datetime(day=23, month=6, year=2020),
            "date_end": datetime(day=23, month=6, year=2020),
            "course": self.course1,
            "school": self.s1,
            "name": "Difficult Stage"}

    def test_stage_correct_creation(self):

        """
        Test the creation of a Stage, using the correct admin and school.
        :return:
        """

        f = StageForm(user=self.a1, data=self.form_data)
        f.full_clean()
        self.assertTrue(f.is_valid())

    def test_stage_wrong_admin_for_school_creation(self):
        """
        Test the creation of a Stage, using the wrong school for the admin.
        :return:
        """
        # But admin of school 1
        f = StageForm(user=self.a2, data=self.form_data)
        f.full_clean()
        self.assertTrue(f.has_error('school'))   # The form should have an error on the school field.

    def test_stage_wrong_course_for_school_creation(self):
        """
        Test the creation of a stage, using the wrong course.
        :return:
        """
        form_data = {
            "date_start": datetime(day=23, month=6, year=2020),
            "date_end": datetime(day=23, month=6, year=2020),
            "course": self.course2,    # Wrong course
            "school": self.s1,
            "name": "Difficult Stage"}
        # But admin of school 1
        f = StageForm(user=self.a1, data=form_data)
        f.full_clean()
        self.assertTrue(f.has_error('course'))   # The form should have an error on the course field.

    def test_stage_wrong_course_and_school_for_admin_creation(self):
        """
        Test the creation of a stage, using the wrong course and school for admin.
        :return:
        """
        form_data = {
            "date_start": datetime(day=23, month=6, year=2020),
            "date_end": datetime(day=23, month=6, year=2020),
            "course": self.course2,  # Wrong course
            "school": self.s2,       # wrong school
            "school_year": self.school_year_2020,
            "name": "Difficult Stage"}
        # But admin of school 1
        f = StageForm(user=self.a1, data=form_data)
        f.full_clean()
        self.assertFalse(f.is_valid())  # The form should have an error on the course field.

    def test_stage_wrong_date(self):
        """
        Test the creation of a stage, using the wrong date (start > end)
        :return:
        """
        form_data = {
            "date_start": datetime(day=24, month=6, year=2020),   # start date is after end date
            "date_end": datetime(day=23, month=6, year=2020),
            "course": self.course1,    # Wrong course
            "school": self.s1,
            "school_year": self.school_year_2020,
            "name": "Difficult Stage"}
        # But admin of school 1
        f = StageForm(user=self.a1, data=form_data)
        f.full_clean()
        self.assertFalse(f.is_valid())   # The form should have error on the dates
