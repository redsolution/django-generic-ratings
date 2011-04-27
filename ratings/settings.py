from django.conf import settings

# set to False to allow votes only by authenticated users
ALLOW_ANONYMOUS = getattr(settings, 'GENERIC_RATINGS_ALLOW_ANONYMOUS', False)
# must be a tuple of min and max values for scores (including the extremes)
SCORE_RANGE = getattr(settings, 'GENERIC_RATINGS_SCORE_RANGE', (1, 5))
# how many decimal places are allowed in scores
VOTE_DECIMALS = getattr(settings, 'GENERIC_RATINGS_VOTE_DECIMALS', 0)
# default key to use for votes when there is only one vote-pre-content
DEFAULT_KEY = getattr(settings, 'GENERIC_RATINGS_DEFAULT_KEY', 'main')
# querystring key that can contain the url of the redirection 
# performed after voting
NEXT_QUERYSTRING_KEY = getattr(settings, 
    'GENERIC_RATINGS_NEXT_QUERYSTRING_KEY', 'next')