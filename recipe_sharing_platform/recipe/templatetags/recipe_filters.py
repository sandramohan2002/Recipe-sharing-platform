from django import template
import re

register = template.Library()

@register.filter
def split(value, arg):
    """
    Splits the value by argument
    """
    return value.split(arg) if value else []

@register.filter
def strip(value):
    """
    Strips whitespace from value
    """
    return value.strip() if value else '' 