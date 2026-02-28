from django import template

register = template.Library()

@register.filter
def has_profile_photo(user):
    """Check if user has a profile photo"""
    try:
        return user.profile and user.profile.profile_photo
    except:
        return False

@register.filter
def get_profile_photo_url(user):
    """Get user's profile photo URL"""
    try:
        if user.profile and user.profile.profile_photo:
            return user.profile.profile_photo.url
    except:
        pass
    return None
