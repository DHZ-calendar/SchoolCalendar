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
    Custom Subclass for User, in order to save as many chickens as we can.
    """
    pass


class School(models.Model):
    name = models.CharField(max_length=256)


class Teacher(MyUser):
    """
    The teacher class inherits from User
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE)


class AdminSchool(MyUser):
    """
    This is the admin, has increased privileges wrt a normal Teacher
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE)


class SchoolYear(models.Model):
    """
    The school year is identified by a pair of consecutive years (like 2020/2021).
    Only the first year is stored, the ending year is always year_start + 1
    """
    year_start = models.IntegerField()   # If the school_year is 2020/2021, then we store only 2020


class Course(models.Model):
    """
    Course is an alias for the class (like IA and so on)
    """
    year = models.IntegerField()
    section = models.CharField(max_length=256)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    school = models.ForeignKey(School,  on_delete=models.CASCADE)


class HourSlot(models.Model):
    """
    HourSlot is used to store the time interval of first, second, third and so on hours.
    Every school, in fact, keeps them separately.
    """
    hour_number = models.IntegerField()   # Used to store first, second third hour and so on.
    starts_at = models.TimeField()
    ends_at = models.TimeField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    day_of_week = models.CharField(choices=DAYS_OF_WEEK, max_length=32)


