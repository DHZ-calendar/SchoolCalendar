from django.test import TestCase
from django.forms.models import model_to_dict
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class SchoolYearTestCase(BaseTestCase):
    def setUp(self):
        super(SchoolYearTestCase, self).setUp()

    def test_school_year_correct_creation(self):
        """
        Test the creation of a school year, using the correct date of start
        :return:
        """
        data = {'year_start': 2020,
                'date_start': "2020-08-31"}
        f = SchoolYearForm(data=data)
        f.full_clean()
        self.assertTrue(f.is_valid())

    def test_school_year_wrong_creation(self):
        """
        Test the creation of a school_year, using the wrong start_date.
        :return:
        """
        data = {'year_start': 2021,
                'date_start': datetime(year=2020, month=8, day=31)}
        f = SchoolYearForm(data=data)
        f.full_clean()
        self.assertFalse(f.is_valid())

