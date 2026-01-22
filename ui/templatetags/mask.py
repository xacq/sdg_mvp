from django import template

register = template.Library()

@register.filter
def mask(value):
    if not value:
        return value
    value = str(value)
    if len(value) < 4:
        return value
    return value[:2] + "*" * (len(value) - 4) + value[-2:]
