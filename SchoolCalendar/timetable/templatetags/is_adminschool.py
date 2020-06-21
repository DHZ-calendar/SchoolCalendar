from django import template
from timetable import utils

register = template.Library()


@register.filter(name='is_adminschool')
def is_adminschool(user):
    return utils.is_adminschool(user)
