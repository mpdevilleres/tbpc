from django import template

register = template.Library()

@register.filter('fieldtype')
def field_type(field):
    return field.field.__class__.__name__

@register.filter('hr')
def field_type(element):
    if element=='hr':
        return True
    return False

@register.filter('blank')
def field_type(element):
    if element=='blank':
        return True
    return False

@register.filter('return_item')
def return_item(l, i):
    try:
        return l[i]
    except:
        return None

@register.filter('getattr')
def get_attr(obj, val):
    return getattr(obj, val)

@register.filter('return_list')
def return_list(l, i):
    try:
        return l[i]
    except:
        return None

@register.filter('is_signed_in')
def is_signed_in(user):
    attendance = user.attendance_set.order_by('-pk').first()
    return attendance.is_signed_in()