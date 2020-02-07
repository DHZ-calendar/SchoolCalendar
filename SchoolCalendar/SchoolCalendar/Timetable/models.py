from django.db import models
from django.contrib.auth.models import User

# Create your models here.


DAYS_OF_WEEK = (
    ('Monday', 0),
    ('Tuesday', 1),
    ('Wednesday', 2),
    ('Thursday', 3),
    ('Friday', 4),
    ('Saturday', 5),
    ('Sunday', 6)
)


class MyUser(User):
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


class Teacher(MyUser):
    """
    The teacher class inherits from MyUser, is only able to see her timetable
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False)
    notes = models.TextField(blank=True, null=True)   # Optional field


class AdminSchool(MyUser):
    """
    This is the headmaster, the only user capable to create the timetable
    """
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


class Course(models.Model):
    """
    Course is an alias for the class (like IA and so on)
    """
    year = models.IntegerField(blank=False, null=False)  # in class IA, year is 1
    section = models.CharField(max_length=256, blank=False, null=False)   # In class IA, the section is A
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT, blank=False, null=False)
    school = models.ForeignKey(School,  on_delete=models.CASCADE, blank=False, null=False)


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
    day_of_week = models.CharField(choices=DAYS_OF_WEEK, max_length=32, null=False, blank=False)
    # This counts the effective duration of each lecture (e.g., lectures of 55' actually are worth 1 hour)
    legal_duration = models.DurationField(null=False, blank=False)


class AbsenceBlock(models.Model):
    """
    Absence Block keeps track of hours when teachers are not available for teaching
    (It can be used to accommodate teachers with part-time contracts, or special needs)
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False)
    hour_slot = models.ForeignKey(HourSlot, on_delete=models.CASCADE, null=False, blank=False)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=False, blank=False)


class Holiday(models.Model):
    """
    Days when teachers don't have lectures
    """
    date = models.DateField(null=False, blank=False)
    name = models.CharField(max_length=256, null=False, blank=False)
    school = models.ForeignKey(School, null=False, blank=False, on_delete=models.PROTECT)
    # Maybe this is useless (as the information is kept in the date)
    school_year = models.ForeignKey(SchoolYear, null=False, blank=False, on_delete=models.CASCADE)


class Stage(models.Model):
    """
    During a stage, a class doesn't have teachers assigned (it is like an holiday, but specific for a given class).
    """
    date = models.DateField(null=False, blank=False)
    course = models.ForeignKey(Course, null=False, blank=False, on_delete=models.CASCADE)
    school = models.ForeignKey(School, null=False, blank=False, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, null=False, blank=False, on_delete=models.CASCADE)


class Subject(models.Model):
    """
    Subjects of courses
    """
    name = models.CharField(max_length=256, blank=False, null=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=False, blank=False)


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
    hour_start = models.TimeField()
    hour_end = models.TimeField()
    bes = models.BooleanField(null=False, blank=False, default=False)
    substitution = models.BooleanField(null=False, blank=False, default=False)
    absent = models.BooleanField(null=False, blank=False, default=False)   # for substituted teachers


