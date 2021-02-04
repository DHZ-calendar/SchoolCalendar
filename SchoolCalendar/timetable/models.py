from colorfield.fields import ColorField
from django.db import models
from django.contrib.auth.models import User, UserManager, AbstractUser
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import queryable_property, SetterMixin, QueryableProperty

# Create your models here.


DAYS_OF_WEEK = (
    (0, _('Monday')),
    (1, _('Tuesday')),
    (2, _('Wednesday')),
    (3, _('Thursday')),
    (4, _('Friday')),
    (5, _('Saturday')),
    (6, _('Sunday'))
)


class MyUser(User):
    """
    Custom Subclass for User (in case we ever need it)
    """
    pass


class SchoolFromHourSlotsGroupProperty(SetterMixin, QueryableProperty):
    def get_value(self, obj):
        return obj.hour_slots_group.school

    def get_filter(self, cls, lookup, value):
        if lookup != 'exact':
            raise NotImplementedError()
        return Q(hour_slots_group__school=value)


class SchoolYearFromHourSlotsGroupProperty(SetterMixin, QueryableProperty):
    def get_value(self, obj):
        return obj.hour_slots_group.school_year

    def get_filter(self, cls, lookup, value):
        if lookup != 'exact':
            raise NotImplementedError()
        return Q(hour_slots_group__school_year=value)


class SchoolFromHourSlotProperty(SetterMixin, QueryableProperty):
    def get_value(self, obj):
        return obj.hour_slot.school

    def get_filter(self, cls, lookup, value):
        if lookup != 'exact':
            raise NotImplementedError()
        return Q(hour_slot__school=value)


class SchoolYearFromHourSlotProperty(SetterMixin, QueryableProperty):
    def get_value(self, obj):
        return obj.hour_slot.school_year

    def get_filter(self, cls, lookup, value):
        if lookup != 'exact':
            raise NotImplementedError()
        return Q(hour_slot__school_year=value)


class SchoolFromCourseProperty(SetterMixin, QueryableProperty):
    def get_value(self, obj):
        return obj.course.school

    def get_filter(self, cls, lookup, value):
        if lookup != 'exact':
            raise NotImplementedError()
        return Q(course__school=value)


class SchoolYearFromCourseProperty(SetterMixin, QueryableProperty):
    def get_value(self, obj):
        return obj.course.school_year

    def get_filter(self, cls, lookup, value):
        if lookup != 'exact':
            raise NotImplementedError()
        return Q(course__school_year=value)


class SchoolFromTeacherProperty(SetterMixin, QueryableProperty):
    def get_value(self, obj):
        return obj.teacher.school

    def get_filter(self, cls, lookup, value):
        if lookup != 'exact':
            raise NotImplementedError()
        return Q(teacher__school=value)


class School(models.Model):
    """
    This allows to keep more schools on the same db.
    In case we have one school per db, we can just set all foreign keys to a default value.
    """
    name = models.CharField(max_length=256, null=False, blank=False, verbose_name=_("name"))

    def __str__(self):
        return self.name


class Room(models.Model):
    """
    Every assignment can (optionally) be put in a Room.
    Every Room object has a certain capacity, so that if necessary more assignments can be held concurrently.
    If no room is specified for the assignment, it means that room conflicts are not a problem for that assignment.
    """
    name = models.CharField(max_length=256, null=False, blank=False, verbose_name=_("name"))
    capacity = models.IntegerField(null=False, blank=False, verbose_name=_("capacity"))
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("school"))

    def __str__(self):
        return self.name


