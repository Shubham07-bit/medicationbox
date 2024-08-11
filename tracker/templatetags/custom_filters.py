from django import template

register = template.Library()

@register.filter
def get_doses(patient_doses, device_id):
    return patient_doses.get(device_id, [])
