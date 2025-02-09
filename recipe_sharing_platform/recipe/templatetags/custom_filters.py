from django import template

register = template.Library()

@register.filter
def calculate_percentage(value, max_value):
    try:
        return int((value / max_value) * 100)
    except (ValueError, ZeroDivisionError):
        return 0 