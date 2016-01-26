#!/usr/bin/env python
import os
import sys

sys.path.append('..')
backup = os.environ.get('DJANGO_SETTINGS_MODULE', '')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

try:
    # Needed for django > 1.7
    import django
    django.setup()
except AttributeError:
    pass

try:
    from django.test.runner import DiscoverRunner
except Exception as e:
    from django.test.simple import DjangoTestSuiteRunner as DiscoverRunner

if __name__ == "__main__":
    failures = DiscoverRunner().run_tests(['ratings',], verbosity=1)
    if failures:
        sys.exit(failures)
    os.environ['DJANGO_SETTINGS_MODULE'] = backup
