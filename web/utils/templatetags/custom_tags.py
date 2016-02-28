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

@register.filter('return_list')
def return_list(l, i):
    try:
        return l[i]
    except:
        return None