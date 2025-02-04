from django import template

register = template.Library()

@register.filter
def status_color(status):
    """
    Maps agreement status to a corresponding Bootstrap badge color.
    """
    color_map = {
        'pending': 'secondary',  # Gray
        'active': 'success',     # Green
        'completed': 'primary',  # Blue
        'terminated': 'danger',  # Red
    }
    return color_map.get(status.lower(), 'secondary')  # Default to gray if status not found