class Teacher(MyUser):
    """
    The teacher class inherits from MyUser, is only able to see her timetable
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("school"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("notes"))  # Optional field
    # This field is used to choose not to visualize teachers in the right column in the timetable page.
    in_activity = models.BooleanField(default=True, null=False, blank=False, verbose_name=_("in activity"))

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class AdminSchool(MyUser):
    """
    This is the headmaster, the only user capable to create the timetable
    """

    class Meta:
        verbose_name = _('Admin School')

    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("school"))


class SchoolYear(models.Model):
    """
    The school year is identified by a pair of consecutive years (like 2020/2021).
    Only the first year is stored, the ending year is always year_start + 1
    """
    # If the school_year is 2020/2021, then we store only 2020
    year_start = models.IntegerField(blank=False, null=False, verbose_name=_("start year"))

    # Used to evaluate to which school_year any date belongs to. A good day could be the 31st of August
    date_start = models.DateField(blank=False, null=False, verbose_name=_("start date"))

    def __str__(self):
        """
        :return: School years displayed as 2019-2020
        """
        return "{}-{}".format(str(self.year_start), str(self.year_start + 1))


class HourSlotsGroup(models.Model):
    """
    Group up several HourSlots to define the blocks that compose a week
    """
    name = models.CharField(max_length=256, null=False, blank=False, verbose_name=_("name"))
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("school"))
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT, null=False, blank=False,
                                    verbose_name=_("school year"))

    def __str__(self):
        """
        :return: hourslots_group like "Standard week, 2019/2020"
        """
        return "{}, {}/{}".format(self.name,
                                  str(self.school_year.year_start),
                                  str(self.school_year.year_start + 1))


class HourSlot(models.Model):
    """
    HourSlot is used to store the time interval of first, second, third and so on hours.
    Every school, in fact, keeps them separately.
    """
    hour_number = models.IntegerField(blank=False, null=False, verbose_name=_(
        "hour number"))  # Used to store first, second third hour and so on.
    starts_at = models.TimeField(null=False, blank=False, verbose_name=_("begins at"))
    ends_at = models.TimeField(null=False, blank=False, verbose_name=_("ends at"))
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, null=False, blank=False, verbose_name=_("day of the week"))
    # This counts the effective duration of each lecture (e.g., lectures of 55' actually are worth 1 hour)
    legal_duration = models.DurationField(null=False, blank=False, verbose_name=_("legal duration"))
    hour_slots_group = models.ForeignKey(HourSlotsGroup, on_delete=models.CASCADE, null=False, blank=False,
                                         verbose_name=_("hour slots group"))

    school = SchoolFromHourSlotsGroupProperty()
    school_year = SchoolYearFromHourSlotsGroupProperty()

    objects = QueryablePropertiesManager()

    def __str__(self):
        """
        :return: hourslots like "Monday, 8:00-9:00 2019/2020"
        """
        return "{}, {}-{} {}/{} ({})".format(DAYS_OF_WEEK[self.day_of_week][1],
                                             self.starts_at.strftime("%H:%M"),
                                             self.ends_at.strftime("%H:%M"),
                                             str(self.hour_slots_group.school_year.year_start),
                                             str(self.hour_slots_group.school_year.year_start + 1),
                                             self.hour_slots_group.name)


class Course(models.Model):
    """
    Course is an alias for the class (like IA and so on)
    """
    year = models.IntegerField(blank=False, null=False, verbose_name=_("year"))  # in class IA, year is 1
    section = models.CharField(max_length=256, blank=False, null=False,
                               verbose_name=_("section"))  # In class IA, the section is A
    hour_slots_group = models.ForeignKey(HourSlotsGroup, on_delete=models.CASCADE, blank=False, null=False,
                                         verbose_name=_("hour slots group"))

    school = SchoolFromHourSlotsGroupProperty()
    school_year = SchoolYearFromHourSlotsGroupProperty()

    objects = QueryablePropertiesManager()

    class Meta:
        unique_together = ('year', 'section', 'hour_slots_group',)

    def __str__(self):
        """
        :return: classes as 1 A, 2 Bord and so on (according to what year and section are like)
        """
        return "{} {}, {}".format(str(self.year), self.section, str(self.hour_slots_group.school_year))


class AbsenceBlock(models.Model):
    """
    Absence Block keeps track of hours when teachers are not available for teaching
    (It can be used to accommodate teachers with part-time contracts, or special needs)
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("teacher"))
    hour_slot = models.ForeignKey(HourSlot, on_delete=models.CASCADE, null=False, blank=False,
                                  verbose_name=_("hour slot"))

    school = SchoolFromHourSlotProperty()
    school_year = SchoolYearFromHourSlotProperty()

    objects = QueryablePropertiesManager()

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
    date_start = models.DateField(null=False, blank=False, verbose_name=_("start date"))
    date_end = models.DateField(null=False, blank=False, verbose_name=_("end date"))
    name = models.CharField(max_length=256, null=False, blank=False, verbose_name=_("name"))
    school = models.ForeignKey(School, null=False, blank=False, on_delete=models.PROTECT, verbose_name=_("school"))
    # Maybe this is useless (as the information is kept in the date)
    school_year = models.ForeignKey(SchoolYear, null=False, blank=False, on_delete=models.CASCADE,
                                    verbose_name=_("school year"))

    def __str__(self):
        return _("{}: from {} to {}").format(self.name, self.date_start, self.date_end)


class Stage(models.Model):
    """
    During a stage, a class doesn't have teachers assigned (it is like an holiday, but specific for a given class).
    """
    date_start = models.DateField(null=False, blank=False, verbose_name=_("start date"))
    date_end = models.DateField(null=False, blank=False, verbose_name=_("end date"))
    course = models.ForeignKey(Course, null=False, blank=False, on_delete=models.CASCADE, verbose_name=_("course"))
    name = models.CharField(null=True, blank=True, max_length=256, verbose_name=_("name"))

    school = SchoolFromCourseProperty()
    school_year = SchoolYearFromCourseProperty()

    objects = QueryablePropertiesManager()

    def __str__(self):
        return _("{} from {} to {} in {} {}").format(
            self.name,
            self.date_start,
            self.date_end,
            self.course.year,
            self.course.section
        )


