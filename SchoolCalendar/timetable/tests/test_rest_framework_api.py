from django.test import TestCase
from django.forms.models import model_to_dict
from django.test import Client
from datetime import datetime, timedelta, time

from timetable.models import *
from timetable.forms import *
from timetable.tests.base_test import BaseTestCase


class RestFrameworkApiTestCase(BaseTestCase):
    def setUp(self):
        super(RestFrameworkApiTestCase, self).setUp()
        self.school_year_2020 = SchoolYear(year_start=2020, date_start=datetime(month=8, year=2020, day=31))
        self.school_year_2020.save()
        # Create some teachers
        self.t1 = Teacher(username='t1', school=self.s1, email='t1@g.com', password='password_demo',
                          first_name='fn1', last_name='ln1')
        self.t1.set_password("password_demo")
        self.t1.save()

        # Create 2 hour slots groups in two different schools.
        self.hsg1 = HourSlotsGroup(school=self.s1, school_year=self.school_year_2020, name='Dafault school 1')
        self.hsg1.save()

        # Create some courses
        self.c1 = Course(year=1, section='A', hour_slots_group=self.hsg1)
        self.c1.save()
        # Create some rooms
        self.r1 = Room(name='lab1', capacity=2, school=self.s1)  # The room has capacity 2.
        self.r1.save()
        # Create some subjects
        self.sub1 = Subject(name='Maths', school=self.s1)
        self.sub1.save()
        # Create some hoursperteacherinclass
        self.h1_1 = HoursPerTeacherInClass(teacher=self.t1,
                                           course=self.c1,
                                           subject=self.sub1,
                                           hours=100,
                                           hours_bes=100,
                                           hours_co_teaching=100)
        self.h1_1.save()

        self.hs1 = HourSlot(hour_number=2,
                            starts_at=time(hour=9, minute=0),
                            ends_at=time(hour=10, minute=0),
                            day_of_week=0,
                            legal_duration=timedelta(hours=1, minutes=0),
                            hour_slots_group=self.hsg1)
        self.hs1.save()

        # Fill one week with one assignment
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
        self.ass1.save()

        self.holiday = Holiday(date_start=datetime(year=2020, month=12, day=25),
                               date_end=datetime(year=2020, month=12, day=25),
                               name="Christmas",
                               school=self.s1,
                               school_year=self.school_year_2020)
        self.holiday.save()

        self.stage = Stage(date_start=datetime(year=2020, month=11, day=25),
                           date_end=datetime(year=2020, month=11, day=25),
                           name="Internship",
                           course=self.c1)
        self.stage.save()

        self.absence_block = AbsenceBlock(teacher=self.t1,
                                          hour_slot=self.hs1)
        self.absence_block.save()

        self.tyl = TeachersYearlyLoad(teacher=self.t1,
                                      yearly_load=20,
                                      yearly_load_bes=0,
                                      yearly_load_co_teaching=0,
                                      school_year=self.school_year_2020)
        self.tyl.save()

        self.cyl = CoursesYearlyLoad(course=self.c1,
                                     yearly_load=20,
                                     yearly_load_bes=0)
        self.cyl.save()

        # Define the client, and login as preside1 of school s1.
        self.c = Client()
        self.c.login(username='preside1', password='password_demo')
        # Define the client, and login as teacher1 of school s1.
        self.c_t = Client()
        self.c_t.login(username='t1', password='password_demo')

    def test_teachers_api(self):
        """
        Test that the rest-framework teachers api are working.
        """
        response = self.c.get('/timetable/api/teachers/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_year_only_course_api(self):
        """
        Test that the rest-framework year_only_course api are working.
        """
        response = self.c.get('/timetable/api/year_only_course/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_section_only_course_api(self):
        """
        Test that the rest-framework section_only_course api are working.
        """
        response = self.c.get('/timetable/api/section_only_course/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_holidays_api(self):
        """
        Test that the rest-framework holidays api are working.
        """
        response = self.c.get('/timetable/api/holidays/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_rooms_api(self):
        """
        Test that the rest-framework rooms api are working.
        """
        response = self.c.get('/timetable/api/rooms/')
        json_res = response.json()
        self.assertTrue(len(json_res) == 1)

    def test_stages_api(self):
        """
        Test that the rest-framework stages api are working.
        """
        response = self.c.get('/timetable/api/stages/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_subjects_api(self):
        """
        Test that the rest-framework subjects api are working.
        """
        response = self.c.get('/timetable/api/subjects/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_hour_slots_api(self):
        """
        Test that the rest-framework hour_slots api are working.
        """
        response = self.c.get('/timetable/api/hour_slots/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_hour_slots_groups_api(self):
        """
        Test that the rest-framework hour_slots_groups api are working.
        """
        response = self.c.get('/timetable/api/hour_slots_groups/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_hour_per_teacher_in_class_api(self):
        """
        Test that the rest-framework hour_per_teacher_in_class api are working.
        """
        response = self.c.get('/timetable/api/hour_per_teacher_in_class/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_assignments_api(self):
        """
        Test that the rest-framework assignments api are working.
        """
        response = self.c.get('/timetable/api/assignments/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_substitutions_api(self):
        """
        Test that the rest-framework substitutions api are working.
        """
        assgn = Assignment(teacher=self.t1,
                           course=self.c1,
                           subject=self.sub1,
                           room=self.r1,
                           date=datetime(year=2020, month=5, day=4),  # Monday 4/5/2020
                           hour_start=time(hour=9, minute=0),
                           hour_end=time(hour=10, minute=0),
                           bes=False,
                           co_teaching=False,
                           substitution=True,
                           absent=False,
                           free_substitution=False)
        assgn.save()

        response = self.c.get('/timetable/api/substitutions/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_teacher_assignments_api(self):
        """
        Test that the rest-framework teacher_assignments api are working.
        """
        response = self.c.get('/timetable/api/teacher_assignments/{}/{}/'.format(self.t1.id, self.school_year_2020.id))
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_teacher_absence_block_api(self):
        """
        Test that the rest-framework teacher_absence_block api are working.
        """
        response = self.c.get('/timetable/api/teacher_absence_block/{}/{}/'.format(self.t1.id, self.school_year_2020.id))
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_teacher_timetable_api(self):
        """
        Test that the rest-framework teacher_timetable api are working.
        """
        response = self.c_t.get('/timetable/api/teacher_timetable/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_room_timetable_api(self):
        """
        Test that the rest-framework room_timetable api are working.
        """
        response = self.c.get('/timetable/api/room_timetable/{}/'.format(self.r1.id))
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_absence_blocks_api(self):
        """
        Test that the rest-framework absence_blocks api are working.
        """
        response = self.c.get('/timetable/api/absence_blocks/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_teachers_summary_api(self):
        """
        Test that the rest-framework teachers_summary api are working.
        """
        response = self.c.get('/timetable/api/teachers_summary/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_courses_summary_api(self):
        """
        Test that the rest-framework courses_summary api are working.
        """
        response = self.c.get('/timetable/api/courses_summary/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_teachers_yearly_loads_api(self):
        """
        Test that the rest-framework teachers_yearly_loads api are working.
        """
        response = self.c.get('/timetable/api/teachers_yearly_loads/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)

    def test_courses_yearly_loads_api(self):
        """
        Test that the rest-framework courses_yearly_loads api are working.
        """
        response = self.c.get('/timetable/api/courses_yearly_loads/')
        json_res = response.json()
        self.assertTrue(type(json_res) == list)
        self.assertTrue(len(json_res) == 1)
