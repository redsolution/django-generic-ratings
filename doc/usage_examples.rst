Usage and examples
==================

As seen previously in :doc:`handlers`, we can customize the voting process
creating and registering rating handlers.

In this section we will deal with some real-world examples of usage of 
Django Generic Ratings.


Simple rating
~~~~~~~~~~~~~

We want votes in range 1-10 (including extremes) and we want to use
a slider widget to let the user vote.

The model ragistration is straightforward::

    from ratings.handlers import ratings
    from ratings.forms import SliderVoteForm
    ratings.register(Film, score_range=(1, 10), form_class=SliderVoteForm)
    
The template where we want users to vote requires very little code:

.. code-block:: html+django

    {# javascripts required by SliderVoteForm #}
    <script src="path/to/jquery.js" type="text/javascript"></script>
    <script src="path/to/jquery-ui.js" type="text/javascript"></script>

    {% load ratings_tags %}
    
    {% get_rating_form for film as rating_form %}
    <form action="{% url ratings_vote %}" method="post">
        {% csrf_token %}
        {{ rating_form }}
        <p><input type="submit" value="Vote &rarr;"></p>
    </form>
    
    {% get_rating_score for film as score %}
    {% if score %}
        Average score: {{ score.average|floatformat }}
        Number of votes: {{ score.num_votes }}
    {% else %}
        How sad: nobody voted {{ film }}
    {% endif %}

Done. See :doc:`forms_api` for a description of all available forms and widgets.
    
    
Multiple ratings
~~~~~~~~~~~~~~~~

We want users to vote (in range 1-10) both the film and the trailer of 
the film (I know: this is odd).

We have to customize the handler in order to make it deal with two different
rating keys (that we call ``'film'`` and ``'trailer'``)::

    from ratings.handlers import ratings, RatingHandler
    
    class MyHandler(RatingHandler):
        score_range = (1, 10)
        
        def allow_key(self, request, instance, key):
            return key in ('film', 'trailer')
           
    ratings.register(Film, MyHandler)
    
This way we are saying to the handler to allow those new keys.
    
The template is very similar to the one seen in simple rating, but we must
specify the rating key when using templatetags:

.. code-block:: html+django

    {% load ratings_tags %}
    
    Vote the film:
    {# note the 'using' argument below #}
    {% get_rating_form for film using 'film' as film_rating_form %} 
    <form action="{% url ratings_vote %}" method="post">
        {% csrf_token %}
        {{ film_rating_form }}
        <p><input type="submit" value="Vote Film &rarr;"></p>
    </form>
    
    Vote the trailer:
    {% get_rating_form for film using 'trailer' as trailer_rating_form %}
    <form action="{% url ratings_vote %}" method="post">
        {% csrf_token %}
        {{ trailer_rating_form }}
        <p><input type="submit" value="Vote Trailer &rarr;"></p>
    </form>
    
    {# note the 'using' argument below #}
    {% get_rating_score for film using 'film' as film_score %}
    {% if film_score %}
        Average film score: {{ film_score.average|floatformat }}
        Number of votes: {{ film_score.num_votes }}
    {% else %}
        How sad: nobody voted {{ film }}
    {% endif %}
    
    {% get_rating_score for film using 'trailer' as trailer_score %}
    {% if trailer_score %}
        Average trailer score: {{ trailer_score.average|floatformat }}
        Number of votes: {{ trailer_score.num_votes }}
    {% else %}
        How sad: nobody voted {{ film }}'s trailer
    {% endif %}
    
That's all: of course you can assign more than 2 rating keys to each model.


Conditional ratings
~~~~~~~~~~~~~~~~~~~

We want users to star rate our film, using five stars with a step of half star.
This time we want two different ratings: the first, we call it ``'expectation'``,
is used when the film is not yet released, while the second one, we call it
``real`` is used after the film release. Again, this is odd too, but at least 
this is something I actually had to implement.

So, we want the rating system to use two different rating keys based on the 
release status of the voted object::

    import datetime
    from ratings.handlers import ratings, RatingHandler
    
    class MyHandler(RatingHandler):
        score_range = (1, 5)
        score_step = 0.5
        
        def get_key(self, request, instance):
            today = datetime.date.today()
            return 'expectation' if instance.release_date < today else 'real'
            
The template looks like this (here we assume the film has an ``is_released`` 
self explanatory method):

.. code-block:: html+django

    {# javascripts and css required by StarVoteForm #}
    <script src="path/to/jquery.js" type="text/javascript"></script>
    <script src="path/to/jquery-ui.js" type="text/javascript"></script>
    <link href="/path/to/jquery.rating.css" rel="stylesheet" type="text/css" />
    <script type="text/javascript" src="/path/to/jquery.MetaData.js"></script>
    <script type="text/javascript" src="/path/to/jquery.rating.js"></script>

    {% load ratings_tags %}
    
    {# do not specify the key -> the key is obtained using our handler #}
    {% get_rating_form for film as rating_form %}
    <form action="{% url ratings_vote %}" method="post">
        {% csrf_token %}
        {{ rating_form }}
        <p><input type="submit" value="Vote &rarr;"></p>
    </form>
    
    {% if film.is_released %}
        
        {% get_rating_score for film using 'real' as real_score %}
        {% if real_score %}
            Average score: {{ real_score.average|floatformat }}
            Number of votes: {{ real_score.num_votes }}
        {% else %}
            How sad: nobody voted {{ film }}
        {% endif %}
        
    {% else %}
    
        {% get_rating_score for film using 'expectation' as expected_score %}
        {% if expected_score %}
            Average expectation: {{ expected_score.average|floatformat }}
            Number of votes: {{ expected_score.num_votes }}
        {% else %}
            Good: nobody expected something!
        {% endif %}
    
    {% endif %}
            
Note that while the ``allow_key`` method (from previous example) is used to 
validate the key submitted by the form, the ``get_key`` one is used only 
if the key is not specified as a templatetag argument.

Actually, the default implementation of ``allow_key`` only checks if the 
given key matches the key returned by ``get_key``.


Like/Dislike rating
~~~~~~~~~~~~~~~~~~~~

We want users to rate *+1* or *-1* our film. Actually this application does not
provide a widget for like/dislike rating, and it's up to you creating one.
But the business logic is straightforward::
    
    from somewhere import LikeForm
    from ratings.handlers import ratings
    
    ratings.register(Film, score_range=(-1, 1), form_class=LikeForm)
    
In the template we can show the current film rating using the total sum of
all votes, e.g.:

.. code-block:: html+django

    {% load ratings_tags %}
    
    {% get_rating_score for film as score %}
    {% if score %}
        Film score: {% if score.total > 0 %}+{% endif %}{{ score.total }}
        Number of votes: {{ score.num_votes }}
    {% else %}
        How sad: nobody voted {{ film }}
    {% endif %}


Working with querysets
~~~~~~~~~~~~~~~~~~~~~~

Consider the following code, printing all votes given by current user::

    from ratings.models import Vote
    for vote in Vote.objects.filter(user=request.user):
        print "%s -> %s" % (vote.content_object, vote.score)
        
There is nothing wrong in the above code snippet, except that it does,
for each vote, a query to retrieve the voted object.
You can avoid this using the ``filter_with_contents`` method of the *Vote*
and *Score* models, e.g.::

    from ratings.models import Vote
    for vote in Vote.objects.filter_with_contents(user=request.user):
        print "%s -> %s" % (vote.content_object, vote.score)

This way only a query for each different content type is performed.
We have shortcuts for votes retreival: for example the previous code
can be rewritten like this::

    from ratings.handlers import ratings
    for vote in ratings.get_votes_by(request.user):
        print "%s -> %s" % (vote.content_object, vote.score)

The application also provides handler's shortcuts to get votes associated 
to a particular content type::

    from ratings.handlers import ratings
    handler = ratings.get_handler(MyModel)
    
    # get all votes by user (regarding MyModel instances)
    user_votes = handler.get_votes_by(request.user)
    
    # get all votes given to myinstance
    instance_votes = handler.get_votes_for(myinstance)
    
What if instead you have a queryset and you want to print the *main* score of
each object in it?
Of course you can write something like this::

    from ratings.handlers import ratings
    
    queryset = Film.objects.all()
    handler = ratings.get_handler(queryset.model)
    key = 'main'
    
    for instance in queryset:
        score = handler.get_score(instance, key)
        print 'film:', instance
        print 'average score:', score.average
        print 'votes:', score.num_votes
        
Again, this is correct but you are doing a query for each object in the queryset.
The ratings handler lets you annotate the *queryset* with scores using a 
given *key*, e.g.::

    from ratings.handlers import ratings
    
    queryset = Film.objects.all()
    handler = ratings.get_handler(queryset.model)
    key = 'main'
    
    queryset_with_scores = handler.annotate_scores(queryset, key, 
        myaverage='average', num_votes='num_votes')
        
    for instance in queryset_with_scores:
        print 'film:', instance
        print 'average score:', instance.myaverage
        print 'votes:', instance.num_votes
        
As seen, each film in queryset has two new attached fields: 
*myaverage* and *num_votes*.
The same kind of annotation can be done with user's votes, see 
:doc:`handlers_api`.


Using AJAX
~~~~~~~~~~

This application comes with out-of-the-box *AJAX* voting support.

All is needed is the inclusion of the provided ``ratings.js`` javascript
in the template where the vote form is displayed. The javascript file is
present in the ``static/ratings/js/`` directory of the distribution.

The script will handle the AJAX vote submit for all forms having *ratings*
class.

Here is a working example of an *AJAX* voting form that uses the slider widget:

.. code-block:: html+django

    {# javascripts and css required by SliderVoteForm #}
    <script src="path/to/jquery.js" type="text/javascript"></script>
    <script src="path/to/jquery-ui.js" type="text/javascript"></script>
    script type="text/javascript" src="/path/to/ratings.js"></script>

    {% load ratings_tags %}
    
    {% get_rating_form for object as rating_form %}
    
    <form action="{% url ratings_vote %}" class="ratings" method="post">
        {% csrf_token %}
        {{ rating_form }}
        <p>
            {# only authenticated users can vote #}
            {% if user.is_authenticated %}
                <input type="submit" value="Vote"></p>
            {% else %}
                <a href="{% url login %}?next={{ request.path }}">Vote</a>
            {% endif %}
        </p>
        <span class="success" style="display: none;">Vote registered!</span>
        <span class="error" style="display: none;">Errors...</span>
    </form>
    
By default, if you did not customize the handler, the *AJAX* request 
(on form submit) returns a *JSON* response containing::

    {
        'key': 'the_rating_key',
        'vote_id': vote.id,
        'vote_score': vote.score,
        'score_average': score.average,
        'score_num_votes': score.num_votes,
        'score_total': score.total,
    }

In the previous example, we put two hidden elements inside the form, 
the former having class *success* and the latter having class *error*.
Each one, if present, is showed whenever an AJAX vote is successfully 
completed or not.

Further more, various javascript events are triggered during *AJAX* votes:
see :doc:`forms_api` for details.
    

Performance and database denormalization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One goal of *Django Generic Ratings* is to provide a generic solution to rate
model instances without the need to edit your (or third party) models.

Sometimes, however, you may want to denormalize ratings data, for example
because you need to speed up *order by* queries for tables with a lot of 
records, or for backward compatibility with legacy code.

Assume you want to store the average score and the number of votes in your
film instances, and you want these values to change each time a user votes 
a film.

This is easily achievable, again, customizing the handler, e.g.::

    from ratings.handlers import RatingHandler, ratings

    class FilmRatingHandler(RatingHandler):
        
        def post_vote(self, request, vote, created):
            instance = vote.content_object
            score = vote.get_score() 
            instance.average_vote = score.average
            instance.num_votes = score.num_votes
            instance.save()
        
    ratings.register(Film, FilmRatingHandler)


Deleting model instances
~~~~~~~~~~~~~~~~~~~~~~~~

When you delete a model instance all related votes and scores are
contextually deleted too.
