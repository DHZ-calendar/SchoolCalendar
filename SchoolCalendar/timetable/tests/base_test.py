from django.test import TestCase
from datetime import datetime

from timetable.models import *
from timetable.forms import *


class BaseTestCase(TestCase):
    def setUp(self):
        self.s1 = School(name='Scuola 1')
        self.s2 = School(name='Scuola 2')
        self.s1.save()
        self.s2.save()
        self.sy = SchoolYear(date_start=datetime(day=31, month=8, year=2020), year_start=2020)
        self.a1 = AdminSchool(first_name='marco', last_name='rossi', username='preside1', email='m.r@fake.com',
                              password='password_demo', school=self.s1)
        self.a2 = AdminSchool(first_name='andrea', last_name='verdi', username='preside2', email='a.v@fake.com',
                              password='password_demo', school=self.s2)
        self.sy.save()
        self.a1.save()
        self.a2.save()
