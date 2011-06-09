Customization
=============

When you register an handler you can customize all the ratings options, as
seen in :doc:`handlers`.

But it is also possible to register an handler without overriding options 
or methods, and that handler will work using pre-defined global settings.

This section describes the settings used to globally customize ratings 
handlers, together with their default values.

----

``GENERIC_RATINGS_ALLOW_ANONYMOUS = False``

Set to False to allow votes only by authenticated users.

----

``GENERIC_RATINGS_SCORE_RANGE = (1, 5)``

A sequence of minimum and maximum values allowed in scores.

----

``GENERIC_RATINGS_SCORE_STEP = 1``

Step allowed in scores.

----

``GENERIC_RATINGS_WEIGHT = 0``

The weight used to calculate average score.

----

``GENERIC_RATINGS_DEFAULT_KEY = 'main'``

Default key to use for votes when there is only one vote-per-content.

----

``GENERIC_RATINGS_NEXT_QUERYSTRING_KEY = 'next'``

Querystring key that can contain the url of the redirection performed 
after voting.

----

``GENERIC_RATINGS_VOTES_PER_IP_ADDRESS = 0``

In case of anonymous users it is possible to limit votes per ip address 
(0 = no limits).

----

``GENERIC_RATINGS_COOKIE_NAME_PATTERN = 'grvote_%(model)s_%(object_id)s_%(key)s'``

The pattern used to create a cookie name.

----

``GENERIC_RATINGS_COOKIE_MAX_AGE = 60 * 60 * 24 * 365 # one year``

The cookie max age (number of seconds) for anonymous votes.
