from django.test import TestCase
from django.forms.models import model_to_dict
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class AbsenceBlockTestCase(BaseTestCase):
    def setUp(self):
        super(AbsenceBlockTestCase, self).setUp()
        self.school_year_2020 = SchoolYear(year_start=2020, date_start=datetime(month=8, year=2020, day=31))
        self.school_year_2020.save()
        # Create two teachers in two different schools
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

        # Create hour slots and hour slots groups.
        self.hsg1 = HourSlotsGroup(name='default1', school=self.s1, school_year=self.school_year_2020)
        self.hsg2 = HourSlotsGroup(name='default2', school=self.s2, school_year=self.school_year_2020)
        self.hsg1.save()
        self.hsg2.save()
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

    def test_absence_block_correct_creation(self):
        """
        Test the creation of an Absence Block, using the correct admin and school.
        :return:
        """
        data = {'teacher': self.teacher1,
                'hour_slot': self.hs1}
        f = AbsenceBlockForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.is_valid(), msg=f.errors)

    def test_absence_block_wrong_teacher_creation(self):
        """
        Test the creation of a wrong Absence Block, using a teacher from a different school
        :return:
        """
        data = {'teacher': self.teacher2,    # Teacher from a different school
                'hour_slot': self.hs1}
        f = AbsenceBlockForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('teacher'))

    def test_absence_block_wrong_hour_slot_creation(self):
        """
        Test the creation of a wrong Absence Block, using an hour_slot from a different school
        :return:
        """
        data = {'teacher': self.teacher1,    # Teacher from a different school
                'hour_slot': self.hs2}
        f = AbsenceBlockForm(user=self.a1, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('hour_slot'))

    def test_absence_block_wrong_admin_creation(self):
        """
        Test the creation of a wrong Absence Block, using an admin from a different school
        :return:
        """
        data = {'teacher': self.teacher1,    # Teacher from a different school
                'hour_slot': self.hs1}
        f = AbsenceBlockForm(user=self.a2, data=data)
        f.full_clean()
        self.assertTrue(f.has_error('teacher'))
        self.assertTrue(f.has_error('hour_slot'))
