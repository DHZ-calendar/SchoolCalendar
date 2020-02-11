from Timetable.models import Teacher, AdminSchool


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
