"""
Signals relating to ratings.
"""
from django.dispatch import Signal

# fired before a vote is saved
content_will_be_voted = Signal(providing_args=['vote', 'request'])
# fired after a vote is saved
content_was_voted = Signal(providing_args=['vote', 'request'])
