from rating import settings

class ForbiddenError(Exception): pass


def get_cookie_name(instance, key):
    """
    Return a cookie name for anonymous vote of *instance* using *key*.
    """
    mapping = {
        'model': str(instance._meta),
        'content_type_id': str(content_type.pk),
        'key': key,
    }
    return settings.COOKIE_NAME_PATTERN % mapping
