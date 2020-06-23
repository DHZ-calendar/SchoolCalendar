from django.test import TestCase

from timetable.models import *


class SchoolTestCase(TestCase):
    def setUp(self):
        School(name='Liceo Scientifico Alan Turing').save()

    def test_school(self):
        self.assertLess(0, School.objects.all().count())
