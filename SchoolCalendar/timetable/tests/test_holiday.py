from django.test import TestCase
from django.forms.models import model_to_dict
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class HolidayTestCase(BaseTestCase):
    def setUp(self):
        super(HolidayTestCase, self).setUp()
        self.school_year_2020 = SchoolYear(year_start=2020, date_start=datetime(month=8, year=2020, day=31))
        self.school_year_2020.save()

        self.form_data = {
            "date_start": datetime(day=22, month=6, year=2020),
            "date_end": datetime(day=23, month=6, year=2020),
            "school": self.s1,
            "school_year": self.school_year_2020,
            "name": "Resting Holiday"}

    def test_holiday_correct_creation(self):

        """
        Test the creation of a Holiday, using the correct admin and school.
        :return:
        """

        f = HolidayForm(user=self.a1, data=self.form_data)
        f.full_clean()
        self.assertTrue(f.is_valid())

    def test_holiday_wrong_admin_for_school_creation(self):
        """
        Test the creation of a Holiday, using the wrong school for the admin.
        :return:
        """
        # But admin of school 1
        f = HolidayForm(user=self.a2, data=self.form_data)
        f.full_clean()
        self.assertTrue(f.has_error('school'))   # The form should have an error on the school field.

    def test_holiday_wrong_date(self):
        """
        Test the creation of a Holiday, using the wrong date (start > end)
        :return:
        """
        form_data = {
            "date_start": datetime(day=24, month=6, year=2020),   # start date is after end date
            "date_end": datetime(day=23, month=6, year=2020),
            "school": self.s1,
            "school_year": self.school_year_2020,
            "name": "Holiday at the seaside"}
        f = HolidayForm(user=self.a1, data=form_data)
        f.full_clean()
        self.assertFalse(f.is_valid())   # The form should have error on the dates
