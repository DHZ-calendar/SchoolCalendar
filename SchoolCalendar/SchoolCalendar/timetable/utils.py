import datetime

from timetable.models import Teacher, AdminSchool


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
