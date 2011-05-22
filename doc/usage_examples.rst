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
        Average score: {{ score.average }}
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
        Average film score: {{ film_score.average }}
        Number of votes: {{ film_score.num_votes }}
    {% else %}
        How sad: nobody voted {{ film }}
    {% endif %}
    
    {% get_rating_score for film using 'trailer' as trailer_score %}
    {% if trailer_score %}
        Average trailer score: {{ trailer_score.average }}
        Number of votes: {{ trailer_score.num_votes }}
    {% else %}
        How sad: nobody voted {{ film }}'s trailer
    {% endif %}
    
That's all: of course you can assign more than 2 rating keys to each model.


Conditional ratings
~~~~~~~~~~~~~~~~~~~

We want users to star rate our film, using five stars with a step of half star.
This time we wants two different ratings: the first, we call it ``'expectation'``,
is used when the film is not yet released, while the second one, we call it
``real`` is used after the film release. Again, this is odd too, but at least 
this is something I actually had to implement.

So, the want the rating system to use two different rating keys based on release
status of the voted object::

    import datetime
    from ratings.handlers import ratings, RatingHandler
    
    class MyHandler(RatingHandler):
        score_range = (1, 5)
        score_step = 0.5
        
        def get_key(self, request, instance):
            today = datetime.date.today()
            return 'expectation' if instance.release_date < today else 'real'
            
The template looks like this (in the template we assume the film has an
``is_published`` self explanatory method):

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
    
    {% if film.is_published %}
        
        {% get_rating_score for film using 'real' as real_score %}
        {% if real_score %}
            Average score: {{ real_score.average }}
            Number of votes: {{ real_score.num_votes }}
        {% else %}
            How sad: nobody voted {{ film }}
        {% endif %}
        
    {% else %}
    
        {% get_rating_score for film using 'expectation' as expected_score %}
        {% if expected_score %}
            Average expectation: {{ expected_score.average }}
            Number of votes: {{ expected_score.num_votes }}
        {% else %}
            Good: nobody expected something!
        {% endif %}
    
    {% endif %}
            
Note that while the ``allow_key`` method (from previous example) is used to 
validate the key submitted by the form, the ``get_key`` one is used only 
if the key is not specified as a templatetag argument.

Actually, the default implementation of ``allow_key`` only checks if the 
given key equals to the key returned by ``get_key``.


Like/Dislike rating
~~~~~~~~~~~~~~~~~~~~

# TODO

Using AJAX
~~~~~~~~~~

# TODO

Working with querysets
~~~~~~~~~~~~~~~~~~~~~~

# TODO