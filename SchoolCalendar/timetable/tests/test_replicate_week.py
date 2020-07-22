from django.test import TestCase
from django.forms.models import model_to_dict
from django.test import Client
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase
from timetable.views.other_views import CheckWeekReplicationView


class ReplicateWeekTestCase(BaseTestCase):
    def setUp(self):
        super(ReplicateWeekTestCase, self).setUp()
        self.school_year_2020 = SchoolYear(year_start=2020, date_start=datetime(month=8, year=2020, day=31))
        self.school_year_2020.save()
        # Create some teachers
        self.t1 = Teacher(username='t1', school=self.s1, email='t1@g.com', password='password_demo',
                          first_name='fn', last_name='ln')
        self.t2 = Teacher(username='t2', school=self.s1, email='t2@g.com')
        self.t3 = Teacher(username='t3', school=self.s1, email='t3@g.com')
        self.t1.save()
        self.t2.save()
        self.t3.save()
        # Create some courses
        self.c1 = Course(year=1, section='A', school_year=self.school_year_2020, school=self.s1)
        self.c2 = Course(year=1, section='B', school_year=self.school_year_2020, school=self.s1)
        self.c1.save()
        self.c2.save()
        # Create some rooms
        self.r1 = Room(name='lab1', capacity=2, school=self.s1)
        self.r1.save()
        # Create some subjects
        self.sub1 = Subject(name='Maths', school=self.s1)
        self.sub2 = Subject(name='Literature', school=self.s1)
        self.sub3 = Subject(name='Physics', school=self.s1)
        self.sub1.save()
        self.sub2.save()
        self.sub3.save()
        # Create some hoursperteacherinclass
        self.h1_1 = HoursPerTeacherInClass(teacher=self.t1,
                                           course=self.c1,
                                           subject=self.sub1,
                                           school=self.s1,
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h1_2 = HoursPerTeacherInClass(teacher=self.t1,
                                           course=self.c2,
                                           subject=self.sub1,
                                           school=self.s1,
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h2_2 = HoursPerTeacherInClass(teacher=self.t2,
                                           course=self.c1,
                                           subject=self.sub2,
                                           school=self.s1,
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h3_2 = HoursPerTeacherInClass(teacher=self.t3,
                                           course=self.c2,
                                           subject=self.sub3,
                                           school=self.s1,
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h1_1.save()
        self.h1_2.save()
        self.h2_2.save()
        self.h3_2.save()

        # Fill one week with some assignments that are going to be replicated.
        self.ass1 = Assignment(teacher=self.t1,
                               course=self.c1,
                               subject=self.sub1,
                               school=self.s1,
                               room=self.r1,
                               date=datetime(year=2020, month=5, day=4),  # Monday 4/5/2020
                               hour_start=time(hour=9, minute=0),
                               hour_end=time(hour=10, minute=0),
                               bes=False,
                               co_teaching=False,
                               substitution=False,
                               absent=False,
                               free_substitution=False)
        self.ass1.save()

        # Define the client, and login as preside1 of school s1.
        self.c = Client()
        self.c.login(username='preside1', password='password_demo')

    # Test 1: check that if there are two teachers in the same class, there is not a room conflict.
    def test_check_conflict_1(self):
        """
        Try to replicate one week which should be without conflicts, and check if it is indeed true.
        """
        response = self.c.post('/timetable/check_week_replication/2020-05-04/2020-05-24',
                               {'assignments[]': [self.ass1.id]})
        json_res = response.json()
        self.assertTrue(len(json_res['teacher_conflicts']) == 0)
        self.assertTrue(len(json_res['room_conflicts']) == 0)
        self.assertTrue(len(json_res['course_conflicts']) == 0)

    def test_check_conflict_2(self):
        """
        Try to replicate one week which should be with a teacher conflict.
        """
        ass2 = Assignment(teacher=self.t1,
                          course=self.c2,    # In course 2
                          subject=self.sub1,
                          school=self.s1,
                          room=self.r1,
                          date=datetime(year=2020, month=5, day=11),  # Monday 11/5/2020
                          hour_start=time(hour=9, minute=0),
                          hour_end=time(hour=10, minute=0),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass2.save()
        response = self.c.post('/timetable/check_week_replication/2020-05-04/2020-05-24',
                               {'assignments[]': [self.ass1.id]})
        json_res = response.json()
        self.assertTrue(len(json_res['teacher_conflicts']) == 1)
        self.assertTrue(len(json_res['room_conflicts']) == 0)
        self.assertTrue(len(json_res['course_conflicts']) == 0)
        ass2.delete()
