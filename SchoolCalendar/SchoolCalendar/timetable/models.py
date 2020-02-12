from django.db import models
from django.contrib.auth.models import User, UserManager, AbstractUser
from django.utils.translation import gettext as _

# Create your models here.


DAYS_OF_WEEK = (
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday')
)


class MyUser(AbstractUser):
    """
    Custom Subclass for User (in case we ever need it)
    """
    pass


class School(models.Model):
    """
    This allows to keep more schools on the same db.
    In case we have one school per db, we can just set all foreign keys to a default value.
    """
    name = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.name


class Teacher(MyUser):
    """
    The teacher class inherits from MyUser, is only able to see her timetable
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False)
    notes = models.TextField(blank=True, null=True)   # Optional field

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class AdminSchool(MyUser):
    """
    This is the headmaster, the only user capable to create the timetable
    """
    class Meta:
        verbose_name = 'Admin School'
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False)


class SchoolYear(models.Model):
    """
    The school year is identified by a pair of consecutive years (like 2020/2021).
    Only the first year is stored, the ending year is always year_start + 1
    """
    # If the school_year is 2020/2021, then we store only 2020
    year_start = models.IntegerField(blank=False, null=False)

    # Used to evaluate to which school_year any date belongs to. A good day could be the 31st of August
    date_start = models.DateField(blank=False, null=False)

    def __str__(self):
        """
        :return: School years displayed as 2019-2020
        """
        return "{}-{}".format(str(self.year_start), str(self.year_start + 1))


class Course(models.Model):
    """
    Course is an alias for the class (like IA and so on)
    """
    year = models.IntegerField(blank=False, null=False)  # in class IA, year is 1
    section = models.CharField(max_length=256, blank=False, null=False)   # In class IA, the section is A
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT, blank=False, null=False)
    school = models.ForeignKey(School,  on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        """
        :return: classes as 1 A, 2 Bord and so on (according to what year and section are like)
        """
        return "{} {}".format(str(self.year), self.section)


class HourSlot(models.Model):
    """
    HourSlot is used to store the time interval of first, second, third and so on hours.
    Every school, in fact, keeps them separately.
    """
    hour_number = models.IntegerField(blank=False, null=False)   # Used to store first, second third hour and so on.
    starts_at = models.TimeField(null=False, blank=False)
    ends_at = models.TimeField(null=False, blank=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT, null=False, blank=False)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, null=False, blank=False)
    # This counts the effective duration of each lecture (e.g., lectures of 55' actually are worth 1 hour)
    legal_duration = models.DurationField(null=False, blank=False)

    def __str__(self):
        """
        :return: hourslots like "Monday, 8:00-9:00"
        """
        return "{}, {}-{}".format(DAYS_OF_WEEK[self.day_of_week][1],
                                  self.starts_at.strftime("%H:%M"),
                                  self.ends_at.strftime("%H:%M"),)


class AbsenceBlock(models.Model):
    """
    Absence Block keeps track of hours when teachers are not available for teaching
    (It can be used to accommodate teachers with part-time contracts, or special needs)
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    hour_slot = models.ForeignKey(HourSlot, on_delete=models.CASCADE, null=False, blank=False)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        """
        :return:
        """
        return "{}, {}, {}".format(str(self.teacher), str(self.hour_slot), str(self.school_year))


class Holiday(models.Model):
    """
    Days when teachers don't have lectures
    """
    # The holiday lasts from date_start to date_end inclusive
    # In order to make a 1 day holiday, just use the same date for both start and end.
    date_start = models.DateField(null=False, blank=False)
    date_end = models.DateField(null=False, blank=False)
    name = models.CharField(max_length=256, null=False, blank=False)
    school = models.ForeignKey(School, null=False, blank=False, on_delete=models.PROTECT)
    # Maybe this is useless (as the information is kept in the date)
    school_year = models.ForeignKey(SchoolYear, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return _("{}: from {} to {}".format(self.name, self.date_start, self.date_end))


class Stage(models.Model):
    """
    During a stage, a class doesn't have teachers assigned (it is like an holiday, but specific for a given class).
    """
    date_start = models.DateField(null=False, blank=False)
    date_end = models.DateField(null=False, blank=False)
    course = models.ForeignKey(Course, null=False, blank=False, on_delete=models.CASCADE)
    school = models.ForeignKey(School, null=False, blank=False, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, null=False, blank=False, on_delete=models.CASCADE)
    name = models.CharField(null=True, blank=True, max_length=256)


class Subject(models.Model):
    """
    Subjects of courses
    """
    name = models.CharField(max_length=256, blank=False, null=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.name


class HoursPerTeacherInClass(models.Model):
    """
    This model keeps track of how many hours any teacher has in every class.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    course = models.ForeignKey(Course, null=False, blank=False, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, null=False, blank=False, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, null=False, blank=False, on_delete=models.CASCADE)
    school = models.ForeignKey(School, null=False, blank=False, on_delete=models.CASCADE)

    # A teacher has both "normal" hours and "bes" hours
    hours = models.IntegerField(null=False, blank=False)
    hours_bes = models.IntegerField(null=False, blank=False)


class Assignment(models.Model):
    """
    Assignment for a teacher in a class.
    Every hour has a different assignment.
    (Monday the 1st and Monday the 8th have two different assignments for the same teacher, hour_slot and class).
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    course = models.ForeignKey(Course, null=False, blank=False, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, null=False, blank=False, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, null=False, blank=False, on_delete=models.CASCADE)
    school = models.ForeignKey(School, null=False, blank=False, on_delete=models.CASCADE)

    date = models.DateField(null=False, blank=False)

    # Both hour start and hour end should coincide with the HourSlot if the hour is not special.
    hour_start = models.TimeField(null=False, blank=False)
    hour_end = models.TimeField(null=False, blank=False)
    bes = models.BooleanField(null=False, blank=False, default=False)
    substitution = models.BooleanField(null=False, blank=False, default=False)
    absent = models.BooleanField(null=False, blank=False, default=False)   # for substituted teachers

    def __str__(self):
        return "{}; {}; {}; {} - {}".format(
            self.teacher, self.course, self.date, self.hour_start, self.hour_end
        )
