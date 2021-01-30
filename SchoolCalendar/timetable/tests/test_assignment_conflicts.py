from django.test import TestCase
from django.forms.models import model_to_dict
from datetime import datetime, timedelta, time
from django.test import Client

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class AssignmentConflictsTestCase(BaseTestCase):
    def setUp(self):
        super(AssignmentConflictsTestCase, self).setUp()
        self.school_year_2020 = SchoolYear(year_start=2020, date_start=datetime(month=8, year=2020, day=31))
        self.school_year_2020.save()

        self.t1 = Teacher(
            first_name='Paolino',
            last_name='Paperino',
            username='teacher1',
            email='p.p@fake.com',
            school=self.s1,
            password='password_demo'
        )
        self.t2 = Teacher(
            first_name='Micky',
            last_name='Mouse',
            username='teacher2',
            email='m.m@fake.com',
            school=self.s2,
            password='password_demo'
        )
        self.t1.save()
        self.t2.save()

        # Create 2 hour slots groups.
        self.hsg1 = HourSlotsGroup(school=self.s1, school_year=self.school_year_2020, name='Default school 1')
        self.hsg2 = HourSlotsGroup(school=self.s1, school_year=self.school_year_2020, name='Default school 2')
        self.hsg1.save()
        self.hsg2.save()

        self.subj1 = Subject(name="Mathematics", school=self.s1)
        self.subj2 = Subject(name="English", school=self.s2)
        self.subj1.save()
        self.subj2.save()

        self.c1 = Course(year=1, section='A', hour_slots_group=self.hsg1)
        self.c3 = Course(year=2, section='B', hour_slots_group=self.hsg1)
        self.c2 = Course(year=1, section='B', hour_slots_group=self.hsg2)
        self.c1.save()
        self.c3.save()
        self.c2.save()

        # Create two hour_slots
        self.hs1 = HourSlot(hour_number=4,
                            starts_at=time(hour=9, minute=0),
                            ends_at=time(hour=10, minute=0),
                            hour_slots_group=self.hsg1,
                            day_of_week=0,
                            legal_duration=timedelta(seconds=3600))
        self.hs2 = HourSlot(hour_number=4,
                            starts_at=time(hour=9, minute=30),
                            ends_at=time(hour=10, minute=30),
                            hour_slots_group=self.hsg2,
                            day_of_week=0,
                            legal_duration=timedelta(seconds=3600))
        self.hs1.save()
        self.hs2.save()

        # Define the client, and login as preside1 of school s1.
        self.c = Client()
        self.c.login(username='preside1', password='password_demo')

    def test_no_conflicts(self):
        """
        Test when there aren't any conflicts because the assignment time doesn't collide with an hour slot.
        :return:
        """
        ass1 = Assignment(teacher=self.t1,
                          course=self.c1,
                          subject=self.subj1,
                          room=None,
                          date=datetime(day=14, month=9, year=2020),
                          hour_start=time(hour=8, minute=0),
                          hour_end=time(hour=9, minute=0),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass1.save()

        response = self.c.get('/timetable/api/teacher_assignments/{}/{}/'.format(self.t1.id, self.school_year_2020.id))
        json_res = response.json()
        found = False
        for assgn in json_res:
            if assgn['id'] == ass1.id:
                found = True
                self.assertTrue(len(assgn['conflicting_hour_slots']) == 0)
        self.assertTrue(found)

    def test_conflict_in_one_hsg(self):
        """
        Test when there is a conflict in one hour slot group.
        :return:
        """
        ass1 = Assignment(teacher=self.t1,
                          course=self.c1,
                          subject=self.subj1,
                          room=None,
                          date=datetime(day=14, month=9, year=2020),
                          hour_start=time(hour=8, minute=30),
                          hour_end=time(hour=9, minute=30),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass1.save()

        response = self.c.get(
            '/timetable/api/teacher_assignments/{}/{}/'.format(self.t1.id, self.school_year_2020.id))
        json_res = response.json()
        found = False
        for assgn in json_res:
            if assgn['id'] == ass1.id:
                found = True
                self.assertTrue(len(assgn['conflicting_hour_slots']) == 1)
                self.assertTrue(self.hs1.id in assgn['conflicting_hour_slots'])
        self.assertTrue(found)

    def test_conflict_in_different_hsg(self):
        """
        Test when there is a conflict in two different hour slot groups.
        :return:
        """
        ass1 = Assignment(teacher=self.t1,
                          course=self.c1,
                          subject=self.subj1,
                          room=None,
                          date=datetime(day=14, month=9, year=2020),
                          hour_start=time(hour=9, minute=30),
                          hour_end=time(hour=10, minute=30),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass1.save()

        response = self.c.get(
            '/timetable/api/teacher_assignments/{}/{}/'.format(self.t1.id, self.school_year_2020.id))
        json_res = response.json()
        found = False
        for assgn in json_res:
            if assgn['id'] == ass1.id:
                found = True
                self.assertTrue(len(assgn['conflicting_hour_slots']) == 2)
                self.assertTrue(self.hs1.id in assgn['conflicting_hour_slots'])
                self.assertTrue(self.hs2.id in assgn['conflicting_hour_slots'])
        self.assertTrue(found)
