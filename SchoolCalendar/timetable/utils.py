import datetime
import random
import string

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.db.models import Q
from timetable.models import Teacher, AdminSchool, HoursPerTeacherInClass, Assignment, HourSlot, School


def get_school_from_user(user):
    """
    Returns the school related to a Teacher or an AdminSchool instance.
    :param user:
    :return: the school related to that user. None if no teacher or AdminSchool is related to that user.
    """
    teacher = Teacher.objects.filter(id=user.id)
    if teacher:
        return teacher[0].school
    admin_school = AdminSchool.objects.filter(id=user.id)
    if admin_school:
        return admin_school[0].school
    return None


def convert_weekday_into_0_6_format(day):
    """
    Dates go from 1 (Sunday) to 7 (Saturday), whereas our db keeps them from 0 (Monday) to 6 (Sunday)
    :param day:
    :return:
    """
    return (day - 2) % 7


def convert_weekday_into_1_7_format(day):
    """
        Dates go from 1 (Sunday) to 7 (Saturday), whereas our db keeps them from 0 (Monday) to 6 (Sunday)
        :param day: from 0 to 6
        :return:
        """
    return (day + 2) % 7


def get_closest_smaller_Monday():
    return datetime.datetime.now().date() - datetime.timedelta(days=datetime.datetime.now().date().weekday())


def is_date_string_valid(date_str):
    """
    Returns True only if the specified string is in the format YYYY-MM-DD
    """
    try:
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def is_adminschool(user):
    """
    :param user:
    :return: True when the user is an AdminSchool corresponding to the given user
    """
    if not user:
        return False
    return AdminSchool.objects.filter(id=user.id).exists()


def compute_total_hours_assignments(assignments, hours_slots):
    """
    In order to compute the total_hour_assignments for a teacher, we should merge assignments with the
    hour_slots in a left outer join fashion.
    Where there exists an hour slot for a given assignment, then we should use the 'legal_duration' field.
    Where there is no time_slot for it, we should use instead the actual duration of the assignment.
    :param assignments: the list of assignments for a given teacher, course, school_year, school, subject (bes and
                        co-teaching can be both True or False, but not True at the same time).
    :param hours_slots: the list of hour_slots for a given school and school_year
    :return: the total number of hours planned (both past and in the future) for a given teacher, course, school,
             school_year, subject.
    """
    # Create a 3 dimensional map, indexed by day_of_week, starts_at, ends_at -> legal_duration
    map_hour_slots = {}
    for el in hours_slots:
        if el['day_of_week'] not in map_hour_slots:
            map_hour_slots[el['day_of_week']] = {}
        if el['starts_at'] not in map_hour_slots[el['day_of_week']]:
            map_hour_slots[el['day_of_week']][el['starts_at']] = {}
        if el['ends_at'] not in map_hour_slots[el['day_of_week']][el['starts_at']]:
            map_hour_slots[el['day_of_week']][el['starts_at']][el['ends_at']] = {}
        map_hour_slots[el['day_of_week']][el['starts_at']][el['ends_at']] = el['legal_duration']

    for el in assignments:
        if el["date__week_day"] in map_hour_slots and el['hour_start'] in map_hour_slots[el['date__week_day']] and \
                el['hour_end'] in map_hour_slots[el['date__week_day']][el['hour_start']]:
            el['legal_duration'] = map_hour_slots[el['date__week_day']][el['hour_start']][el['hour_end']]
        else:
            el['legal_duration'] = datetime.datetime.combine(datetime.date.min, el['hour_end']) - \
                                   datetime.datetime.combine(datetime.date.min, el['hour_start'])

    total = datetime.timedelta(0)
    for el in assignments:
        total += el['legal_duration']
    return int(total.seconds / 3600)