class Subject(models.Model):
    """
    Subjects of courses
    """
    name = models.CharField(max_length=256, blank=False, null=False, verbose_name=_("name"))
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("school"))

    color = ColorField(default='#20B2AA', null=False, blank=False, verbose_name=_("color"))

    def __str__(self):
        return self.name


class TeachersYearlyLoad(models.Model):
    """
    This model keeps track of how many hours any teacher needs to do in a school, in a certain school year.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False,
                                verbose_name=_("teacher"))
    # A teacher has both "normal" hours and "bes" hours
    yearly_load = models.IntegerField(null=False, blank=False, verbose_name=_("yearly load"))
    yearly_load_bes = models.IntegerField(null=False, blank=False, verbose_name=_("yearly load bes"))
    yearly_load_co_teaching = models.IntegerField(null=False, blank=False, verbose_name=_("yearly load co-teaching"))
    school_year = models.ForeignKey(SchoolYear, null=False, blank=False, on_delete=models.CASCADE,
                                    verbose_name=_("school year"))

    school = SchoolFromTeacherProperty()

    objects = QueryablePropertiesManager()

    def __str__(self):
        return _("{} in {}: {} and {} of bes").format(str(self.teacher),
                                                      str(self.school_year),
                                                      self.yearly_load,
                                                      self.yearly_load_bes)


class CoursesYearlyLoad(models.Model):
    """
    This model keeps track of how many hours any course needs to do.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False, blank=False,
                               verbose_name=_("course"))
    # A course has both "normal" hours and "bes" hours
    yearly_load = models.IntegerField(null=False, blank=False, verbose_name=_("yearly load"))
    yearly_load_bes = models.IntegerField(null=False, blank=False, verbose_name=_("yearly load bes"))
    # TODO: Do we want the co teaching hours in a course yearly load? :/

    school = SchoolFromCourseProperty()
    school_year = SchoolYearFromCourseProperty()

    objects = QueryablePropertiesManager()

    def __str__(self):
        return _("{}: {} and {} of bes").format(str(self.course),
                                                self.yearly_load,
                                                self.yearly_load_bes)


class HoursPerTeacherInClass(models.Model):
    """
    This model keeps track of how many hours any teacher has in every class.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False,
                                verbose_name=_("teacher"))
    course = models.ForeignKey(Course, null=False, blank=False, on_delete=models.CASCADE, verbose_name=_("course"))
    subject = models.ForeignKey(Subject, null=False, blank=False, on_delete=models.CASCADE, verbose_name=_("subject"))

    # A teacher has "normal" hours, "bes" hours and co-teaching hours.
    hours = models.IntegerField(null=False, blank=False, verbose_name=_("hours"))
    hours_bes = models.IntegerField(null=False, blank=False, verbose_name=_("hours BES"))
    hours_co_teaching = models.IntegerField(null=False, blank=False, verbose_name=_("Hours co-teaching"))

    school = SchoolFromCourseProperty()
    school_year = SchoolYearFromCourseProperty()

    objects = QueryablePropertiesManager()

    def __str__(self):
        return str(self.teacher) + " - " + str(self.course) + " " + self.subject.name


class Assignment(models.Model):
    """
    Assignment for a teacher in a class.
    Every hour has a different assignment.
    (Monday the 1st and Monday the 8th have two different assignments for the same teacher, hour_slot, class and room).
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=False, blank=False, verbose_name=_("teacher"))
    course = models.ForeignKey(Course, null=False, blank=False, on_delete=models.CASCADE, verbose_name=_("course"))
    subject = models.ForeignKey(Subject, null=False, blank=False, on_delete=models.CASCADE, verbose_name=_("subject"))
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_("room"))

    date = models.DateField(null=False, blank=False, verbose_name=_("date"))

    # Both hour start and hour end should coincide with the HourSlot if the hour is not special.
    hour_start = models.TimeField(null=False, blank=False, verbose_name=_("start hour"))
    hour_end = models.TimeField(null=False, blank=False, verbose_name=_("end hour"))
    bes = models.BooleanField(null=False, blank=False, default=False, verbose_name=_("BES"))
    co_teaching = models.BooleanField(null=False, blank=False, default=False, verbose_name=_("Co-teaching"))
    substitution = models.BooleanField(null=False, blank=False, default=False, verbose_name=_("substitution"))
    substituted_assignment = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True,
                                               default=None, verbose_name=_("substituted assignment"))
    absent = models.BooleanField(null=False, blank=False, default=False,
                                 verbose_name=_("absence"))  # for substituted teachers

    # it means that the substitution should not be considered when counting the total hours of substitutions
    free_substitution = models.BooleanField(null=False, blank=False, default=False, verbose_name=_("free substitution"))

    school = SchoolFromCourseProperty()
    school_year = SchoolYearFromCourseProperty()

    objects = QueryablePropertiesManager()

    def __str__(self):
        return "{}; {}; {}; {}; {} - {}".format(
            self.teacher,
            self.course,
            self.room if self.room is not None else _("No room"),
            self.date,
            self.hour_start,
            self.hour_end
        )
