from django.test import TestCase
from django.forms.models import model_to_dict
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class AssignmentTestCase(BaseTestCase):
    def setUp(self):
        super(AssignmentTestCase, self).setUp()
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
        self.teacher3 = Teacher(
            first_name='Scrooge',
            last_name='McDuck',
            username='teacher3',
            email='s.m@fake.com',
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
        self.teacher3.save()
        self.teacher2.save()

        # Create two subjects for two different schools
        self.subj1 = Subject(name="Mathematics", school=self.s1)
        self.subj2 = Subject(name="English", school=self.s2)
        self.subj1.save()
        self.subj2.save()

        # Create two hour slot groups, one per each school.
        self.hsg1 = HourSlotsGroup(school=self.s1, school_year=self.school_year_2020, name='Default school 1')
        self.hsg2 = HourSlotsGroup(school=self.s2, school_year=self.school_year_2020, name='Default school 2')
        self.hsg1.save()
        self.hsg2.save()

        # Create two courses in different schools
        self.c1 = Course(year=1, section='A', hour_slots_group=self.hsg1)
        self.c3 = Course(year=2, section='B', hour_slots_group=self.hsg1)
        self.c2 = Course(year=2, section='B', hour_slots_group=self.hsg2)
        self.c1.save()
        self.c3.save()
        self.c2.save()

        # Create two hour_slots in two different schools
        self.hs1 = HourSlot(hour_number=4,
                            starts_at=time(hour=9, minute=0),
                            ends_at=time(hour=10, minute=5),
                            hour_slots_group=self.hsg1,
                            day_of_week=0,
                            legal_duration=timedelta(seconds=3600))
        self.hs2 = HourSlot(hour_number=4,
                            starts_at=time(hour=9, minute=0),
                            ends_at=time(hour=10, minute=5),
                            hour_slots_group=self.hsg2,
                            day_of_week=0,
                            legal_duration=timedelta(seconds=3600))
        self.hs1.save()
        self.hs2.save()

        # Create some hours per teacher in class
        self.hptic1 = HoursPerTeacherInClass(
            course=self.c1,
            subject=self.subj1,
            teacher=self.teacher1,
            school=self.s1,
            hours=100,
            hours_bes=100,
            hours_co_teaching=100)
        self.hptic3 = HoursPerTeacherInClass(
            course=self.c3,
            subject=self.subj1,
            teacher=self.teacher3,
            school=self.s1,
            hours=100,
            hours_bes=100,
            hours_co_teaching=100)

        self.hptic2 = HoursPerTeacherInClass(
            course=self.c2,
            subject=self.subj2,
            teacher=self.teacher2,
            school=self.s2,
            hours=100,
            hours_bes=100,
            hours_co_teaching=100)
        self.hptic1.save()
        self.hptic2.save()
        self.hptic3.save()

    def test_assignment_correct_creation(self):
        """
        Test the creation of an Assignment, using the correct admin and school.
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj1,
                'teacher': self.teacher1,
                'school': self.s1,
                'date': datetime(day=15, month=5, year=2020),
                'hour_start': time(hour=9, minute=0),
                'hour_end': time(hour=10, minute=5),
                'bes': 'false',
                'substitution': 'false',
                'absent': 'false'}
        f = AssignmentForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.is_valid())

    def test_assignment_wrong_admin_creation(self):
        """
        Test the creation of an Assignment, using the wrong admin.
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj1,
                'teacher': self.teacher1,
                'school': self.s1,
                'date': datetime(day=15, month=5, year=2020),
                'hour_start': time(hour=9, minute=0),
                'hour_end': time(hour=10, minute=5),
                'bes': 'false',
                'substitution': 'false',
                'absent': 'false'}
        f = AssignmentForm(user=self.a2, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('school'))
        self.assertTrue(f.has_error('course'))
        self.assertTrue(f.has_error('subject'))
        self.assertTrue(f.has_error('teacher'))

    def test_assignment_wrong_school_creation(self):
        """
        Test the creation of an Assignment, using the wrong school for the admin.
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj1,
                'teacher': self.teacher1,
                'school': self.s2,
                'date': datetime(day=15, month=5, year=2020),
                'hour_start': time(hour=9, minute=0),
                'hour_end': time(hour=10, minute=5),
                'bes': 'false',
                'substitution': 'false',
                'absent': 'false'}
        f = AssignmentForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('school'))

    def test_hours_per_teacher_in_class_wrong_teacher_creation(self):
        """
        Test the creation of an Assignment, using the wrong teacher for the admin.
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj1,
                'teacher': self.teacher2,
                'school': self.s1,
                'date': datetime(day=15, month=5, year=2020),
                'hour_start': time(hour=9, minute=0),
                'hour_end': time(hour=10, minute=5),
                'bes': 'false',
                'substitution': 'false',
                'absent': 'false'}
        f = AssignmentForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('teacher'))

    def test_assignment_wrong_course_creation(self):
        """
        Test the creation of an Assignment, using the wrong course for the admin.
        :return:
        """
        data = {'course': self.c2,
                'subject': self.subj1,
                'teacher': self.teacher1,
                'school': self.s1,
                'date': datetime(day=15, month=5, year=2020),
                'hour_start': time(hour=9, minute=0),
                'hour_end': time(hour=10, minute=5),
                'bes': 'false',
                'substitution': 'false',
                'absent': 'false'}
        f = AssignmentForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('course'))

    def test_assignment_wrong_subject_creation(self):
        """
        Test the creation of an Assignment, using the wrong subject for the admin.
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj2,
                'teacher': self.teacher1,
                'school': self.s1,
                'date': datetime(day=15, month=5, year=2020),
                'hour_start': time(hour=9, minute=0),
                'hour_end': time(hour=10, minute=5),
                'bes': 'false',
                'substitution': 'false',
                'absent': 'false'}
        f = AssignmentForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('subject'))

    def test_assignment_wrong_hour_creation(self):
        """
        Test the creation of an Assignment, using the hour_start (> hour_end).
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj2,
                'teacher': self.teacher1,
                'school': self.s1,
                'date': datetime(day=15, month=5, year=2020),
                'hour_start': time(hour=11, minute=0),
                'hour_end': time(hour=10, minute=5),
                'bes': 'false',
                'substitution': 'false',
                'absent': 'false'}
        f = AssignmentForm(user=self.a1, data=data)
        f.full_clean()
        self.assertFalse(f.is_valid())

    def test_assignment_wrong_hour_per_teacher_in_class_creation(self):
        """
        Test the creation of an Assignment, using the hour_start (> hour_end).
        :return:
        """
        data = {'course': self.c1,
                'subject': self.subj1,
                'teacher': self.teacher3,   # This teacher does not have class for such course.
                'school': self.s1,
                'date': datetime(day=15, month=5, year=2020),
                'hour_start': time(hour=9, minute=0),
                'hour_end': time(hour=10, minute=5),
                'bes': 'false',
                'substitution': 'false',
                'absent': 'false'}
        f = AssignmentForm(user=self.a1, data=data)
        f.full_clean()
        self.assertFalse(f.is_valid(), msg=f.errors)
