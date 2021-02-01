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

        # Create a teacher
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
                               substitution=True,
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
        # Define the client, and login as django admin.
        self.c_da = Client()
        self.c_da.login(username='admin', password='password_demo')

    def test_generic_webpages(self):
        """
        Test that some generic webpages are working.
        """
        response = self.c.get('/timetable/admin_school')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/substitute_teacher')
        self.assertTrue(response.status_code == 200)

        response = self.c_t.get('/timetable/teacher_view')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/room_view')
        self.assertTrue(response.status_code == 200)

    def test_summary_webpages(self):
        """
        Test that the summary webpages are working.
        """
        response = self.c.get('/timetable/teacher_summary_view')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/course_summary_view')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/substitution_summary_view')
        self.assertTrue(response.status_code == 200)

    def test_pdf_report_webpages(self):
        """
        Test that the pdf report webpages are working.
        """
        response = self.c.get('/timetable/timetable_report_view')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/substitution_pdf_ticket/{}'.format(self.ass1.id))
        self.assertTrue(response.status_code == 200)

    #CRUD entities

    def test_school_webpages(self):
        """
        Test that the schools' webpages are working.
        """
        response = self.c_da.get('/timetable/school/')
        self.assertTrue(response.status_code == 200)

        response = self.c_da.get('/timetable/school/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c_da.get('/timetable/school/{}/edit/'.format(self.s1.id))
        self.assertTrue(response.status_code == 200)

        response = self.c_da.get('/timetable/school/{}/delete/'.format(self.s1.id))
        self.assertTrue(response.status_code == 200)

    def test_room_webpages(self):
        """
        Test that the rooms' webpages are working.
        """
        response = self.c.get('/timetable/room/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/room/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/room/{}/edit/'.format(self.r1.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/room/{}/delete/'.format(self.r1.id))
        self.assertTrue(response.status_code == 200)

    def test_teacher_webpages(self):
        """
        Test that the teachers' webpages are working.
        """
        response = self.c.get('/timetable/teacher/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/teacher/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/teacher/{}/edit/'.format(self.t1.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/teacher/{}/delete/'.format(self.t1.id))
        self.assertTrue(response.status_code == 200)

    def test_admin_school_webpages(self):
        """
        Test that the admin_schools' webpages are working.
        """
        response = self.c_da.get('/timetable/admin_school/')
        self.assertTrue(response.status_code == 200)

        response = self.c_da.get('/timetable/admin_school/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c_da.get('/timetable/admin_school/{}/edit/'.format(self.a1.id))
        self.assertTrue(response.status_code == 200)

        response = self.c_da.get('/timetable/admin_school/{}/delete/'.format(self.a1.id))
        self.assertTrue(response.status_code == 200)

    def test_school_year_webpages(self):
        """
        Test that the school_years' webpages are working.
        """
        response = self.c_da.get('/timetable/school_year/')
        self.assertTrue(response.status_code == 200)

        response = self.c_da.get('/timetable/school_year/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c_da.get('/timetable/school_year/{}/edit/'.format(self.school_year_2020.id))
        self.assertTrue(response.status_code == 200)

        response = self.c_da.get('/timetable/school_year/{}/delete/'.format(self.school_year_2020.id))
        self.assertTrue(response.status_code == 200)

    def test_course_webpages(self):
        """
        Test that the courses' webpages are working.
        """
        response = self.c.get('/timetable/course/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/course/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/course/{}/edit/'.format(self.c1.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/course/{}/delete/'.format(self.c1.id))
        self.assertTrue(response.status_code == 200)

    def test_hour_slots_group_webpages(self):
        """
        Test that the hour_slots_groups' webpages are working.
        """
        response = self.c.get('/timetable/hour_slots_group/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/hour_slots_group/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/hour_slots_group/{}/edit/'.format(self.hsg1.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/hour_slots_group/{}/delete/'.format(self.hsg1.id))
        self.assertTrue(response.status_code == 200)

    def test_hour_slot_webpages(self):
        """
        Test that the hour_slots' webpages are working.
        """
        response = self.c.get('/timetable/hour_slot/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/hour_slot/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/hour_slot/{}/edit/'.format(self.hs1.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/hour_slot/{}/delete/'.format(self.hs1.id))
        self.assertTrue(response.status_code == 200)

    def test_absence_block_webpages(self):
        """
        Test that the absence_blocks' webpages are working.
        """
        response = self.c.get('/timetable/absence_block/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/absence_block/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/absence_block/{}/edit/'.format(self.absence_block.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/absence_block/{}/delete/'.format(self.absence_block.id))
        self.assertTrue(response.status_code == 200)

    def test_holiday_webpages(self):
        """
        Test that the holidays' webpages are working.
        """
        response = self.c.get('/timetable/holiday/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/holiday/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/holiday/{}/edit/'.format(self.holiday.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/holiday/{}/delete/'.format(self.holiday.id))
        self.assertTrue(response.status_code == 200)

    def test_stage_webpages(self):
        """
        Test that the stages' webpages are working.
        """
        response = self.c.get('/timetable/stage/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/stage/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/stage/{}/edit/'.format(self.stage.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/stage/{}/delete/'.format(self.stage.id))
        self.assertTrue(response.status_code == 200)

    def test_subject_webpages(self):
        """
        Test that the subjects' webpages are working.
        """
        response = self.c.get('/timetable/subject/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/subject/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/subject/{}/edit/'.format(self.sub1.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/subject/{}/delete/'.format(self.sub1.id))
        self.assertTrue(response.status_code == 200)

    def test_teachers_yearly_load_webpages(self):
        """
        Test that the teachers_yearly_loads' webpages are working.
        """
        response = self.c.get('/timetable/teachers_yearly_load/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/teachers_yearly_load/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/teachers_yearly_load/{}/edit/'.format(self.tyl.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/teachers_yearly_load/{}/delete/'.format(self.tyl.id))
        self.assertTrue(response.status_code == 200)

    def test_courses_yearly_load_webpages(self):
        """
        Test that the courses_yearly_loads' webpages are working.
        """
        response = self.c.get('/timetable/courses_yearly_load/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/courses_yearly_load/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/courses_yearly_load/{}/edit/'.format(self.cyl.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/courses_yearly_load/{}/delete/'.format(self.cyl.id))
        self.assertTrue(response.status_code == 200)

    def test_hours_per_teacher_in_class_webpages(self):
        """
        Test that the hours_per_teacher_in_classes' webpages are working.
        """
        response = self.c.get('/timetable/hours_per_teacher_in_class/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/hours_per_teacher_in_class/add/')
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/hours_per_teacher_in_class/{}/edit/'.format(self.h1_1.id))
        self.assertTrue(response.status_code == 200)

        response = self.c.get('/timetable/hours_per_teacher_in_class/{}/delete/'.format(self.h1_1.id))
        self.assertTrue(response.status_code == 200)

    def test_assignment_webpages(self):
        """
        Test that the assignments' webpages are working.
        """
        response = self.c.get('/timetable/assignment/add/')
        self.assertTrue(response.status_code == 200)
