import datetime

try:
    from django.utils.crypto import salted_hmac, constant_time_compare
except ImportError:
    from ratings.utils import salted_hmac, constant_time_compare

from ratings import settings

def get_name(instance, key):
    """
    Return a cookie name for anonymous vote of *instance* using *key*.
    """
    mapping = {
        'model': str(instance._meta),
  #      'content_type_id': str(content_type.pk),
        'key': key,
        'object_id': instance.id,
    }
    return settings.COOKIE_NAME_PATTERN % mapping

def get_value(ip_address):
    """
    Return a cookie value for an anonymous vote.
    """
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    return salted_hmac("gr.cookie", "%s-%s" % (now, ip_address)).hexdigest()