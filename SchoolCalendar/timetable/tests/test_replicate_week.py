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

        # Fill one week with some assignments that are going to be replicated.
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

    def test_check_conflict_3(self):
        """
        Try to replicate one week which should be with a course conflict.
        """
        ass2 = Assignment(teacher=self.t2,
                          course=self.c1,    # In course 1, hence a course conflict
                          subject=self.sub1,
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
        self.assertTrue(len(json_res['teacher_conflicts']) == 0)
        self.assertTrue(len(json_res['room_conflicts']) == 0)
        self.assertTrue(len(json_res['course_conflicts']) == 1)
        ass2.delete()

    def test_check_conflict_4(self):
        """
        Try to replicate one week where a room is filled with 2 courses, but the room has capacity 2.
        """
        ass2 = Assignment(teacher=self.t2,
                          course=self.c2,    # In course 1, hence a course conflict
                          subject=self.sub2,
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
        self.assertTrue(len(json_res['teacher_conflicts']) == 0)
        self.assertTrue(len(json_res['room_conflicts']) == 0)
        self.assertTrue(len(json_res['course_conflicts']) == 0)
        ass2.delete()

    def test_check_conflict_5(self):
        """
        Try to replicate one week where a room is filled with 3 courses, but the room has capacity 2.
        """
        ass2 = Assignment(teacher=self.t2,
                          course=self.c2,
                          subject=self.sub2,
                          room=self.r1,            # Room 1 is already filled with 2 courses.
                          date=datetime(year=2020, month=5, day=11),  # Monday 11/5/2020
                          hour_start=time(hour=9, minute=0),
                          hour_end=time(hour=10, minute=0),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass2.save()
        ass3 = Assignment(teacher=self.t3,
                          course=self.c3,
                          subject=self.sub3,
                          room=self.r1,           # room 1 is filled with 2 courses already
                          date=datetime(year=2020, month=5, day=11),  # Monday 11/5/2020
                          hour_start=time(hour=9, minute=0),
                          hour_end=time(hour=10, minute=0),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass3.save()
        # This has no use for the room conflict, but could still cause troubles for the view,
        # so it is better to test with it.
        ass4 = Assignment(teacher=self.t3,
                          course=self.c3,
                          subject=self.sub3,
                          room=self.r1,           # room 1 is filled with 2 courses already
                          date=datetime(year=2020, month=5, day=18),  # Monday 18/5/2020
                          hour_start=time(hour=9, minute=0),
                          hour_end=time(hour=10, minute=0),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass4.save()
        response = self.c.post('/timetable/check_week_replication/2020-05-04/2020-05-24',
                               {'assignments[]': [self.ass1.id]})
        json_res = response.json()
        self.assertTrue(len(json_res['teacher_conflicts']) == 0)
        self.assertTrue(len(json_res['room_conflicts']) == 2)  # There are 2 possible courses that are in conflict!
        self.assertTrue(len(json_res['course_conflicts']) == 0)
        ass2.delete()
        ass3.delete()
        ass4.delete()

    def test_check_conflict_6(self):
        """
        Try to replicate one week where a room is filled with 3 courses, on Monday but of different days.
        """
        ass2 = Assignment(teacher=self.t2,
                          course=self.c2,
                          subject=self.sub2,
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
        ass3 = Assignment(teacher=self.t2,
                          course=self.c2,
                          subject=self.sub2,
                          room=self.r1,
                          date=datetime(year=2020, month=5, day=18),  # Monday 18/5/2020
                          hour_start=time(hour=9, minute=0),
                          hour_end=time(hour=10, minute=0),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass3.save()
        response = self.c.post('/timetable/check_week_replication/2020-05-04/2020-05-24',
                               {'assignments[]': [self.ass1.id]})
        json_res = response.json()
        self.assertTrue(len(json_res['teacher_conflicts']) == 0)
        # There should not be any room conflict, assignments are on different days
        self.assertTrue(len(json_res['room_conflicts']) == 0)
        self.assertTrue(len(json_res['course_conflicts']) == 0)
        ass2.delete()
        ass3.delete()

    def test_check_conflict_6(self):
        """
        Add test for multiple teachers in the same course and hour slot.
        Room capacity should count only the courses which are concurrent, not the number of assignments
        (since there could be multiple assignments for the same course).
        """
        ass2 = Assignment(teacher=self.t2,   # Theacher 2 in course 2
                          course=self.c2,
                          subject=self.sub2,
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
        ass3 = Assignment(teacher=self.t3,    # Teacher 3 in course 2.
                          course=self.c2,
                          subject=self.sub2,
                          room=self.r1,
                          date=datetime(year=2020, month=5, day=11),  # Monday 11/5/2020
                          hour_start=time(hour=9, minute=0),
                          hour_end=time(hour=10, minute=0),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass3.save()
        response = self.c.post('/timetable/check_week_replication/2020-05-04/2020-05-24',
                               {'assignments[]': [self.ass1.id]})
        json_res = response.json()
        self.assertTrue(len(json_res['teacher_conflicts']) == 0)
        # There should not be no room conflict, assignments on the 11th of May are in the same course.
        self.assertTrue(len(json_res['room_conflicts']) == 0)
        self.assertTrue(len(json_res['course_conflicts']) == 0)
        ass2.delete()
        ass3.delete()

    def test_check_conflict_7(self):
        """
        Add test for multiple teachers in the same course and hour slot.
        The assignment checked (ass1) would be the second for the day in the same course (ass4).
        Hence, no room conflict should be raised.
        Still, there should be a course conflict!
        """
        ass2 = Assignment(teacher=self.t2,   # Theacher 2 in course 2
                          course=self.c2,
                          subject=self.sub2,
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
        ass3 = Assignment(teacher=self.t3,    # Teacher 3 in course 2.
                          course=self.c2,
                          subject=self.sub2,
                          room=self.r1,
                          date=datetime(year=2020, month=5, day=11),  # Monday 11/5/2020
                          hour_start=time(hour=9, minute=0),
                          hour_end=time(hour=10, minute=0),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass3.save()
        ass4 = Assignment(teacher=self.t4,  # Teacher 3 in course 2.
                          course=self.c1,
                          subject=self.sub2,
                          room=self.r1,
                          date=datetime(year=2020, month=5, day=11),  # Monday 11/5/2020
                          hour_start=time(hour=9, minute=0),
                          hour_end=time(hour=10, minute=0),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass4.save()
        response = self.c.post('/timetable/check_week_replication/2020-05-04/2020-05-24',
                               {'assignments[]': [self.ass1.id]})
        json_res = response.json()
        self.assertTrue(len(json_res['teacher_conflicts']) == 0)
        # There should not be no room conflict, assignments on the 11th of May are in the same course.
        self.assertTrue(len(json_res['room_conflicts']) == 0)
        self.assertTrue(len(json_res['course_conflicts']) == 1)
        ass2.delete()
        ass3.delete()
        ass4.delete()

    def test_speed_multiple_assignments_check_1(self):
        """
        Try to create a bunch of assignments, and test that the time taken by the view is not too long!
        """
        # Create a lot of assignments in the same hour slot.
        start_date = datetime(year=2019, month=9, day=16)
        assignments = []
        assignments_to_check = []
        for day in range(7):
            for hour in range(8, 14):
                for i in range(50):
                    ass1 = Assignment(teacher=self.t1,
                                      course=self.c1,
                                      subject=self.sub1,
                                      room=self.r1,
                                      date=start_date + timedelta(days=day) + timedelta(days=7*i),
                                      hour_start=time(hour=hour, minute=0),
                                      hour_end=time(hour=hour + 1, minute=0),
                                      bes=False,
                                      co_teaching=False,
                                      substitution=False,
                                      absent=False,
                                      free_substitution=False)
                    ass1.save()
                    assignments.append(ass1)
                ass1 = Assignment(teacher=self.t1,
                                  course=self.c1,
                                  subject=self.sub1,
                                  room=self.r1,
                                  date=datetime(year=2019, month=9, day=9) + timedelta(days=day),
                                  hour_start=time(hour=hour, minute=0),
                                  hour_end=time(hour=hour + 1, minute=0),
                                  bes=False,
                                  co_teaching=False,
                                  substitution=False,
                                  absent=False,
                                  free_substitution=False)
                ass1.save()
                assignments_to_check.append(ass1.id)

        print(len(assignments))   # Make the assignments in advance.
        print(len(assignments_to_check))
        start = datetime.now()
        response = self.c.post('/timetable/check_week_replication/2020-05-04/2020-05-24',
                               {'assignments[]': assignments_to_check})
        json_res = response.json()
        print(len(json_res['teacher_conflicts']))
        end = datetime.now()
        print(start, end)
        self.assertLessEqual((end - start).seconds, 3)     # Just a good constant, so that github can run it :)
        for el in assignments:
            el.delete()
        Assignment.objects.filter(id__in=assignments_to_check).delete()

    def test_course_already_present_in_replicated_week(self):
        """
        Assume we want to replicate one week. The week after should be empty so that no conflicts are shown.
        But maybe we have the exact copy of one of the courses we are going to replicate.
        So, although in theory one conflict should be shown, in practice we do not want to have any.
        In this example, the assign1 is present in both week 1 and 2 (1 is the week we want to replicate into 2).
        So, assign1 should not be shown as a conflict.
        """
        ass1 = Assignment(teacher=self.t1,
                          course=self.c1,
                          subject=self.sub1,
                          room=self.r1,
                          date=datetime(day=14, month=9, year=2020),
                          hour_start=time(hour=7, minute=55),
                          hour_end=time(hour=8, minute=45),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass2 = Assignment(teacher=self.t1,
                          course=self.c1,
                          subject=self.sub1,
                          room=self.r1,
                          date=datetime(day=14, month=9, year=2020),
                          hour_start=time(hour=8, minute=45),
                          hour_end=time(hour=9, minute=35),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass3 = Assignment(teacher=self.t1,         # Replicated course. It should not be considered as a conflict.
                          course=self.c1,
                          subject=self.sub1,
                          room=self.r1,
                          date=datetime(day=21, month=9, year=2020),
                          hour_start=time(hour=7, minute=55),
                          hour_end=time(hour=8, minute=45),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass1.save()
        ass2.save()
        ass3.save()
        response = self.c.post('/timetable/check_week_replication/2020-09-21/2020-09-27',
                               {'assignments[]': [ass1.id, ass2.id]})
        json_res = response.json()
        # Assert that no conflict is raised, although there already is the copy of course 1 in week 21/9 - 27/9
        self.assertTrue(len(json_res['teacher_conflicts']) == 0)
        self.assertTrue(len(json_res['room_conflicts']) == 0)
        self.assertTrue(len(json_res['course_conflicts']) == 0)
        ass1.delete()
        ass2.delete()
        ass3.delete()

    def test_course_already_present_in_replicated_week_2(self):
        """
        When we replicate a week, and in the next week we already have the assignment that we are replicating, then
        no conflicts should be raised (test before) and no new assignment should be created.
        """
        ass1 = Assignment(teacher=self.t1,
                          course=self.c1,
                          subject=self.sub1,
                          room=self.r1,
                          date=datetime(day=14, month=9, year=2020),
                          hour_start=time(hour=7, minute=55),
                          hour_end=time(hour=8, minute=45),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass2 = Assignment(teacher=self.t1,
                          course=self.c1,
                          subject=self.sub1,
                          room=self.r1,
                          date=datetime(day=14, month=9, year=2020),
                          hour_start=time(hour=8, minute=45),
                          hour_end=time(hour=9, minute=35),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass3 = Assignment(teacher=self.t1,         # Replicated course. It should not be considered as a conflict.
                          course=self.c1,
                          subject=self.sub1,
                          room=self.r1,
                          date=datetime(day=21, month=9, year=2020),
                          hour_start=time(hour=7, minute=55),
                          hour_end=time(hour=8, minute=45),
                          bes=False,
                          co_teaching=False,
                          substitution=False,
                          absent=False,
                          free_substitution=False)
        ass1.save()
        ass2.save()
        ass3.save()
        response = self.c.post('/timetable/replicate_week/add/{school_year}/{course}/2020-09-21/2020-09-27'.format(
                school_year=self.school_year_2020.id,
                course=self.c1.pk),
            {'assignments[]': [ass1.id, ass2.id]})
        # Assert that no conflict is raised, although there already is the copy of course 1 in week 21/9 - 27/9
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Assignment.objects.filter(teacher=self.t1,
                                                  course=self.c1,
                                                  subject=self.sub1,
                                                  room=self.r1,
                                                  date=datetime(day=21, month=9, year=2020),
                                                  hour_start=time(hour=8, minute=45),
                                                  hour_end=time(hour=9, minute=35)).exists())
        self.assertTrue(Assignment.objects.filter(teacher=self.t1,
                                                  course=self.c1,
                                                  subject=self.sub1,
                                                  room=self.r1,
                                                  date=datetime(day=21, month=9, year=2020),
                                                  hour_start=time(hour=7, minute=55),
                                                  hour_end=time(hour=8, minute=45)).exists())
        ass1.delete()
        ass2.delete()
        ass3.delete()