def get_teachers_hours_info(school):
    teachers_report = []
    for hptic in HoursPerTeacherInClass.objects.filter(school_id=school)\
            .order_by('teacher__last_name', 'teacher__first_name', 'course__year', 'course__section'):
        assignments = Assignment.objects.filter(teacher=hptic.teacher,
                                                course=hptic.course,
                                                subject=hptic.subject,
                                                school=hptic.school,
                                                school_year=hptic.school_year).values(
            'date__week_day', 'hour_start', 'hour_end')
        for el in assignments:
            el['date__week_day'] = convert_weekday_into_0_6_format(el['date__week_day'])

        hours_slots = HourSlot.objects.filter(school=hptic.school,
                                              school_year=hptic.school_year).values("day_of_week", "starts_at",
                                                                                    "ends_at", "legal_duration")
        # TODO: Make tests for co-teaching!
        # Normal assignments lessons
        normal_done_assign = assignments.filter(bes=False, substitution=False, co_teaching=False)
        total_normal_done = compute_total_hours_assignments(normal_done_assign, hours_slots)

        # Substitution assignments
        subst_done_assign = Assignment.objects.filter(teacher=hptic.teacher,
                                                      school=hptic.school,
                                                      school_year=hptic.school_year,
                                                      substitution=True, free_substitution=False).values(
            'date__week_day', 'hour_start', 'hour_end')
        for el in subst_done_assign:
            el['date__week_day'] = convert_weekday_into_0_6_format(el['date__week_day'])
        total_subst_done = compute_total_hours_assignments(subst_done_assign, hours_slots)

        # BES assignments
        bes_done_assign = assignments.filter(bes=True)
        total_bes_done = compute_total_hours_assignments(bes_done_assign, hours_slots)

        # Co-teaching assignments
        co_teaching_done_assign = assignments.filter(co_teaching=True)
        total_co_teaching_done = compute_total_hours_assignments(co_teaching_done_assign, hours_slots)

        teachers_report.append({
            'first_name': hptic.teacher.first_name,
            'last_name': hptic.teacher.last_name,
            'subject': hptic.subject.name,
            'course': str(hptic.course.year) + " " + hptic.course.section,
            'normal_done': total_normal_done,
            'substitution_done': total_subst_done,
            'bes_done': total_bes_done,
            'co_teaching_done': total_co_teaching_done,
            'missing_hours': hptic.hours - total_normal_done,
            'missing_bes': hptic.hours_bes - total_bes_done,
            'missing_co_teaching': hptic.hours_co_teaching - total_co_teaching_done
        })
    return teachers_report


def assign_html_style_to_visible_forms_fields(form):
    """
    Add the form-control class to the html of the form fields,
    so that they are well formatted by Bootstrap.
    :param form: a form instance
    """
    for visible in form.visible_fields():
        if 'class' not in visible.field.widget.attrs:
            visible.field.widget.attrs['class'] = 'form-control'


def generate_random_password():
    """
    Generate a random 15-chars string composed of ascii letters + digits + punctuation characters.
    """
    length = 15
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(length))


def get_available_teachers(assign: Assignment, school: School):
    """
    Return the list of all the available teachers to make a substitution for a given assignment
    """
    teachers_list = Teacher.objects.filter(school=school) \
        .exclude(id=assign.teacher.id) \
        .filter(hoursperteacherinclass__course__school_year=assign.school_year).distinct()

    # Remove all teachers who have an absence block there.
    hour_slot = HourSlot.objects.filter(school=assign.school,
                                        school_year=assign.school_year,
                                        starts_at=assign.hour_start,
                                        ends_at=assign.hour_end,
                                        day_of_week=assign.date.weekday()).first()
    if hour_slot:
        # If there is the hour_slot, then exclude all teachers that have an absence block in that period.
        # TODO: do some tests with absence blocks!!
        teachers_list = teachers_list.exclude(absenceblock__hour_slot=hour_slot)

        # Exclude from the choice the teachers that are already busy with other assignments.
        teachers_to_exclude = Assignment.objects.filter(school=assign.school,
                                                        school_year=assign.school_year,
                                                        hour_start=assign.hour_start,
                                                        hour_end=assign.hour_end,
                                                        date=assign.date).values_list('teacher__id')

        teachers_list = teachers_list.exclude(id__in=teachers_to_exclude)

    return teachers_list


def send_invitation_email(user_pk, request):
    class InvitationForm(PasswordResetForm):
        def __init__(self, user, *args, **kwargs):
            self.user = user
            super(InvitationForm, self).__init__(*args, **kwargs)

        def get_users(self, email):
            return (self.user, )

    user = User.objects.get(id=user_pk)
    form = InvitationForm(user, {'email': user.email})
    assert form.is_valid()
    form.save(
        request=request,
        use_https=request.is_secure(),
        email_template_name='email_templates/invite.html',
        subject_template_name='email_templates/invite_subject.txt'
    )
