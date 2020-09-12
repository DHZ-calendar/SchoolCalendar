from django.test import TestCase
from django.forms.models import model_to_dict
from django.test import Client
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase
from timetable.views.other_views import TeacherSubstitutionView, SubstituteTeacherApiView


class ReplicateWeekTestCase(BaseTestCase):
    def setUp(self):
        super(ReplicateWeekTestCase, self).setUp()
        self.school_year_2020 = SchoolYear(year_start=2020, date_start=datetime(month=8, year=2020, day=31))
        self.school_year_2020.save()
        # Create some teachers
        self.t1 = Teacher(username='t1', school=self.s1, email='t1@g.com', password='password_demo',
                          first_name='fn1', last_name='ln1')
        self.t2 = Teacher(username='t2', school=self.s1, email='t2@g.com', password='password_demo',
                          first_name='fn2', last_name='ln2')
        self.t3 = Teacher(username='t3', school=self.s1, email='t3@g.com', password='password_demo',
                          first_name='fn3', last_name='ln3')
        self.t4 = Teacher(username='t4', school=self.s1, email='t4@g.com', password='password_demo',
                          first_name='fn4', last_name='ln4')
        self.t1.save()
        self.t2.save()
        self.t3.save()
        self.t4.save()

        # Create 2 hour slots groups in two different schools.
        self.hsg1 = HourSlotsGroup(school=self.s1, school_year=self.school_year_2020, name='Dafault school 1')
        self.hsg1.save()

        # Create some courses
        self.c1 = Course(year=1, section='A', hour_slots_group=self.hsg1)
        self.c2 = Course(year=1, section='B', hour_slots_group=self.hsg1)
        self.c3 = Course(year=1, section='C', hour_slots_group=self.hsg1)
        self.c1.save()
        self.c2.save()
        self.c3.save()
        # Create some rooms
        self.r1 = Room(name='lab1', capacity=2, school=self.s1)   # The room has capacity 2.
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
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h1_2 = HoursPerTeacherInClass(teacher=self.t1,
                                           course=self.c2,
                                           subject=self.sub1,
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h2_2 = HoursPerTeacherInClass(teacher=self.t2,
                                           course=self.c2,
                                           subject=self.sub2,
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h3_2 = HoursPerTeacherInClass(teacher=self.t3,
                                           course=self.c2,
                                           subject=self.sub3,
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h3_3 = HoursPerTeacherInClass(teacher=self.t3,
                                           course=self.c3,
                                           subject=self.sub3,
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h4_1 = HoursPerTeacherInClass(teacher=self.t4,
                                           course=self.c1,
                                           subject=self.sub1,
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h1_1.save()
        self.h1_2.save()
        self.h2_2.save()
        self.h3_2.save()
        self.h3_3.save()
        self.h4_1.save()

        self.hs1 = HourSlot(hour_number=2,
                            starts_at=time(hour=9, minute=0),
                            ends_at=time(hour=10, minute=0),
                            day_of_week=0,
                            legal_duration=timedelta(hours=1,minutes=0),
                            hour_slots_group=self.hsg1)
        self.hs1.save()

        # Create some assignments
        self.ass1 = Assignment(teacher=self.t1,
                               course=self.c1,
                               subject=self.sub1,
                               room=self.r1,
                               date=datetime(year=2020, month=5, day=4),  # Monday 4/5/2020
                               hour_start=time(hour=9, minute=0),
                               hour_end=time(hour=10, minute=0),
                               bes=False,
                               co_teaching=False,
                               substitution=False,
                               absent=False,
                               free_substitution=False)
        self.ass2 = Assignment(teacher=self.t2,
                               course=self.c2,
                               subject=self.sub2,
                               room=self.r1,
                               date=datetime(year=2020, month=5, day=4),  # Monday 4/5/2020
                               hour_start=time(hour=9, minute=0),
                               hour_end=time(hour=10, minute=0),
                               bes=False,
                               co_teaching=False,
                               substitution=False,
                               absent=False,
                               free_substitution=False)
        self.ass3 = Assignment(teacher=self.t1,
                               course=self.c1,
                               subject=self.sub1,
                               room=self.r1,
                               date=datetime(year=2020, month=5, day=4),  # Monday 4/5/2020
                               hour_start=time(hour=10, minute=0),
                               hour_end=time(hour=11, minute=0),
                               bes=False,
                               co_teaching=False,
                               substitution=False,
                               absent=False,
                               free_substitution=False)
        self.ass1.save()
        self.ass2.save()
        self.ass3.save()

        # Define the client, and login as preside1 of school s1.
        self.c = Client()
        self.c.login(username='preside1', password='password_demo')

    # Test 1: check that if only the available teachers are returned.
    def test_check_available_teachers(self):
        """
        Check the correctness of the available teachers for a substitution.
        """
        response = self.c.get('/timetable/teacher_can_substitute/' + str(self.ass1.id))
        json_res = response.json()
        self.assertTrue(len(json_res['available_teachers']) == 2)
        available_teachers_ids = [tea['id'] for tea in json_res['available_teachers']]
        self.assertTrue(self.t3.id in available_teachers_ids)
        self.assertTrue(self.t4.id in available_teachers_ids)

        self.assertTrue(len(json_res['other_teachers']) == 1)
        other_teachers_ids = [tea['id'] for tea in json_res['other_teachers']]
        self.assertTrue(self.t2.id in other_teachers_ids)

    def test_substitute_teacher(self):
        """
        Substitute a teacher with another one that is available.
        """
        response = self.c.post('/timetable/substitute_teacher_api/{0}/{1}'.format(self.ass1.id, self.t3.id))
        status_code = response.status_code
        self.assertTrue(status_code == 200)

        response = self.c.get('/timetable/api/assignments/{}/'.format(self.ass1.id))
        json_res = response.json()
        self.assertTrue(json_res['absent'])
        self.assertTrue(not json_res['substitution'])
        self.assertTrue(json_res['teacher']['id'] == self.t1.id)

        response = self.c.get('/timetable/api/assignments/')
        json_res = response.json()
        last_created = max(json_res, key=lambda x: x['id'])
        self.assertTrue(not last_created['absent'])
        self.assertTrue(last_created['substitution'])
        self.assertTrue(not last_created['free_substitution'])
        self.assertTrue(last_created['teacher']['id'] == self.t3.id)

    def test_substitute_teacher_free_substitution(self):
        """
        Substitute the teacher with another one with a free_substitution
        """
        response = self.c.post('/timetable/substitute_teacher_api/{0}/{1}'.format(self.ass1.id, self.t2.id))
        status_code = response.status_code
        self.assertTrue(status_code == 200)

        response = self.c.get('/timetable/api/assignments/{}/'.format(self.ass1.id))
        json_res = response.json()
        self.assertTrue(not json_res['absent'])
        self.assertTrue(not json_res['substitution'])
        self.assertTrue(json_res['teacher']['id'] == self.t1.id)

        response = self.c.get('/timetable/api/assignments/')
        json_res = response.json()
        last_created = max(json_res, key=lambda x: x['id'])
        self.assertTrue(not last_created['absent'])
        self.assertTrue(last_created['substitution'])
        self.assertTrue(last_created['free_substitution'])
        self.assertTrue(last_created['teacher']['id'] == self.t2.id)

