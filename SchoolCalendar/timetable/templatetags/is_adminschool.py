from django import template
from timetable import utils

register = template.Library()


@register.filter(name='is_adminschool')
def is_adminschool(user):
    return utils.is_adminschool(user)


@register.filter(name='is_teacher')
def is_teacher(user):
    return utils.is_teacher(user)


@register.filter(name='is_secretary')
def is_secretary(user):
    return utils.is_secretary(user)
