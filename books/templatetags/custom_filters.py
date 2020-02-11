from django import template

register = template.Library()

@register.filter
def as_percentage_of(part, whole):
    try:
        return '{0:.2%}'.format( part / whole )

    except (ValueError, ZeroDivisionError):
        return ""