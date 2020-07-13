from django.core.management.base import BaseCommand, CommandError

from timetable.models import *

import random
import datetime
import numpy as np

from SchoolCalendar.timetable.models import AbsenceBlock

PASSWORD_DEMO = 'password_demo'

HOUR_SLOT_LIST = [
    ((7, 55), (8, 45)),
    ((8, 45), (9, 35)),
    ((9, 35), (10, 25)),
    ((10, 35), (11, 25)),
    ((11, 25), (12, 15))
]


class Command(BaseCommand):
    help = 'Populate a new DB with some teachers. ' \
           'In order to run smooth, first you need to remove the previous database (rm db.sqlite3), create a new one ' \
           'and apply the migrations (python manage.py migrate), and lastly run the populate_db script (python ' \
           'manage.py populate_db)'

    def create_school(self, name):
        school = School(name=name)
        school.save()
        return school

    def create_admin_school(self, first_name, last_name, school):
        admin_school = AdminSchool.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                school=school,
                email="{}.{}@{}.com".format(first_name, last_name, "".join(school.name.split())),
                username='{}_{}'.format("".join(first_name.lower().split()),
                                        "".join(last_name.lower().split())),
                password=PASSWORD_DEMO)
        admin_school.save()
        return admin_school

    def create_teacher(self, first_name, last_name, school):
        teacher = Teacher.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            school=school,
            email="{}.{}@{}.com".format(first_name, last_name, "".join(school.name.split())),
            username='{}_{}'.format("".join(first_name.lower().split()),
                                  "".join(last_name.lower().split())),
            password=PASSWORD_DEMO)
        teacher.save()
        return teacher

    def create_school_year(self, year_start, date_start):
        sy = SchoolYear(year_start=year_start, date_start=date_start)
        sy.save()
        return sy

    def create_course(self, year, section, school_year, school):
        c = Course(year=year, section=section, school_year=school_year, school=school)
        c.save()
        return c

    def create_hour_slot(self, hour_number, starts_at, ends_at, school, school_year, day_of_week, legal_duration):
        hs = HourSlot(hour_number=hour_number, starts_at=starts_at, ends_at=ends_at, school=school,
                      school_year=school_year, day_of_week=day_of_week, legal_duration=legal_duration)
        hs.save()
        return hs

    def get_hours_slots(self, from_hour, to_hour, day_of_week, school, school_year):
        return HourSlot.objects.filter(starts_at__gte=from_hour,
                                       ends_at__lte=to_hour,
                                       day_of_week=day_of_week,
                                       school=school,
                                       school_year=school_year)



    def handle(self, *args, **options):
        school = self.create_school("Liceo Scientifico Galileo Galilei Trento")

        # Create the school admin
        admin_school = self.create_admin_school("Patrizio", "Tizi", school)

        # Create the teachers
        teachers = list()
        teachers.append(self.create_teacher('Marco', 'Rossi', school))
        teachers.append(self.create_teacher('Mattia', 'Bianchi', school))
        teachers.append(self.create_teacher('Andrea', 'Verdi', school))
        teachers.append(self.create_teacher('Franca', 'Benedetti', school))
        teachers.append(self.create_teacher('Lucia', 'Legni', school))
        teachers.append(self.create_teacher('Gianmarco', 'Nardi', school))
        teachers.append(self.create_teacher('Francesco', 'Franchi', school))
        teachers.append(self.create_teacher('Antonio', 'Puro', school))
        teachers.append(self.create_teacher('Laura', 'Brevi', school))
        teachers.append(self.create_teacher('Daniela', 'Conci', school))
        teachers.append(self.create_teacher('Valentino', 'Aspi', school))
        teachers.append(self.create_teacher('Loredana', 'Brancacci', school))
        teachers.append(self.create_teacher('Sandro', 'Moro', school))
        teachers.append(self.create_teacher('Giovanna', 'Ciola', school))

        # Create School Years
        school_years = list()
        for i in range (0, 10):
            school_years.append(self.create_school_year(2019-i, datetime.datetime(year=2019-i, month=8, day=31)))

        # Create Courses:
        courses = list()
        for i in range(1,6):
            courses.append(self.create_course(i, 'A ORD', school_years[0], school))

        hour_slots = list()
        for day_of_week in range(0, 6):
            for i, el in enumerate(HOUR_SLOT_LIST):
                hour_slots.append(self.create_hour_slot(hour_number=i+1,
                                                        starts_at=datetime.time(hour=el[0][0], minute=el[0][1]),
                                                        ends_at=datetime.time(hour=el[1][0], minute=el[1][1]),
                                                        school=school,
                                                        school_year=school_years[0],
                                                        day_of_week=day_of_week,
                                                        legal_duration=datetime.timedelta(hours=1)))

        # Create some random absence blocks
        absences = {}
        for t in teachers:
            # Add a random number of absences blocks: every teacher gets assigned with 1 to 5 absence blocks.
            number_of_absence_blocks = [1, 2, 3, 4, 5]
            absences[t.username] = []
            permutation_of_absence_blocks = np.random.permutation(len(hour_slots))
            for i in range(0, random.choice(number_of_absence_blocks)):
                absences[t.username].append(AbsenceBlock(teacher=t,
                                                         hour_slot=hour_slots[permutation_of_absence_blocks[i]]))
            for el in absences[t.username]:
                el.save()

        # Create Holidays
        holidays = []
        holidays.append(Holiday(date_start=datetime.datetime(year=2019, month=12, day=23),
                                date_end=datetime.datetime(year=2020, month=1, day=5),
                                name='Christmas',
                                school=school,
                                school_year=school_years[0]).save())

        holidays.append(Holiday(date_start=datetime.datetime(year=2020, month=4, day=9),
                                date_end=datetime.datetime(year=2020, month=4, day=14),
                                name='Easter',
                                school=school,
                                school_year=school_years[0]).save())

        holidays.append(Holiday(date_start=datetime.datetime(year=2020, month=2, day=22),
                                date_end=datetime.datetime(year=2020, month=2, day=25),
                                name='Carnival',
                                school=school,
                                school_year=school_years[0]).save())

        holidays.append(Holiday(date_start=datetime.datetime(year=2020, month=4, day=25),
                                date_end=datetime.datetime(year=2020, month=4, day=25),
                                name='Liberation Day',
                                school=school,
                                school_year=school_years[0]).save())

        # Add stages
        stages = []
        stages.append(Stage(date_start=datetime.datetime(year=2020, month=4, day=30),
                            date_end=datetime.datetime(year=2020, month=5, day=16),
                            course=courses[0],
                            school=school,
                            name="Contability by local industry",
                            school_year=school_years[0]).save())
        stages.append(Stage(date_start=datetime.datetime(year=2019, month=12, day=2),
                            date_end=datetime.datetime(year=2019, month=12, day=6),
                            course=courses[1],
                            school=school,
                            name="Physics laboratory in research lab.",
                            school_year=school_years[0]).save())
        stages.append(Stage(date_start=datetime.datetime(year=2020, month=1, day=20),
                            date_end=datetime.datetime(year=2020, month=1, day=25),
                            course=courses[2],
                            school=school,
                            name="Robotics lab.",
                            school_year=school_years[0]).save())
        stages.append(Stage(date_start=datetime.datetime(year=2020, month=3, day=9),
                            date_end=datetime.datetime(year=2020, month=3, day=21),
                            course=courses[3],
                            school=school,
                            name="Philosophy lecture at university.",
                            school_year=school_years[0]).save())
        stages.append(Stage(date_start=datetime.datetime(year=2019, month=10, day=7),
                            date_end=datetime.datetime(year=2019, month=10, day=19),
                            course=courses[4],
                            school=school,
                            name="Programming laboratory.",
                            school_year=school_years[0]).save())

        # Create subjects
        subjects = []
        subjects.append(Subject(name='Mathematics',
                                school=school,
                                school_year=school_years[0]).save())

        subjects.append(Subject(name='Physics',
                                school=school,
                                school_year=school_years[0]).save())

        subjects.append(Subject(name='Italian',
                                school=school,
                                school_year=school_years[0]).save())

        subjects.append(Subject(name='Latin',
                                school=school,
                                school_year=school_years[0]).save())

        subjects.append(Subject(name='Religion',
                                school=school,
                                school_year=school_years[0]).save())

        subjects.append(Subject(name='History',
                                school=school,
                                school_year=school_years[0]).save())

        subjects.append(Subject(name='Philosophy',
                                school=school,
                                school_year=school_years[0]).save())

        subjects.append(Subject(name='Science',
                                school=school,
                                school_year=school_years[0]).save())

        # Create HoursPerTeacherInClass:
        hours_per_teacher_in_class = []
        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='marco_rossi'),
                                                                 course=Course.objects.get(year=1, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Mathematics'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=140,
                                                                 hours_bes=0,).save())
        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='marco_rossi'),
                                                                 course=Course.objects.get(year=2, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Mathematics'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=140,
                                                                 hours_bes=0,).save())
        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='marco_rossi'),
                                                                 course=Course.objects.get(year=1, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Physics'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=100,
                                                                 hours_bes=0, ).save())
        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='marco_rossi'),
                                                                 course=Course.objects.get(year=2, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Physics'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=100,
                                                                 hours_bes=0, ).save())

        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='mattia_bianchi'),
                                                                 course=Course.objects.get(year=3, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Mathematics'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=140,
                                                                 hours_bes=0, ).save())
        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='mattia_bianchi'),
                                                                 course=Course.objects.get(year=4, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Mathematics'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=140,
                                                                 hours_bes=0, ).save())
        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='mattia_bianchi'),
                                                                 course=Course.objects.get(year=3, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Physics'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=100,
                                                                 hours_bes=0, ).save())
        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='mattia_bianchi'),
                                                                 course=Course.objects.get(year=4, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Physics'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=100,
                                                                 hours_bes=0, ).save())

        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='andrea_verdi'),
                                                                 course=Course.objects.get(year=1, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Italian'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=170,
                                                                 hours_bes=0, ).save())
        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='andrea_verdi'),
                                                                 course=Course.objects.get(year=4, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Italian'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=170,
                                                                 hours_bes=0,).save())

        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='franca_benedetti'),
                                                                 course=Course.objects.get(year=5, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Italian'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=170,
                                                                 hours_bes=0, ).save())
        hours_per_teacher_in_class.append(HoursPerTeacherInClass(teacher=Teacher.objects.get(username='franca_benedetti'),
                                                                 course=Course.objects.get(year=2, section='A ORD'),
                                                                 subject=Subject.objects.get(name='Italian'),
                                                                 school_year=school_years[0],
                                                                 school=school,
                                                                 hours=170,
                                                                 hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='franca_benedetti'),
                                   course=Course.objects.get(year=5, section='A ORD'),
                                   subject=Subject.objects.get(name='Latin'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=100,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='franca_benedetti'),
                                   course=Course.objects.get(year=2, section='A ORD'),
                                   subject=Subject.objects.get(name='Latin'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=100,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='franca_benedetti'),
                                   course=Course.objects.get(year=4, section='A ORD'),
                                   subject=Subject.objects.get(name='Latin'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=100,
                                   hours_bes=0, ).save())

        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='lucia_legni'),
                                   course=Course.objects.get(year=1, section='A ORD'),
                                   subject=Subject.objects.get(name='Latin'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=100,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='lucia_legni'),
                                   course=Course.objects.get(year=3, section='A ORD'),
                                   subject=Subject.objects.get(name='Latin'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=100,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='lucia_legni'),
                                   course=Course.objects.get(year=3, section='A ORD'),
                                   subject=Subject.objects.get(name='Italian'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=170,
                                   hours_bes=0, ).save())

        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='gianmarco_nardi'),
                                   course=Course.objects.get(year=5, section='A ORD'),
                                   subject=Subject.objects.get(name='Mathematics'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=140,
                                   hours_bes=0, ).save())

        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='francesco_franchi'),
                                   course=Course.objects.get(year=5, section='A ORD'),
                                   subject=Subject.objects.get(name='Physics'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=100,
                                   hours_bes=0, ).save())

        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='antonio_puro'),
                                   course=Course.objects.get(year=1, section='A ORD'),
                                   subject=Subject.objects.get(name='Religion'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=40,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='antonio_puro'),
                                   course=Course.objects.get(year=2, section='A ORD'),
                                   subject=Subject.objects.get(name='Religion'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=40,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='antonio_puro'),
                                   course=Course.objects.get(year=3, section='A ORD'),
                                   subject=Subject.objects.get(name='Religion'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=40,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='antonio_puro'),
                                   course=Course.objects.get(year=4, section='A ORD'),
                                   subject=Subject.objects.get(name='Religion'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=40,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='antonio_puro'),
                                   course=Course.objects.get(year=5, section='A ORD'),
                                   subject=Subject.objects.get(name='Religion'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=40,
                                   hours_bes=0, ).save())

        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='laura_brevi'),
                                   course=Course.objects.get(year=1, section='A ORD'),
                                   subject=Subject.objects.get(name='Philosophy'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=100,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='laura_brevi'),
                                   course=Course.objects.get(year=3, section='A ORD'),
                                   subject=Subject.objects.get(name='Philosophy'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=100,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='laura_brevi'),
                                   course=Course.objects.get(year=3, section='A ORD'),
                                   subject=Subject.objects.get(name='History'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=80,
                                   hours_bes=0, ).save())

        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='daniela_conci'),
                                   course=Course.objects.get(year=2, section='A ORD'),
                                   subject=Subject.objects.get(name='History'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=80,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='daniela_conci'),
                                   course=Course.objects.get(year=5, section='A ORD'),
                                   subject=Subject.objects.get(name='History'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=80,
                                   hours_bes=0, ).save())

        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='valentino_aspi'),
                                   course=Course.objects.get(year=2, section='A ORD'),
                                   subject=Subject.objects.get(name='Philosophy'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=100,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='valentino_aspi'),
                                   course=Course.objects.get(year=4, section='A ORD'),
                                   subject=Subject.objects.get(name='Philosophy'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=100,
                                   hours_bes=0, ).save())

        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='loredana_brancacci'),
                                   course=Course.objects.get(year=1, section='A ORD'),
                                   subject=Subject.objects.get(name='History'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=80,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='loredana_brancacci'),
                                   course=Course.objects.get(year=4, section='A ORD'),
                                   subject=Subject.objects.get(name='History'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=80,
                                   hours_bes=0, ).save())

        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='sandro_moro'),
                                   course=Course.objects.get(year=3, section='A ORD'),
                                   subject=Subject.objects.get(name='Science'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=140,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='sandro_moro'),
                                   course=Course.objects.get(year=4, section='A ORD'),
                                   subject=Subject.objects.get(name='Science'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=140,
                                   hours_bes=0, ).save())

        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='giovanna_ciola'),
                                   course=Course.objects.get(year=1, section='A ORD'),
                                   subject=Subject.objects.get(name='Science'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=140,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='giovanna_ciola'),
                                   course=Course.objects.get(year=2, section='A ORD'),
                                   subject=Subject.objects.get(name='Science'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=140,
                                   hours_bes=0, ).save())
        hours_per_teacher_in_class.append(
            HoursPerTeacherInClass(teacher=Teacher.objects.get(username='giovanna_ciola'),
                                   course=Course.objects.get(year=5, section='A ORD'),
                                   subject=Subject.objects.get(name='Science'),
                                   school_year=school_years[0],
                                   school=school,
                                   hours=140,
                                   hours_bes=0, ).save())

