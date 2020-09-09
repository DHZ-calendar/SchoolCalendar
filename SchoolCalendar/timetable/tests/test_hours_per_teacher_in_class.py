from django.test import TestCase
from django.forms.models import model_to_dict
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class HoursTeacherInClassTestCase(BaseTestCase):
    def setUp(self):
        super(HoursTeacherInClassTestCase, self).setUp()
        self.school_year_2020 = SchoolYear(year_start=2020, date_start=datetime(month=8, year=2020, day=31))
        self.school_year_2020.save()
        # Create two teachers in different schools
        self.teacher1 = Teacher(
            first_name='Paolino',
            last_name='Paperino',
            username='teacher1',
            email='p.p@fake.com',
            school=self.s1,
            password='password_demo'
        )
        self.teacher2 = Teacher(
            first_name='Micky',
            last_name='Mouse',
            username='teacher2',
            email='m.m@fake.com',
            school=self.s2,
            password='password_demo'
        )
        self.teacher1.save()
        self.teacher2.save()

        # Create two subjects for two different schools
        self.subj1 = Subject(name="mathematics", school=self.s1)
        self.subj2 = Subject(name="Englisj", school=self.s2)
        self.subj1.save()
        self.subj2.save()

        # Create 2 hour slots groups in two different schools.
        self.hsg1 = HourSlotsGroup(school=self.s1, school_year=self.school_year_2020, name='Dafault school 1')
        self.hsg2 = HourSlotsGroup(school=self.s2, school_year=self.school_year_2020, name='Dafault school 2')
        self.hsg1.save()
        self.hsg2.save()

        # Create two courses in different schools
        self.c1 = Course(year=1, section='A', hour_slots_group=self.hsg1)
        self.c2 = Course(year=2, section='B', hour_slots_group=self.hsg2)
        self.c1.save()
        self.c2.save()

    def test_hours_per_teacher_in_class_correct_creation(self):
        """
        Test the creation of an HourPerTeacherInClass, using the correct admin and school.
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj1,
                'teacher': self.teacher1,
                'hours': 100,
                'hours_bes': 150,
                'hours_co_teaching': 150}
        f = HoursPerTeacherInClassForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.is_valid())

    def test_hours_per_teacher_in_class_wrong_admin_creation(self):
        """
        Test the creation of an HourPerTeacherInClass, using the wrong admin.
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj1,
                'teacher': self.teacher1,
                'hours': 100,
                'hours_bes': 150,
                'hours_co_teaching': 150}
        f = HoursPerTeacherInClassForm(user=self.a2, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('course'))
        self.assertTrue(f.has_error('subject'))
        self.assertTrue(f.has_error('teacher'))

    def test_hours_per_teacher_in_class_wrong_teacher_creation(self):
        """
        Test the creation of an HourPerTeacherInClass, using the wrong teacher for the admin.
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj1,
                'teacher': self.teacher2,
                'hours': 100,
                'hours_bes': 150,
                'hours_co_teaching': 150}
        f = HoursPerTeacherInClassForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('teacher'))

    def test_hours_per_teacher_in_class_wrong_course_creation(self):
        """
        Test the creation of an HourPerTeacherInClass, using the wrong course for the admin.
        :return:
        """
        data = {'course': self.c2,
                'subject': self.subj1,
                'teacher': self.teacher1,
                'hours': 100,
                'hours_bes': 150,
                'hours_co_teaching': 150}
        f = HoursPerTeacherInClassForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('course'))

    def test_hours_per_teacher_in_class_wrong_subject_creation(self):
        """
        Test the creation of an HourPerTeacherInClass, using the wrong subject for the admin.
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj2,
                'teacher': self.teacher1,
                'hours': 100,
                'hours_bes': 150,
                'hours_co_teaching': 150}
        f = HoursPerTeacherInClassForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('subject'))
